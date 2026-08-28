from django.db import IntegrityError
from django.db.models import Q
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import Friendship
from .permissions import IsFriendshipParticipant, IsRecipient
from .serializers import (
    RegisterSerializer, UserMeSerializer, UserPublicSerializer,
    FriendshipSerializer, FriendRequestCreateSerializer,
)

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


class FriendshipViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/auth/friendships/            — все мои заявки (входящие+исходящие, любой статус)
    POST   /api/v1/auth/friendships/  {to_user}  — отправить заявку в друзья
                                                    (если у адресата уже висит встречная заявка
                                                    к нам — дружба подтверждается сразу же)
    DELETE /api/v1/auth/friendships/<id>/        — отменить свою заявку / удалить из друзей
    POST   /api/v1/auth/friendships/<id>/accept/ — принять входящую заявку (только получатель)
    POST   /api/v1/auth/friendships/<id>/decline/— отклонить входящую заявку (только получатель)
    POST   /api/v1/auth/friendships/<id>/block/  — заблокировать пользователя (любой участник)
    """
    permission_classes = [permissions.IsAuthenticated, IsFriendshipParticipant]

    def get_queryset(self):
        user = self.request.user
        return (
            Friendship.objects.filter(Q(from_user=user) | Q(to_user=user))
            .select_related("from_user", "to_user")
        )

    def get_serializer_class(self):
        return FriendRequestCreateSerializer if self.action == "create" else FriendshipSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        to_user = serializer.validated_data["to_user"]

        # Если нас уже когда-то заблокировали (в любую сторону) — заявку не создаём.
        blocked = Friendship.objects.filter(
            Q(from_user=request.user, to_user=to_user) | Q(from_user=to_user, to_user=request.user),
            status="blocked",
        ).exists()
        if blocked:
            raise ValidationError("Невозможно отправить заявку: пользователь заблокирован.")

        # Взаимная заявка = дружба сразу, без второго "accept".
        reverse = Friendship.objects.filter(from_user=to_user, to_user=request.user, status="pending").first()
        if reverse:
            reverse.status = "accepted"
            reverse.save(update_fields=["status"])
            return Response(FriendshipSerializer(reverse).data, status=status.HTTP_200_OK)

        try:
            friendship = serializer.save(from_user=request.user)
        except IntegrityError:
            raise ValidationError("Заявка в друзья уже существует.")

        return Response(
            FriendshipSerializer(friendship).data,
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsRecipient])
    def accept(self, request, pk=None):
        friendship = self.get_object()
        friendship.status = "accepted"
        friendship.save(update_fields=["status"])
        return Response(FriendshipSerializer(friendship).data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated, IsRecipient])
    def decline(self, request, pk=None):
        friendship = self.get_object()
        friendship.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def block(self, request, pk=None):
        """Заблокировать: доступно любому из двух участников заявки/дружбы."""
        friendship = self.get_object()
        friendship.status = "blocked"
        friendship.save(update_fields=["status"])
        return Response(FriendshipSerializer(friendship).data)
