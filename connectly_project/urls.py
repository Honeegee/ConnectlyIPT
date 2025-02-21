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

urlpatterns = [
    # API endpoints first for proper routing
    path('api/', include('posts.urls')),  # API endpoints
    path('api/docs/', APIDocsView.as_view(), name='api_docs'),  # API documentation
    
    # Admin URL
    path('admin/', admin.site.urls),
    
    # Frontend URLs
    path('', home_view, name='home'),  # Root URL showing news feed
    path('login/', login_view, name='login'),  # Login page with Google OAuth
    path('logout/', logout_view, name='logout'),  # Logout
    
    # OAuth URLs - social-auth-django handles the main flow
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('auth/google/', GoogleOAuth2LoginView.as_view(), name='google_login'),  # Manual token verification endpoint
    path('oauth/complete/', OAuthCompleteView.as_view(), name='oauth_complete'),  # Callback endpoint
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) if settings.DEBUG else []
