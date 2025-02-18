from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from .models import Post, Comment
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsPostAuthor, IsCommentAuthor, IsAdminUser, ReadOnly
from singletons.logger_singleton import LoggerSingleton
from singletons.config_manager import ConfigManager
from factories.post_factory import PostFactory

class UserDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, pk):
        """Retrieve a user"""
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update a user"""
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a user"""
        user = get_object_or_404(User, pk=pk)
        username = user.username
        user.delete()
        return Response(
            {"message": f"User '{username}' was successfully deleted"},
            status=status.HTTP_200_OK
        )

class UserListCreate(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [AllowAny()]
        return [IsAuthenticated()]
    def get(self, request):
        """List all users"""
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new user with secure password"""
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Create user with hashed password
                user = User.objects.create_user(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=request.data.get('password')
                )
                
                # Create auth token for the new user
                token, _ = Token.objects.get_or_create(user=user)
                
                response_data = UserSerializer(user).data
                response_data['token'] = token.key
                
                return Response(response_data, status=status.HTTP_201_CREATED)
            except Exception as e:
                if 'UNIQUE constraint' in str(e):
                    if 'username' in str(e):
                        return Response(
                            {'error': 'Username already exists. Please choose a different username.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    elif 'email' in str(e):
                        return Response(
                            {'error': 'Email already exists. Please use a different email.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostAuthor]
    def get(self, request, pk):
        """Retrieve a post"""
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update a post"""
        post = get_object_or_404(Post, pk=pk)
        
        # Check if user is the author
        if post.author != request.user:
            return Response(
                {"error": "You do not have permission to edit this post"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a post"""
        post = get_object_or_404(Post, pk=pk)
        
        # Check if user is the author
        if post.author != request.user:
            return Response(
                {"error": "You do not have permission to delete this post"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        post_id = post.id
        post.delete()
        return Response(
            {"message": f"Post {post_id} was successfully deleted"},
            status=status.HTTP_200_OK
        )

class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def __init__(self):
        super().__init__()
        self.logger = LoggerSingleton().get_logger()
        self.config = ConfigManager()

    def get(self, request):
        """List all posts with their comments"""
        try:
            page_size = self.config.get_setting('DEFAULT_PAGE_SIZE')
            posts = Post.objects.all()[:page_size]
            serializer = PostSerializer(posts, many=True)
            response = Response(serializer.data)
            LoggerSingleton().log_api_request(request, response)
            return response
        except Exception as e:
            self.logger.error(f"Error fetching posts: {str(e)}")
            return Response(
                {'error': 'Failed to fetch posts'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request):
        """Create a new post using PostFactory"""
        try:
            post_data = request.data
            post = PostFactory.create_post(
                author=request.user,
                post_type=post_data.get('post_type', 'text'),
                title=post_data.get('title'),
                content=post_data.get('content', ''),
                metadata=post_data.get('metadata')
            )
            serializer = PostSerializer(post)
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            LoggerSingleton().log_api_request(request, response)
            return response
        except ValidationError as e:
            self.logger.error(f"Validation error creating post: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            self.logger.error(f"Error creating post: {str(e)}")
            return Response(
                {'error': 'Failed to create post'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CommentDetail(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsCommentAuthor]
    def get(self, request, pk):
        """Retrieve a comment"""
        comment = get_object_or_404(Comment, pk=pk)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk):
        """Update a comment"""
        comment = get_object_or_404(Comment, pk=pk)
        
        # Check if user is the author
        if comment.author != request.user:
            return Response(
                {"error": "You do not have permission to edit this comment"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Delete a comment"""
        comment = get_object_or_404(Comment, pk=pk)
        
        # Check if user is the author
        if comment.author != request.user:
            return Response(
                {"error": "You do not have permission to delete this comment"},
                status=status.HTTP_403_FORBIDDEN
            )
            
        comment_id = comment.id
        comment.delete()
        return Response(
            {"message": f"Comment {comment_id} was successfully deleted"},
            status=status.HTTP_200_OK
        )

class CommentListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """List all comments"""
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new comment"""
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                token, _ = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user_id': user.id,
                    'username': user.username
                })
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(
            {'error': 'Username and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

# Keep the home view for API documentation
from django.shortcuts import render
from django.conf import settings

def login_view(request):
    """Render the Google OAuth login page"""
    logger = LoggerSingleton().get_logger()
    client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    
    if not client_id:
        logger.error("Google OAuth client ID is not configured")
        return render(request, 'posts/login.html', {
            'error': 'OAuth configuration error'
        })
    
    logger.info(f"Rendering login page with client ID: {client_id[:10]}...")
    return render(request, 'posts/login.html', {
        'google_oauth2_client_id': client_id
    })

class HomeView(APIView):
    """Homepage view showing API documentation"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
        "message": "Welcome to Connectly API",
        "endpoints": {
            "users": {
                "list": "/api/users/ [GET]",
                "create": "/api/users/ [POST]",
                "retrieve": "/api/users/{id}/ [GET]",
                "update": "/api/users/{id}/ [PUT]",
                "delete": "/api/users/{id}/ [DELETE]"
            },
            "posts": {
                "list": "/api/posts/ [GET]",
                "create": "/api/posts/ [POST]",
                "retrieve": "/api/posts/{id}/ [GET]",
                "update": "/api/posts/{id}/ [PUT]",
                "delete": "/api/posts/{id}/ [DELETE]"
            },
            "comments": {
                "list": "/api/comments/ [GET]",
                "create": "/api/comments/ [POST]",
                "retrieve": "/api/comments/{id}/ [GET]",
                "update": "/api/comments/{id}/ [PUT]",
                "delete": "/api/comments/{id}/ [DELETE]"
            }
        }
    })
