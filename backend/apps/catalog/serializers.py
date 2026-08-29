from rest_framework import serializers
from .models import Game, Genre, Tag, Screenshot, SystemRequirement


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "slug"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class ScreenshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screenshot
        fields = ["id", "image", "order"]


class SystemRequirementSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemRequirement
        fields = ["os", "cpu", "ram", "gpu", "storage"]


class GameListSerializer(serializers.ModelSerializer):
    """Короткая карточка — для витрины/поиска."""
    final_price = serializers.ReadOnlyField()
    genres = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ["id", "title", "slug", "cover_image", "price",
                  "discount_percent", "final_price", "genres"]


class GameDetailSerializer(serializers.ModelSerializer):
    """Полная карточка — страница игры (только чтение вложенных объектов)."""
    final_price = serializers.ReadOnlyField()
    genres = GenreSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    screenshots = ScreenshotSerializer(many=True, read_only=True)
    requirements = SystemRequirementSerializer(read_only=True)

    class Meta:
        model = Game
        fields = "__all__"


class GameWriteSerializer(serializers.ModelSerializer):
    """
    Используется для create/update игры (только staff, см. GameViewSet).
    В отличие от GameDetailSerializer, тут genres/tags/developers/publishers
    можно реально задать при записи — просто списком id.
    После сохранения ответ всё равно отдаём через GameDetailSerializer.
    """

    class Meta:
        model = Game
        fields = [
            "id", "title", "slug", "short_description", "description", "cover_image",
            "price", "discount_percent", "release_date",
            "genres", "tags", "developers", "publishers", "is_published",
        ]
        read_only_fields = ["id"]
