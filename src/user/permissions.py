from rest_framework import permissions

from user.enums import UserRole


class EmployerPermission(permissions.BasePermission):
    message = "You must be the employer to perform this action."

    def has_permission(self, request, view):
        return request.user.role == UserRole.EMPLOYER.value
