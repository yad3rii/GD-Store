from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination

from .filters import GameFilter
from .models import Game, Genre, Tag
from .permissions import IsAdminOrReadOnly
from .serializers import (
    GameDetailSerializer,
    GameListSerializer,
    GenreSerializer,
    TagSerializer,
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = "page_size"
    max_page_size = 100


class GameViewSet(viewsets.ModelViewSet):
    """
    GET /api/v1/catalog/games/ — список игр (с пагинацией, фильтрами, поиском)
    GET /api/v1/catalog/games/<slug>/ — детальная страница игры
    POST/PUT/DELETE — только для is_staff
    """

    queryset = (
        Game.objects.filter(is_published=True)
        .select_related("requirements")
        .prefetch_related(
            "genres", "tags", "developers", "publishers", "screenshots"
        )
        .order_by("-created_at")
    )
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = GameFilter
    search_fields = ["title", "short_description", "description"]
    ordering_fields = ["price", "release_date", "created_at"]
    lookup_field = "slug"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GameDetailSerializer
        return GameListSerializer


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "slug"


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = "id"