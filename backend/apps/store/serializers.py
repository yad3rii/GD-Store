from rest_framework import serializers

from apps.catalog.models import Game
from apps.catalog.serializers import GameListSerializer
from apps.library.models import LibraryEntry

from .models import CartItem, Order, OrderItem, Wishlist


class CartItemSerializer(serializers.ModelSerializer):
    """Только для чтения — отдаёт полную карточку игры."""
    game = GameListSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "game", "added_at"]


class CartItemCreateSerializer(serializers.ModelSerializer):
    """Для POST /cart/ — принимает только id игры, сам owner проставляется во view."""

    class Meta:
        model = CartItem
        fields = ["id", "game"]

    def validate_game(self, game):
        if not game.is_published:
            raise serializers.ValidationError("Игра недоступна для покупки.")
        user = self.context["request"].user
        if LibraryEntry.objects.filter(user=user, game=game).exists():
            raise serializers.ValidationError("Игра уже в вашей библиотеке.")
        return game

    def create(self, validated_data):
        user = self.context["request"].user
        cart_item, _ = CartItem.objects.get_or_create(user=user, game=validated_data["game"])
        return cart_item

    def to_representation(self, instance):
        return CartItemSerializer(instance, context=self.context).data


class WishlistSerializer(serializers.ModelSerializer):
    game = GameListSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ["id", "game", "added_at"]


class WishlistCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = ["id", "game"]

    def create(self, validated_data):
        user = self.context["request"].user
        item, _ = Wishlist.objects.get_or_create(user=user, game=validated_data["game"])
        return item

    def to_representation(self, instance):
        return WishlistSerializer(instance, context=self.context).data


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
        read_only_fields = fields
