from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Game, Genre, Tag
from .serializers import (
    GameListSerializer, GameDetailSerializer, GameWriteSerializer,
    GenreSerializer, TagSerializer,
)
from .filters import GameFilter
from .permissions import IsAdminOrReadOnly


class GameViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/catalog/games/            — витрина со всеми играми (фильтры/сортировка)
    GET    /api/v1/catalog/games/<slug>/     — страница игры
    POST   /api/v1/catalog/games/            — добавить игру (только staff)
    PATCH  /api/v1/catalog/games/<slug>/     — изменить игру (только staff)
    DELETE /api/v1/catalog/games/<slug>/     — удалить игру (только staff)

    Фильтры: ?genres=1&price__gte=100&price__lte=1000&on_sale=true
             &ordering=-release_date&search=witcher

    Раньше это был ReadOnlyModelViewSet — добавить/поменять игру можно было
    только вручную через Django admin, из API — никак, даже админом.
    """
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GameFilter
    search_fields = ["title", "short_description"]
    ordering_fields = ["price", "release_date", "created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        qs = Game.objects.prefetch_related("genres", "tags", "screenshots")
        # Обычные посетители видят только опубликованные игры,
        # staff (для модерации/предпросмотра) видит вообще всё.
        if self.request.user and self.request.user.is_authenticated and self.request.user.is_staff:
            return qs
        return qs.filter(is_published=True)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GameDetailSerializer
        if self.action in ("create", "update", "partial_update"):
            return GameWriteSerializer
        return GameListSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
