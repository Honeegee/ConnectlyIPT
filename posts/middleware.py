from django.http import HttpResponseForbidden
from django.contrib.auth.models import User

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get user role if authenticated
        if request.user.is_authenticated:
            role = request.user.profile.role
            
            # Define role-based permissions
            ROLE_PERMISSIONS = {
                'guest': {
                    'allowed_methods': ['GET'],
                    'allowed_paths': ['/api/posts/', '/api/posts/\d+/', '/api/feed/']
                },
                'user': {
                    'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE'],
                    'allowed_paths': [
                        '/api/posts/',
                        '/api/posts/\d+/',
                        '/api/comments/',
                        '/api/comments/\d+/',
                        '/api/feed/',
                        '/api/profile/',
                        '/api/likes/'
                    ]
                },
                'admin': {
                    # Admin has full access
                    'allowed_methods': ['GET', 'POST', 'PUT', 'DELETE'],
                    'allowed_paths': ['.*']  # Regex to match all paths
                }
            }

            # Skip RBAC for admin users or if middleware is applied to admin/auth URLs
            if role == 'admin' or request.path.startswith(('/admin/', '/auth/')):
                return self.get_response(request)

            # Get permissions for user role
            role_perms = ROLE_PERMISSIONS.get(role, {})
            allowed_methods = role_perms.get('allowed_methods', [])
            allowed_paths = role_perms.get('allowed_paths', [])

            # Check if request method and path are allowed
            if request.method not in allowed_methods:
                return HttpResponseForbidden('Method not allowed for your role')

            # Check if path is allowed (using regex patterns)
            import re
            path_allowed = any(re.match(pattern, request.path) for pattern in allowed_paths)
            if not path_allowed:
                return HttpResponseForbidden('Access denied for your role')

        return self.get_response(request)
