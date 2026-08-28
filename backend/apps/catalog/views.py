from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.filters import OrderingFilter, SearchFilter

from .models import Game, Genre, Tag
from .serializers import (
    GameDetailSerializer,
    GameListSerializer,
    GenreSerializer,
    TagSerializer,
)


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/catalog/games/ — витрина со всеми играми
    GET /api/v1/catalog/games/<slug>/ — страница игры
    """

    queryset = (
        Game.objects.filter(is_published=True)
        .select_related("requirements")
        .prefetch_related(
            "genres", "tags", "developers", "publishers", "screenshots"
        )
    )
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["genres", "tags"]
    search_fields = ["title", "short_description"]
    ordering_fields = ["price", "release_date", "created_at"]
    lookup_field = "slug"

    def get_serializer_class(self):
        return (
            GameDetailSerializer
            if self.action == "retrieve"
            else GameListSerializer
        )


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"