import hashlib
import hmac
import logging
import uuid

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.library.models import LibraryEntry
from apps.store.models import Order

from .models import Payment
from .serializers import (
    CreatePaymentSerializer,
    PaymentSerializer,
    PaymentWebhookSerializer,
)
from .throttles import PaymentCreateThrottle


logger = logging.getLogger(__name__)


class CreatePaymentView(CreateAPIView):
    serializer_class = CreatePaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [PaymentCreateThrottle]

    def create(self, request, *args, **kwargs):
        del args, kwargs

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_id = serializer.validated_data["order_id"]

        with transaction.atomic():
            order = get_object_or_404(
                Order.objects.select_for_update(),
                id=order_id,
                user=request.user,
            )

            if (
                order.expires_at is not None
                and timezone.now() >= order.expires_at
                and order.status == Order.STATUS_PENDING
            ):
                order.status = Order.STATUS_EXPIRED
                order.save(update_fields=["status"])

                return Response(
                    {"detail": "Срок оплаты заказа истёк."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if order.status != Order.STATUS_PENDING:
                return Response(
                    {
                        "detail": (
                            "Оплатить можно только заказ "
                            "в статусе pending."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payment, created = Payment.objects.get_or_create(
                order=order,
                defaults={
                    "amount": order.total,
                },
            )

            if not created:
                payment = Payment.objects.select_for_update().get(
                    pk=payment.pk
                )

            if payment.status == Payment.STATUS_SUCCEEDED:
                return Response(
                    {"detail": "Заказ уже оплачен."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if payment.status == Payment.STATUS_REFUNDED:
                return Response(
                    {
                        "detail": (
                            "Платёж по этому заказу "
                            "уже был возвращён."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Повторный запрос должен вернуть действующую попытку без изменений.
            # Пустой ID возможен у старых записей, созданных вне этого endpoint.
            if (
                created
                or payment.status == Payment.STATUS_FAILED
                or not payment.provider_payment_id
            ):
                payment.status = Payment.STATUS_CREATED
                payment.amount = order.total
                payment.provider_payment_id = uuid.uuid4().hex
                payment.raw_payload = {}
                payment.save()

        logger.info(
            "Payment %s checkout returned for order %s to user %s",
            payment.id,
            order.id,
            request.user.id,
        )

        data = PaymentSerializer(payment).data

        # Заглушка до подключения настоящего Stripe/LiqPay.
        data["checkout_url"] = (
            f"https://pay.example.com/"
            f"{payment.provider}/"
            f"{payment.provider_payment_id}"
        )

        return Response(
            data,
            status=status.HTTP_201_CREATED,
        )


class PaymentWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def _check_signature(self, request):
        secret = getattr(settings, "PAYMENT_WEBHOOK_SECRET", "")

        if not secret or not secret.strip():
            logger.error("Payment webhook rejected: secret is not configured")
            raise PermissionDenied("Приём уведомлений об оплате отключён.")

        signature = request.headers.get("X-Signature", "")

        if (
            len(signature) != 64
            or any(char not in "0123456789abcdefABCDEF" for char in signature)
        ):
            raise PermissionDenied("Отсутствует или неверна подпись webhook'а.")

        expected = hmac.new(
            secret.encode("utf-8"),
            request.body,
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature.lower(), expected):
            logger.warning("Payment webhook rejected: bad signature")
            raise PermissionDenied("Неверная подпись webhook'а.")

    def post(self, request):
        self._check_signature(request)

        serializer = PaymentWebhookSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        provider_payment_id = (
            serializer.validated_data[
                "provider_payment_id"
            ]
        )

        webhook_status = serializer.validated_data[
            "status"
        ]

        # Поиск связи без блокировки. Все денежные операции берут locks
        # в одном порядке: Order -> Payment (как create и refund).
        payment_ref = get_object_or_404(
            Payment.objects.only("id", "order_id"),
            provider_payment_id=provider_payment_id,
        )

        with transaction.atomic():
            order = get_object_or_404(
                Order.objects.select_for_update(),
                pk=payment_ref.order_id,
            )
            # За время ожидания lock могла начаться другая попытка.
            # Перепроверяем ID и связь, а не используем устаревший объект.
            payment = get_object_or_404(
                Payment.objects.select_for_update(),
                pk=payment_ref.pk,
                order_id=order.pk,
                provider_payment_id=provider_payment_id,
            )

            # Задержавшееся failed/succeeded не отменяет успех или возврат.
            if payment.status in (
                Payment.STATUS_SUCCEEDED,
                Payment.STATUS_REFUNDED,
            ):
                return Response(
                    status=status.HTTP_200_OK
                )

            payment.raw_payload = request.data

            if webhook_status == "failed":
                payment.status = Payment.STATUS_FAILED
                payment.save()

                # Не переводим заказ в failed:
                # пользователь может повторить попытку оплаты.
                if (
                    order.status == Order.STATUS_PENDING
                    and order.expires_at is not None
                    and timezone.now() >= order.expires_at
                ):
                    order.status = Order.STATUS_EXPIRED
                    order.save(
                        update_fields=["status"]
                    )

                logger.warning(
                    "Payment %s failed for order %s",
                    payment.id,
                    order.id,
                )

                return Response(
                    status=status.HTTP_200_OK
                )

            # Пришёл succeeded, но заказ уже нельзя оплачивать.
            if order.status != Order.STATUS_PENDING:
                payment.status = Payment.STATUS_FAILED
                payment.save()

                logger.warning(
                    "Successful webhook ignored for "
                    "order %s in status %s",
                    order.id,
                    order.status,
                )

                return Response(
                    status=status.HTTP_200_OK
                )

            # Не принимаем успешную оплату после истечения заказа.
            if (
                order.expires_at is not None
                and timezone.now() >= order.expires_at
            ):
                order.status = Order.STATUS_EXPIRED
                order.save(
                    update_fields=["status"]
                )

                payment.status = Payment.STATUS_FAILED
                payment.save()

                logger.warning(
                    "Successful webhook ignored for "
                    "expired order %s",
                    order.id,
                )

                return Response(
                    status=status.HTTP_200_OK
                )

            payment.status = Payment.STATUS_SUCCEEDED
            payment.save()

            order.status = Order.STATUS_PAID
            order.save(
                update_fields=["status"]
            )

            beneficiary = order.beneficiary

            for item in order.items.all():
                LibraryEntry.objects.get_or_create(
                    user=beneficiary,
                    game_id=item.game_id,
                )

        logger.info(
            "Payment %s succeeded, "
            "order %s granted to user %s",
            payment.id,
            order.id,
            beneficiary.id,
        )

        return Response(
            status=status.HTTP_200_OK
        )
