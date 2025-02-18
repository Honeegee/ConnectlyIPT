"""
URL configuration for connectly_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from posts.views import home

urlpatterns = [
    path('', home, name='home'),  # Root URL showing API documentation
    path('admin/', admin.site.urls),
    path('api/', include('posts.urls')),  # Changed to api/ for cleaner URLs
]
