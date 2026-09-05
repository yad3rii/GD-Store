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
    from_user = UserPublicSerializer(read_only=True)
    to_user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source="to_user", write_only=True
    )
    to_user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = ["id", "from_user", "to_user", "to_user_id", "status", "created_at"]
        read_only_fields = ["id", "from_user", "to_user", "status", "created_at"]

    def validate(self, attrs):
        request = self.context.get("request")
        from_user = request.user
        to_user = attrs.get("to_user")

        if from_user == to_user:
            raise serializers.ValidationError("Нельзя отправить заявку в друзья самому себе.")

        if Friendship.objects.filter(from_user=from_user, to_user=to_user).exists() or \
           Friendship.objects.filter(from_user=to_user, to_user=from_user).exists():
            raise serializers.ValidationError("Заявка между этими пользователями уже существует.")

        return attrs
