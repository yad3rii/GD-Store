from rest_framework import viewsets, permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Game, Genre, Tag
from .serializers import GameListSerializer, GameDetailSerializer, GenreSerializer, TagSerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /api/v1/catalog/games/            — витрина со всеми играми (фильтры/сортировка)
    GET /api/v1/catalog/games/<id>/       — страница игры
    Фильтры: ?genres=1&price__lte=1000&ordering=-release_date&search=witcher
    """
    queryset = Game.objects.filter(is_published=True).prefetch_related("genres", "tags")
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["genres", "tags"]
    search_fields = ["title", "short_description"]
    ordering_fields = ["price", "release_date", "created_at"]
    lookup_field = "slug"

    def get_serializer_class(self):
        return GameDetailSerializer if self.action == "retrieve" else GameListSerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [permissions.AllowAny]


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
