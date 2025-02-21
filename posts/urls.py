
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    UserListCreate, UserDetail,
    PostListCreate, PostDetail,
    CommentListCreate, CommentDetail,
    LoginView, PostLikeView, NewsFeedView,
    login_view, home_view, logout_view,
    APIDocsView, post_comments, profile_view,
    UserProfileView, UserProfilePostsView, UserFollowView
)

# Frontend URLs
frontend_urlpatterns = [
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/<str:username>/', profile_view, name='user-profile'),
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
    
# Profile URLs 
    path('profiles/me/', UserProfileView.as_view(), name='my-profile'),
    path('profiles/<str:username>/', UserProfileView.as_view(), name='user-profile'),
    path('profiles/<str:username>/posts/', UserProfilePostsView.as_view(), name='profile-posts'),
    path('profiles/<str:username>/follow/', UserFollowView.as_view(), name='user-follow'),
    path('profiles/<str:username>/unfollow/', UserFollowView.as_view(), name='user-unfollow'),
]

# Combine API and frontend URLs
urlpatterns = api_urlpatterns + frontend_urlpatterns
