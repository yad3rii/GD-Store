from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Friendship

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "display_name", "avatar", "created_at"]


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "display_name", "avatar",
                  "country_code", "wallet_balance", "is_email_verified"]
        read_only_fields = ["email", "wallet_balance", "is_email_verified"]


class FriendshipSerializer(serializers.ModelSerializer):
    """Отдаём заявку в друзья с развёрнутыми публичными профилями обеих сторон."""
    from_user = UserPublicSerializer(read_only=True)
    to_user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ["id", "from_user", "to_user", "status", "created_at"]
        read_only_fields = ["status", "created_at"]


class FriendRequestCreateSerializer(serializers.ModelSerializer):
    """Отправка новой заявки в друзья: указываем только id получателя."""

    class Meta:
        model = Friendship
        fields = ["id", "to_user"]

    def validate_to_user(self, to_user):
        request_user = self.context["request"].user
        if to_user == request_user:
            raise serializers.ValidationError("Нельзя отправить заявку в друзья самому себе.")
        return to_user

    def validate(self, attrs):
        request_user = self.context["request"].user
        to_user = attrs["to_user"]
        if Friendship.objects.filter(from_user=request_user, to_user=to_user).exists():
            raise serializers.ValidationError("Заявка уже отправлена.")
        # Если обратная заявка уже существует — это не ошибка, реальная логика
        # "принять в ответ" реализована как action accept во FriendshipViewSet.
        return attrs
