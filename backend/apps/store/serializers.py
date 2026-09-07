from rest_framework import serializers

from apps.catalog.serializers import GameListSerializer
from apps.library.models import LibraryEntry

from .models import CartItem, Order, OrderItem, PromoCode, Wishlist


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


class CheckoutSerializer(serializers.Serializer):
    """Вход для POST /cart/checkout/."""
    promo_code = serializers.CharField(required=False, allow_blank=True, max_length=32)
    # Подарок другу: username получателя. Если не указан — покупка себе.
    recipient_username = serializers.CharField(required=False, allow_blank=True, max_length=150)

    def validate_promo_code(self, value):
        if not value:
            return value
        try:
            promo = PromoCode.objects.get(code__iexact=value)
        except PromoCode.DoesNotExist:
            raise serializers.ValidationError("Промокод не найден.")
        if not promo.is_valid():
            raise serializers.ValidationError("Промокод недействителен или истёк.")
        return promo

    def validate_recipient_username(self, value):
        if not value:
            return value
        User = self.context["request"].user.__class__
        buyer = self.context["request"].user
        try:
            recipient = User.objects.get(username=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь-получатель не найден.")
        if recipient == buyer:
            raise serializers.ValidationError("Нельзя подарить самому себе — оформите обычную покупку.")
        return recipient


class OrderItemSerializer(serializers.ModelSerializer):
    game = GameListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["game", "price_at_purchase"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    promo_code = serializers.SlugRelatedField(slug_field="code", read_only=True)
    recipient = serializers.SlugRelatedField(slug_field="username", read_only=True)
    is_gift = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            "id", "status", "subtotal", "discount_total", "total",
            "promo_code", "recipient", "is_gift",
            "created_at", "expires_at", "items",
        ]
        read_only_fields = fields
