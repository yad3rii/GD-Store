from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserMeSerializer, UserPublicSerializer

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """POST /api/v1/auth/register/"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    """POST /api/v1/auth/login/ -> {access, refresh} (JWT)"""
    pass


class MeView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/v1/auth/me/"""
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserPublicProfileView(generics.RetrieveAPIView):
    """GET /api/v1/auth/users/<id>/ — публичный профиль (как страница профиля в Steam)"""
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]
