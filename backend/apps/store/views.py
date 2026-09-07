import logging

from django.db import IntegrityError, transaction
from django.db.models import Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.library.models import LibraryEntry

from .models import CartItem, Order, OrderItem, Wishlist
from .serializers import (
    CartItemCreateSerializer,
    CartItemSerializer,
    CheckoutSerializer,
    OrderSerializer,
    WishlistCreateSerializer,
    WishlistSerializer,
)
from .throttles import CheckoutThrottle, OrderActionThrottle

logger = logging.getLogger(__name__)


class CartViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/store/cart/            — список товаров в корзине
    POST   /api/v1/store/cart/  {game}    — добавить игру
    DELETE /api/v1/store/cart/<id>/       — убрать из корзины
    POST   /api/v1/store/cart/checkout/   — оформить заказ (опционально: promo_code, recipient_username)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related("game")

    def get_serializer_class(self):
        if self.action == "create":
            return CartItemCreateSerializer
        return CartItemSerializer

    def get_throttles(self):
        if self.action == "checkout":
            return [CheckoutThrottle()]
        return super().get_throttles()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = serializer.save()
        except IntegrityError:
            return Response({"detail": "Игра уже в корзине."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.to_representation(instance), status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """
        Создаёт Order из корзины. Реальная оплата — через apps.payments (webhook подтверждает).

        Body (всё опционально):
          {"promo_code": "SUMMER25", "recipient_username": "friend"}

        Игры, которые получатель покупки уже успел приобрести где-то ещё, из корзины
        тихо убираются и в заказ не попадают.
        """
        checkout_data = CheckoutSerializer(data=request.data, context={"request": request})
        checkout_data.is_valid(raise_exception=True)
        promo = checkout_data.validated_data.get("promo_code") or None
        recipient = checkout_data.validated_data.get("recipient_username") or None
        beneficiary = recipient or request.user

        owned_game_ids = set(
            LibraryEntry.objects.filter(user=beneficiary).values_list("game_id", flat=True)
        )
        items = list(self.get_queryset())
        already_owned = [i for i in items if i.game_id in owned_game_ids]
        purchasable = [i for i in items if i.game_id not in owned_game_ids]

        if already_owned:
            CartItem.objects.filter(id__in=[i.id for i in already_owned]).delete()

        if not purchasable:
            return Response(
                {"detail": "Корзина пуста (или все игры уже есть у получателя)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            subtotal = sum((i.game.final_price for i in purchasable), start=0)
            discount_total = 0
            if promo:
                discount_total = round(subtotal * promo.discount_percent / 100, 2)
                promo.times_used += 1
                promo.save(update_fields=["times_used"])

            order = Order.objects.create(
                user=request.user,
                recipient=recipient,
                promo_code=promo,
                subtotal=subtotal,
                discount_total=discount_total,
                total=subtotal - discount_total,
                status=Order.STATUS_PENDING,
            )
            OrderItem.objects.bulk_create([
                OrderItem(order=order, game=i.game, price_at_purchase=i.game.final_price)
                for i in purchasable
            ])
            CartItem.objects.filter(id__in=[i.id for i in purchasable]).delete()

        logger.info(
            "Order %s created by user %s (total=%s, gift=%s, promo=%s)",
            order.id, request.user.id, order.total, order.is_gift, promo.code if promo else None,
        )
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class WishlistViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related("game")

    def get_serializer_class(self):
        if self.action == "create":
            return WishlistCreateSerializer
        return WishlistSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            instance = serializer.save()
        except IntegrityError:
            return Response({"detail": "Игра уже в вишлисте."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.to_representation(instance), status=status.HTTP_201_CREATED)


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET  /api/v1/store/orders/               — история покупок пользователя
    POST /api/v1/store/orders/<id>/cancel/   — отменить свой ещё не оплаченный заказ
    POST /api/v1/store/orders/<id>/refund/   — запросить возврат за оплаченный заказ
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__game")

    def get_throttles(self):
        if self.action in ("cancel", "refund"):
            return [OrderActionThrottle()]
        return super().get_throttles()

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status != Order.STATUS_PENDING:
            return Response(
                {"detail": "Отменить можно только заказ в статусе pending."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = Order.STATUS_CANCELLED
        order.save(update_fields=["status"])
        logger.info("Order %s cancelled by user %s", order.id, request.user.id)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=["post"])
    def refund(self, request, pk=None):
        # Локальный импорт — apps.payments уже импортирует apps.store.models на уровне модуля,
        # так что импорт apps.payments здесь делаем только внутри функции, чтобы не словить
        # циклический импорт при старте Django.
        from apps.payments.models import Payment

        order = self.get_object()
        if order.status != Order.STATUS_PAID:
            return Response(
                {"detail": "Возврат возможен только для оплаченного заказа."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            order = Order.objects.select_for_update().get(pk=order.pk)
            if order.status != Order.STATUS_PAID:
                return Response(
                    {"detail": "Возврат возможен только для оплаченного заказа."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            beneficiary = order.beneficiary
            for item in order.items.select_related("game"):
                # Не отбираем игру, если она есть у получателя ещё по какому-то другому оплаченному заказу
                # (например, купил сам, а потом ему ещё и подарили ту же игру).
                still_owned_elsewhere = (
                    Order.objects.filter(status=Order.STATUS_PAID, items__game=item.game)
                    .filter(Q(user=beneficiary) | Q(recipient=beneficiary))
                    .exclude(pk=order.pk)
                    .exists()
                )
                if not still_owned_elsewhere:
                    LibraryEntry.objects.filter(user=beneficiary, game=item.game).delete()

            order.status = Order.STATUS_REFUNDED
            order.save(update_fields=["status"])

            Payment.objects.filter(order=order).update(status=Payment.STATUS_REFUNDED)

        logger.info("Order %s refunded (requested by user %s)", order.id, request.user.id)
        return Response(OrderSerializer(order).data)
