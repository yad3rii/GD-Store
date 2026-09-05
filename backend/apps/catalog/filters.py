import django_filters
from .models import Game


class GameFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    genres = django_filters.CharFilter(
        field_name="genres__slug", lookup_expr="exact"
    )
    tags = django_filters.CharFilter(
        field_name="tags__slug", lookup_expr="exact"
    )

    class Meta:
        model = Game
        fields = ["min_price", "max_price", "genres", "tags"]