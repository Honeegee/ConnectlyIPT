from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth.models import Group

class IsPostAuthor(BasePermission):
    """
    Custom permission to allow authors and admins to edit/delete posts.
    """
    def has_permission(self, request, view):
        # Guest users can't perform write operations
        if request.user.profile.role == 'guest':
            return request.method in SAFE_METHODS
        return True

    def has_object_permission(self, request, view, obj):
        # Guest users can't perform write operations
        if request.user.profile.role == 'guest':
            return request.method in SAFE_METHODS

        # For non-guests:
        # Read permissions are allowed for any request
        if request.method in SAFE_METHODS:
            return True
            
        # Write permissions only for author or admin
        return obj.author == request.user or request.user.groups.filter(name='Admin').exists()

class IsCommentAuthor(BasePermission):
    """
    Custom permission to only allow authors of a comment to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.author == request.user

class IsAdminUser(BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='Admin').exists()

class ReadOnly(BasePermission):
    """
    Custom permission to only allow read-only methods.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
