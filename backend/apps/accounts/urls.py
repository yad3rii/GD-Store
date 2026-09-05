from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    # Auth
    path("register/", views.RegisterView.as_view()),
    path("login/", views.LoginView.as_view()),
    path("login/refresh/", TokenRefreshView.as_view()),
    path("me/", views.MeView.as_view()),
    path("users/<uuid:pk>/", views.UserPublicProfileView.as_view()),
    
    # Friends
    path("friends/", views.FriendshipListCreateView.as_view()),
    path("friends/<int:pk>/accept/", views.AcceptFriendRequestView.as_view()),
    path("friends/<int:pk>/reject/", views.RejectFriendRequestView.as_view()),
]