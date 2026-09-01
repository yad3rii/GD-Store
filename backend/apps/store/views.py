from django.db import IntegrityError, transaction
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.library.models import LibraryEntry

from .models import CartItem, Order, OrderItem, Wishlist
from .serializers import (
    CartItemCreateSerializer,
    CartItemSerializer,
    OrderSerializer,
    WishlistCreateSerializer,
    WishlistSerializer,
)


class CartViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/store/cart/            — список товаров в корзине
    POST   /api/v1/store/cart/  {game}    — добавить игру
    DELETE /api/v1/store/cart/<id>/       — убрать из корзины
    POST   /api/v1/store/cart/checkout/   — оформить заказ
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user).select_related("game")

    def get_serializer_class(self):
        if self.action == "create":
            return CartItemCreateSerializer
        return CartItemSerializer

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
        Игры, которые пользователь уже успел купить где-то ещё, из корзины тихо убираются
        и в оформление заказа не попадают.
        """
        owned_game_ids = set(
            LibraryEntry.objects.filter(user=request.user).values_list("game_id", flat=True)
        )
        items = list(self.get_queryset())
        already_owned = [i for i in items if i.game_id in owned_game_ids]
        purchasable = [i for i in items if i.game_id not in owned_game_ids]

        if already_owned:
            CartItem.objects.filter(id__in=[i.id for i in already_owned]).delete()

        if not purchasable:
            return Response(
                {"detail": "Корзина пуста (или все игры уже куплены)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            total = sum((i.game.final_price for i in purchasable), start=0)
            order = Order.objects.create(user=request.user, total=total, status=Order.STATUS_PENDING)
            OrderItem.objects.bulk_create([
                OrderItem(order=order, game=i.game, price_at_purchase=i.game.final_price)
                for i in purchasable
            ])
            CartItem.objects.filter(id__in=[i.id for i in purchasable]).delete()

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
    """GET /api/v1/store/orders/ — история покупок пользователя"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__game")
