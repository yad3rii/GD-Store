from decimal import Decimal
from django.db import transaction
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.catalog.models import Game
from apps.library.models import LibraryEntry
from .models import CartItem, Wishlist, Order, OrderItem
from .serializers import CartItemSerializer, WishlistSerializer, OrderSerializer


class CartViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/store/cart/            — список товаров в корзине
    POST   /api/v1/store/cart/  {game}    — добавить игру
    DELETE /api/v1/store/cart/<id>/       — убрать из корзины
    """
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, game_id=self.request.data.get("game"))

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """
        POST /api/v1/store/cart/checkout/
        Создаёт Order из корзины. Реальная оплата — через apps.payments (webhook подтверждает).
        """
        items = self.get_queryset().select_related("game")
        if not items:
            return Response({"detail": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            total = sum(i.game.final_price for i in items)
            order = Order.objects.create(user=request.user, total=total, status="pending")
            OrderItem.objects.bulk_create([
                OrderItem(order=order, game=i.game, price_at_purchase=i.game.final_price)
                for i in items
            ])
            items.delete()

        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, game_id=self.request.data.get("game"))


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """GET /api/v1/store/orders/ — история покупок пользователя"""
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")
