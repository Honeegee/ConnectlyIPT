
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    UserListCreate, UserDetail,
    PostListCreate, PostDetail,
    CommentListCreate, CommentDetail,
    LoginView, PostLikeView, NewsFeedView,
    login_view, home_view, logout_view,
    APIDocsView, post_comments
)

# Frontend URLs
frontend_urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
]

# API URLs
api_urlpatterns = [
    # Authentication URLs
    path('login/', LoginView.as_view(), name='api_login'),
    path('token/', obtain_auth_token, name='token_obtain'),
    
    # API Documentation
    path('docs/', APIDocsView.as_view(), name='api_docs'),
    
    # User URLs
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    
    # Post URLs
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),
    
    # Comment URLs
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetail.as_view(), name='comment-detail'),
    
    # Like URLs
    path('posts/<int:pk>/like/', PostLikeView.as_view(), name='post-like'),
    
    # Feed URL
    path('feed/', NewsFeedView.as_view(), name='news-feed'),
    
    # Post Comments URL
    path('posts/<int:post_id>/comments/', post_comments, name='post-comments'),
]

# Combine frontend and API URLs, with frontend URLs first
urlpatterns = frontend_urlpatterns + api_urlpatterns
