from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.role == request.user.AUTHENTICATED
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.role == request.user.MODERATOR
            or request.user.role == request.user.ADMINISTRATOR
            or request.user.role == request.user.SUPERUSER
        )
