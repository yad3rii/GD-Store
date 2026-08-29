from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Каталог (игры, жанры, теги) — читать может кто угодно (в том числе анонимы),
    а создавать/менять/удалять — только персонал (is_staff), т.е. модераторы/админы
    магазина. Обычные покупатели каталог не редактируют.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
