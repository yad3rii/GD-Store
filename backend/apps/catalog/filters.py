import django_filters
from .models import Game


class GameFilter(django_filters.FilterSet):
    price__gte = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    price__lte = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    on_sale = django_filters.BooleanFilter(method="filter_on_sale")

    class Meta:
        model = Game
        fields = ["genres", "tags", "price__gte", "price__lte"]

    def filter_on_sale(self, queryset, name, value):
        if value:
            return queryset.filter(discount_percent__gt=0)
        return queryset
