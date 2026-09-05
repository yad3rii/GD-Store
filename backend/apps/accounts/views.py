from rest_framework import generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .serializers import RegisterSerializer, UserMeSerializer, UserPublicSerializer
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from .models import Friendship
from .serializers import FriendshipSerializer

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

class FriendshipListCreateView(generics.ListCreateAPIView):
    """
    GET /api/v1/auth/friends/ — список друзей и заявок
    POST /api/v1/auth/friends/ — отправить заявку { "to_user_id": "<uuid>" }
    """

    serializer_class = FriendshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        status_param = self.request.query_params.get("status")

        queryset = Friendship.objects.filter(Q(from_user=user) | Q(to_user=user))
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)


class FriendshipActionView(APIView):
    """
    PATCH /api/v1/auth/friends/<id>/accept/ — принять заявку
    DELETE /api/v1/auth/friends/<id>/reject/ — отклонить/удалить из друзей
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            friendship = Friendship.objects.get(id=pk, to_user=request.user, status="pending")
        except Friendship.DoesNotExist:
            return Response(
                {"detail": "Заявка не найдена или уже обработана."},
                status=status.HTTP_404_NOT_FOUND,
            )

        friendship.status = "accepted"
        friendship.save()
        return Response({"detail": "Заявка в друзья принята."})

    def delete(self, request, pk):
        try:
            friendship = Friendship.objects.get(
                Q(id=pk) & (Q(from_user=request.user) | Q(to_user=request.user))
            )
        except Friendship.DoesNotExist:
            return Response({"detail": "Запись не найдена."}, status=status.HTTP_404_NOT_FOUND)

        friendship.delete()
        return Response({"detail": "Удалено из друзей."}, status=status.HTTP_204_NO_CONTENT)
    
class AcceptFriendRequestView(APIView):
    """POST /api/v1/auth/friends/<id>/accept/ — принять заявку"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            friendship = Friendship.objects.get(id=pk, to_user=request.user, status="pending")
        except Friendship.DoesNotExist:
            return Response(
                {"detail": "Заявка не найдена или уже обработана."},
                status=status.HTTP_404_NOT_FOUND,
            )

        friendship.status = "accepted"
        friendship.save()
        return Response({"detail": "Заявка в друзья принята."})


class RejectFriendRequestView(APIView):
    """POST или DELETE /api/v1/auth/friends/<id>/reject/ — отклонить заявку / удалить из друзей"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        return self._delete_friendship(request, pk)

    def delete(self, request, pk):
        return self._delete_friendship(request, pk)

    def _delete_friendship(self, request, pk):
        try:
            friendship = Friendship.objects.get(
                Q(id=pk) & (Q(from_user=request.user) | Q(to_user=request.user))
            )
        except Friendship.DoesNotExist:
            return Response({"detail": "Запись не найдена."}, status=status.HTTP_404_NOT_FOUND)

        friendship.delete()
        return Response({"detail": "Удалено из друзей."}, status=status.HTTP_204_NO_CONTENT)