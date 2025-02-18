from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import (
    UserListCreate, UserDetail,
    PostListCreate, PostDetail,
    CommentListCreate, CommentDetail,
    LoginView
)

urlpatterns = [
    # Authentication URLs
    path('login/', LoginView.as_view(), name='login'),
    path('token/', obtain_auth_token, name='token_obtain'),
    
    # User URLs
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),
    
    # Post URLs
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetail.as_view(), name='post-detail'),
    
    # Comment URLs
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetail.as_view(), name='comment-detail'),
]
