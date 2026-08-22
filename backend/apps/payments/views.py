from django.db import transaction
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.store.models import Order
from apps.library.models import LibraryEntry
from .models import Payment
from .serializers import PaymentSerializer


class CreatePaymentView(generics.CreateAPIView):
    """
    POST /api/v1/payments/create/ {order_id}
    Создаёт платёж и (в реальной интеграции) возвращает ссылку/client_secret платёжного провайдера.
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        order = Order.objects.get(id=request.data["order_id"], user=request.user)
        payment = Payment.objects.create(order=order, amount=order.total, status="created")
        # TODO: интеграция со Stripe/LiqPay — вернуть client_secret / checkout_url
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)


class PaymentWebhookView(APIView):
    """
    POST /api/v1/payments/webhook/
    Сюда стучится платёжный провайдер. При успехе — помечаем Order оплаченным
    и раскладываем игры по библиотеке пользователя.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # TODO: проверить подпись webhook'а провайдера
        provider_payment_id = request.data.get("provider_payment_id")
        is_success = request.data.get("status") == "succeeded"

        payment = Payment.objects.select_related("order").get(provider_payment_id=provider_payment_id)

        with transaction.atomic():
            payment.status = "succeeded" if is_success else "failed"
            payment.save()

            if is_success:
                order = payment.order
                order.status = "paid"
                order.save()
                LibraryEntry.objects.bulk_create([
                    LibraryEntry(user=order.user, game=item.game)
                    for item in order.items.all()
                ], ignore_conflicts=True)

        return Response(status=status.HTTP_200_OK)
