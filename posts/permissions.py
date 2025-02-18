from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth.models import Group

class IsPostAuthor(BasePermission):
    """
    Custom permission to only allow authors of a post to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the author of the post
        return obj.author == request.user

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
