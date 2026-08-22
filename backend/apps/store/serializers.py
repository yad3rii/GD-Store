from rest_framework import serializers
from apps.catalog.serializers import GameListSerializer
from .models import CartItem, Wishlist, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    game = GameListSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "game", "added_at"]


class WishlistSerializer(serializers.ModelSerializer):
    game = GameListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "game", "added_at"]


class OrderItemSerializer(serializers.ModelSerializer):
    game = GameListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["game", "price_at_purchase"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ["id", "status", "total", "created_at", "items"]
