from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает чтение всем пользователям.
    Создание, обновление и удаление — только администраторам (is_staff).
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)