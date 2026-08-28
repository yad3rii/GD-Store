from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

router = DefaultRouter()
router.register("friendships", views.FriendshipViewSet, basename="friendship")

urlpatterns = [
    path("register/", views.RegisterView.as_view()),
    path("login/", views.LoginView.as_view()),
    path("login/refresh/", TokenRefreshView.as_view()),
    path("me/", views.MeView.as_view()),
    path("users/<uuid:pk>/", views.UserPublicProfileView.as_view()),
    path("", include(router.urls)),
]