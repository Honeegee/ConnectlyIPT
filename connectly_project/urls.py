"""
URL configuration for connectly_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from posts.views import APIDocsView, login_view, home_view, logout_view
from posts.social_auth import GoogleOAuth2LoginView, OAuthCompleteView

from posts.urls import frontend_urlpatterns, api_urlpatterns

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(api_urlpatterns)),
    path('api/docs/', APIDocsView.as_view(), name='api_docs'),
    
    # OAuth URLs
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('auth/google/', GoogleOAuth2LoginView.as_view(), name='google_login'),
    path('oauth/complete/', OAuthCompleteView.as_view(), name='oauth_complete'),
    
    # Frontend URLs
    path('', include(frontend_urlpatterns)),
]

# Serve media files in both development and production
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
