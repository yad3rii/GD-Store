from rest_framework import serializers

from apps.accounts.serializers import UserPublicSerializer

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = UserPublicSerializer(read_only=True)

    class Meta:
        model = Review
        fields = [
            "id",
            "game",
            "user",
            "is_recommended",
            "text",
            "playtime_at_review",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "user",
            "playtime_at_review",
            "created_at",
        ]

    def validate(self, attrs):
        if (
            self.instance is not None
            and "game" in attrs
            and attrs["game"] != self.instance.game
        ):
            raise serializers.ValidationError(
                {
                    "game": (
                        "Нельзя изменить игру "
                        "у существующего отзыва."
                    )
                }
            )

        return attrs