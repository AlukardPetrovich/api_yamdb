from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrOwnerOrSuperuserForUser(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.role == 'admin'
            or (request.user and request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        print(obj)
        return (
            (request.user and request.user.is_superuser)
            or (request.user and request.user.role == 'admin')
            or (request.user and request.user.role == obj.user)
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated and request.user.role == 'admin')
        )


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or request.user.role == 'admin'
        )


