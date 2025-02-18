"""
URL configuration for connectly_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from posts.views import HomeView, login_view
from posts.social_auth import GoogleOAuth2LoginView, OAuthCompleteView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),  # Root URL showing API documentation
    path('admin/', admin.site.urls),
    path('api/', include('posts.urls')),  # API endpoints
    path('login/', login_view, name='login'),  # Login page with Google OAuth
    
    # OAuth URLs - social-auth-django handles the main flow
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('auth/google/', GoogleOAuth2LoginView.as_view(), name='google_login'),  # Manual token verification endpoint
    path('oauth/complete/', OAuthCompleteView.as_view(), name='oauth_complete'),  # Callback endpoint
]
