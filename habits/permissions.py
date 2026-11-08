from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwner(BasePermission):
    """Доступ только владельцу объекта."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.user_id == request.user.id
        return obj.user_id == request.user.id


class IsOwnerOrPublicReadOnly(BasePermission):
    """Публичные привычки доступны на чтение всем; изменять — только владелец."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return obj.user_id == request.user.id or obj.is_public
        return obj.user_id == request.user.id
