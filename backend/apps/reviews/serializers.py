from rest_framework import serializers
from apps.accounts.serializers import UserPublicSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ["id", "game", "user", "is_recommended", "text", "playtime_at_review", "created_at"]
        read_only_fields = ["user", "playtime_at_review"]
