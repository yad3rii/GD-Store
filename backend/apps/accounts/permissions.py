from rest_framework import permissions


class IsFriendshipParticipant(permissions.BasePermission):
    """
    Заявку в друзья (Friendship) может смотреть/менять только один из её
    участников — тот, кто отправил (from_user), или тот, кто получил (to_user).
    Посторонние пользователи доступа не имеют.
    """

    def has_object_permission(self, request, view, obj):
        return request.user in (obj.from_user, obj.to_user)


class IsRecipient(permissions.BasePermission):
    """
    Принять/отклонить заявку в друзья может только тот, кому она адресована
    (to_user) — не тот, кто её отправил.
    """

    def has_object_permission(self, request, view, obj):
        return obj.to_user == request.user