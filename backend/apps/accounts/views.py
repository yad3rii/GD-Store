from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.db.models import Q

from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Friendship
from .permissions import IsFriendshipParticipant, IsRecipient
from .serializers import (
    FriendRequestCreateSerializer,
    FriendshipSerializer,
    RegisterSerializer,
    UserMeSerializer,
    UserPublicSerializer,
)


User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LoginView(TokenObtainPairView):
    pass


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserPublicProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.AllowAny]


class FriendshipViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        IsFriendshipParticipant,
    ]

    def get_queryset(self):
        user = self.request.user

        return (
            Friendship.objects
            .filter(Q(from_user=user) | Q(to_user=user))
            .select_related("from_user", "to_user")
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "create":
            return FriendRequestCreateSerializer

        return FriendshipSerializer

    def create(self, request, *args, **kwargs):
        del args, kwargs

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        to_user = serializer.validated_data["to_user"]

        blocked = Friendship.objects.filter(
            Q(from_user=request.user, to_user=to_user)
            | Q(from_user=to_user, to_user=request.user),
            status="blocked",
        ).exists()

        if blocked:
            raise ValidationError(
                "Невозможно отправить заявку: пользователь заблокирован."
            )

        reverse_request = Friendship.objects.filter(
            from_user=to_user,
            to_user=request.user,
            status="pending",
        ).first()

        if reverse_request:
            reverse_request.status = "accepted"
            reverse_request.save(update_fields=["status"])

            return Response(
                FriendshipSerializer(reverse_request).data,
                status=status.HTTP_200_OK,
            )

        try:
            friendship = serializer.save(from_user=request.user)
        except IntegrityError as exc:
            raise ValidationError(
                "Заявка в друзья уже существует."
            ) from exc

        return Response(
            FriendshipSerializer(friendship).data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            permissions.IsAuthenticated,
            IsRecipient,
        ],
    )
    def accept(self, _request, pk=None):
        _ = pk

        friendship = self.get_object()

        if friendship.status != "pending":
            raise ValidationError(
                "Можно принять только ожидающую заявку."
            )

        friendship.status = "accepted"
        friendship.save(update_fields=["status"])

        return Response(
            FriendshipSerializer(friendship).data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        permission_classes=[
            permissions.IsAuthenticated,
            IsRecipient,
        ],
    )
    def decline(self, _request, pk=None):
        _ = pk

        friendship = self.get_object()

        if friendship.status != "pending":
            raise ValidationError(
                "Можно отклонить только ожидающую заявку."
            )

        friendship.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["post"],
    )
    def block(self, _request, pk=None):
        _ = pk

        friendship = self.get_object()
        friendship.status = "blocked"
        friendship.save(update_fields=["status"])

        return Response(
            FriendshipSerializer(friendship).data,
            status=status.HTTP_200_OK,
        )