import hashlib
import hmac
import uuid

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.library.models import LibraryEntry
from apps.store.models import Order

from .models import Payment
from .serializers import CreatePaymentSerializer, PaymentSerializer, PaymentWebhookSerializer


class CreatePaymentView(CreateAPIView):
    """
    POST /api/v1/payments/create/ {order_id}
    Создаёт (или переиспользует) платёж для заказа и возвращает данные для оплаты.

    В реальной интеграции здесь будет вызов Stripe/LiqPay API, а provider_payment_id
    и checkout_url будут приходить от провайдера. Сейчас это стаб: провайдер подставляется
    условно, а завершение платежа приходит через PaymentWebhookView.
    """
    serializer_class = CreatePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order = get_object_or_404(Order, id=serializer.validated_data["order_id"], user=request.user)

        if order.status != Order.STATUS_PENDING:
            return Response(
                {"detail": "Этот заказ уже обработан."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={"amount": order.total},
        )
        if not created and payment.status == Payment.STATUS_SUCCEEDED:
            return Response({"detail": "Заказ уже оплачен."}, status=status.HTTP_400_BAD_REQUEST)

        # Заново готовим платёж к оплате (если раньше он был failed/created — перевыпускаем id).
        payment.status = Payment.STATUS_CREATED
        payment.amount = order.total
        payment.provider_payment_id = uuid.uuid4().hex  # TODO: заменить на id из ответа провайдера
        payment.save()

        data = PaymentSerializer(payment).data
        # TODO: интеграция со Stripe/LiqPay — вернуть настоящий client_secret / checkout_url
        data["checkout_url"] = f"https://pay.example.com/{payment.provider}/{payment.provider_payment_id}"
        return Response(data, status=status.HTTP_201_CREATED)


class PaymentWebhookView(APIView):
    """
    POST /api/v1/payments/webhook/
    Сюда стучится платёжный провайдер. При успехе — помечаем Order оплаченным
    и раскладываем игры по библиотеке пользователя.

    Подпись запроса проверяется по HMAC-SHA256 из заголовка X-Signature
    (тело запроса + settings.PAYMENT_WEBHOOK_SECRET). Если секрет не задан в settings —
    проверка пропускается (удобно для локальной разработки, но не для продакшена).
    """
    permission_classes = [permissions.AllowAny]

    def _check_signature(self, request):
        secret = getattr(settings, "PAYMENT_WEBHOOK_SECRET", "")
        if not secret:
            return  # локальная разработка без настроенного провайдера
        signature = request.headers.get("X-Signature", "")
        expected = hmac.new(secret.encode(), request.body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected):
            raise PermissionDenied("Неверная подпись webhook'а.")

    def post(self, request):
        self._check_signature(request)

        serializer = PaymentWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider_payment_id = serializer.validated_data["provider_payment_id"]
        is_success = serializer.validated_data["status"] == "succeeded"

        payment = get_object_or_404(
            Payment.objects.select_related("order"),
            provider_payment_id=provider_payment_id,
        )

        with transaction.atomic():
            # select_for_update + повторная проверка статуса — от повторных/параллельных вебхуков.
            payment = Payment.objects.select_for_update().get(pk=payment.pk)
            if payment.status == Payment.STATUS_SUCCEEDED:
                return Response(status=status.HTTP_200_OK)  # уже обработан — идемпотентно ок

            payment.raw_payload = request.data
            payment.status = Payment.STATUS_SUCCEEDED if is_success else Payment.STATUS_FAILED
            payment.save()

            if is_success:
                order = payment.order
                order.status = Order.STATUS_PAID
                order.save(update_fields=["status"])
                LibraryEntry.objects.bulk_create(
                    [LibraryEntry(user=order.user, game=item.game) for item in order.items.all()],
                    ignore_conflicts=True,
                )
            else:
                payment.order.status = Order.STATUS_FAILED
                payment.order.save(update_fields=["status"])

        return Response(status=status.HTTP_200_OK)
