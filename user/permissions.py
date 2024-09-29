from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsSuperAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True  # Allow read-only permissions for GET requests
        user_role = request.user.role
        return request.user.is_authenticated and user_role.roles in ['Superadmin', 'Streamer']

    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True  # Allow read-only permissions for GET requests
        user_role = request.user.role
        return request.user.is_authenticated and user_role.roles in ['Superadmin', 'Streamer']


class CustomTeamPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a Superadmin
        print(request.user)
        if request.user.role.roles == 'Superadmin':
            return True

        # For users with role Viewer and streamer, only allow GET requests
        elif request.method == 'GET' and request.user.role.roles in ['Viewer', 'Streamer']:
            return True

        return False
