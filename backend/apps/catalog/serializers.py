from rest_framework import serializers
from .models import (
    Developer,
    Game,
    Genre,
    Publisher,
    Screenshot,
    SystemRequirement,
    Tag,
)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug"]


class DeveloperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Developer
        fields = ["id", "name", "slug", "website"]


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = ["id", "name", "slug", "website"]


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = ["id", "image", "caption"]


class SystemRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemRequirement
        fields = [
            "os",
            "processor",
            "memory",
            "graphics",
            "storage",
            "additional_notes",
        ]


class GameListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Game
        fields = [
            "id",
            "title",
            "slug",
            "cover_image",
            "price",
            "discount_percent",
            "current_price",
            "genres",
            "tags",
            "release_date",
        ]


class GameDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    developers = DeveloperSerializer(many=True, read_only=True)
    publishers = PublisherSerializer(many=True, read_only=True)
    screenshots = ScreenshotSerializer(many=True, read_only=True)
    requirements = SystemRequirementSerializer(read_only=True)
    current_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )

    class Meta:
        model = Game
        fields = [
            "id",
            "title",
            "slug",
            "description",
            "short_description",
            "cover_image",
            "price",
            "discount_percent",
            "current_price",
            "genres",
            "tags",
            "developers",
            "publishers",
            "screenshots",
            "requirements",
            "release_date",
            "created_at",
        ]