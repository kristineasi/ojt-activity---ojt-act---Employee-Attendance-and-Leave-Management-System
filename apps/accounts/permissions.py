from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    message = "Only managers can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == "manager")
