from rest_framework import viewsets, permissions
from .models import Review
from .serializers import ReviewSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """
    GET  /api/v1/reviews/?game=<id>  — отзывы к игре
    POST /api/v1/reviews/            — оставить отзыв (только если игра в библиотеке — проверить в perform_create)
    """
    serializer_class = ReviewSerializer
    filterset_fields = ["game"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = Review.objects.select_related("user", "game")
        game_id = self.request.query_params.get("game")
        return qs.filter(game_id=game_id) if game_id else qs

    def perform_create(self, serializer):
        # TODO: проверить apps.library.LibraryEntry.objects.filter(user=..., game=...).exists()
        serializer.save(user=self.request.user)
