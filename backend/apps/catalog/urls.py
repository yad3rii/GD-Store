from rest_framework.routers import DefaultRouter
from .views import GameViewSet, GenreViewSet, TagViewSet

router = DefaultRouter()
router.register("games", GameViewSet, basename="game")
router.register("genres", GenreViewSet, basename="genre")
router.register("tags", TagViewSet, basename="tag")

urlpatterns = router.urls
