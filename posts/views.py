
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.generics import ListAPIView
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib import messages
from django.db import IntegrityError, transaction
from .models import Post, Comment, Like, UserFollow
from .serializers import (UserSerializer, PostSerializer, CommentSerializer, 
                        LikeSerializer, UserProfileSerializer)
from .permissions import IsPostAuthor, IsCommentAuthor, IsAdminUser, ReadOnly
from singletons.logger_singleton import LoggerSingleton
from singletons.config_manager import ConfigManager
from factories.post_factory import PostFactory

# Initialize logger
logger = LoggerSingleton().get_logger()

class UserDetail(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
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
                # Get the password from request data
                password = request.data.get('password')
                
                # Password validation
                if not password:
                    return Response({'error': 'Password is required.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                if len(password) < 8:
                    return Response({'error': 'Password must be at least 8 characters long.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                if not any(char.isupper() for char in password):
                    return Response({'error': 'Password must contain at least one uppercase letter.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                if not any(char.islower() for char in password):
                    return Response({'error': 'Password must contain at least one lowercase letter.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                if not any(char.isdigit() for char in password):
                    return Response({'error': 'Password must contain at least one number.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                if not any(not char.isalnum() for char in password):
                    return Response({'error': 'Password must contain at least one special character.'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Create user with validated password
                user = User.objects.create_user(
                    username=serializer.validated_data['username'],
                    email=serializer.validated_data['email'],
                    password=password
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
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated, IsPostAuthor]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    def get(self, request, pk):
        """Retrieve a post"""
        post = get_object_or_404(Post, pk=pk)
        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        """Update a post"""
        post = get_object_or_404(Post, pk=pk)
        
        # Permission check is handled by IsPostAuthor permission class
            
        try:
            serializer = PostSerializer(post, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid():
                updated_post = serializer.save()
                return Response(PostSerializer(updated_post, context={'request': request}).data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        """Delete a post"""
        post = get_object_or_404(Post, pk=pk)
        
        # Permission check is handled by IsPostAuthor permission class
            
        post_id = post.id
        post.delete()
        return Response(
            {"message": f"Post {post_id} was successfully deleted"},
            status=status.HTTP_200_OK
        )

class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def __init__(self):
        super().__init__()
        self.logger = LoggerSingleton().get_logger()
        self.config = ConfigManager()

    def get(self, request):
        """List all posts with their comments"""
        try:
            page_size = self.config.get_setting('DEFAULT_PAGE_SIZE')
            posts = Post.objects.all()[:page_size]
            serializer = PostSerializer(posts, many=True, context={'request': request})
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
        """Create a new post with optional media"""
        try:
            with transaction.atomic():
                # Prepare post data
                post_data = request.data.copy()
                post_data['author'] = request.user.id
                
                # Get media file if present
                media_file = request.FILES.get('media')
                post_type = post_data.get('post_type', 'text')

                # Let the model handle metadata validation and processing
                if media_file:
                    # Keep metadata as is - model's clean() method will handle validation
                    pass

                # Create post using serializer
                serializer = PostSerializer(data=post_data, context={'request': request})
                if not serializer.is_valid():
                    self.logger.error(f"Validation error: {serializer.errors}")
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # Save post without media first
                post = serializer.save()

                # Handle media file separately if present
                if media_file:
                    # Save the file directly without opening it
                    post.media = media_file
                    post.save()

                # Return complete post data
                response_serializer = PostSerializer(post, context={'request': request})
                response = Response(response_serializer.data, status=status.HTTP_201_CREATED)
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
    authentication_classes = [TokenAuthentication, SessionAuthentication]
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
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request):
        """List comments, optionally filtered by post"""
        post_id = request.query_params.get('post')
        if post_id:
            comments = Comment.objects.filter(post_id=post_id)
        else:
            comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Create a new comment"""
        try:
            data = request.data.copy()
            data['author'] = request.user.id
            if 'content' in data:
                data['text'] = data.pop('content')

            serializer = CommentSerializer(data=data)
            if serializer.is_valid():
                comment = serializer.save()
                return Response(
                    CommentSerializer(comment).data,
                    status=status.HTTP_201_CREATED
                )
            return Response(
                {'error': 'Invalid comment data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

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

@login_required
def profile_view(request, username=None):
    """Render the profile page"""
    try:
        if username is None and request.user.is_authenticated:
            return redirect('user-profile', username=request.user.username)
            
        if username is None:
            return redirect('login')
            
        user = User.objects.get(username=username)
            
        profile = user.profile
        is_following = UserFollow.objects.filter(follower=request.user, followed=user).exists()
        
        return render(request, 'posts/profile.html', {
            'user': request.user,
            'profile': profile,
            'is_following': is_following,
            'is_admin': request.user.groups.filter(name='Admin').exists()
        })
            
    except User.DoesNotExist:
        messages.error(request, 'User not found')
        return redirect('home')
    except Exception as e:
        logger = LoggerSingleton().get_logger()
        logger.error(f"Error in profile_view: {str(e)}")
        messages.error(request, 'Error loading profile')
        return redirect('home')

def login_view(request):
    """Handle login and signup forms, and render the login page"""
    if request.user.is_authenticated:
        return redirect('home')

    logger = LoggerSingleton().get_logger()
    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'login':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                logger.info(f"User {username} logged in successfully")
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
                
        elif form_type == 'signup':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            # Validate password
            if not password:
                messages.error(request, 'Password is required.')
                return render(request, 'posts/login.html', {'google_oauth2_client_id': client_id})
                
            # Password validation rules
            if len(password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
                return render(request, 'posts/login.html', {'google_oauth2_client_id': client_id})
                
            if not any(char.isupper() for char in password):
                messages.error(request, 'Password must contain at least one uppercase letter.')
                return render(request, 'posts/login.html', {'google_oauth2_client_id': client_id})
                
            if not any(char.islower() for char in password):
                messages.error(request, 'Password must contain at least one lowercase letter.')
                return render(request, 'posts/login.html', {'google_oauth2_client_id': client_id})
                
            if not any(char.isdigit() for char in password):
                messages.error(request, 'Password must contain at least one number.')
                return render(request, 'posts/login.html', {'google_oauth2_client_id': client_id})
                
            if not any(not char.isalnum() for char in password):
                messages.error(request, 'Password must contain at least one special character.')
                return render(request, 'posts/login.html', {'google_oauth2_client_id': client_id})
            
            # Validate email
            if not email:
                messages.error(request, 'Email is required.')
                return render(request, 'posts/login.html', {'google_oauth2_client_id': client_id})
                
            # Validate username
            if not username:
                messages.error(request, 'Username is required.')
                return render(request, 'posts/login.html', {'google_oauth2_client_id': client_id})
                
            if len(username) < 3:
                messages.error(request, 'Username must be at least 3 characters long.')
                return render(request, 'posts/login.html', {'google_oauth2_client_id': client_id})
            
            try:
                # Create new user
                user = User.objects.create_user(username=username, email=email, password=password)
                # Log them in with the correct backend
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                logger.info(f"New user {username} registered and logged in")
                messages.success(request, 'Account created successfully!')
                return redirect('home')
            except IntegrityError as e:
                if 'username' in str(e):
                    messages.error(request, 'Username already exists. Please choose a different username.')
                elif 'email' in str(e):
                    messages.error(request, 'Email already exists. Please use a different email.')
                else:
                    messages.error(request, 'Username or email already exists.')
            except Exception as e:
                logger.error(f"Error creating user: {str(e)}")
                messages.error(request, 'Error creating account. Please try again.')
    
    # Get Google OAuth client ID for the template
    client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    if not client_id:
        logger.error("Google OAuth client ID is not configured")
        messages.warning(request, 'Google Sign-in is currently unavailable.')
    
    return render(request, 'posts/login.html', {
        'google_oauth2_client_id': client_id
    })

@login_required
def home_view(request):
    """Render the home page with news feed"""
    # Check if user is in admin group
    is_admin = request.user.groups.filter(name='Admin').exists()
    
    # Get user profile
    profile = request.user.profile
    
    return render(request, 'posts/home.html', {
        'user': request.user,
        'profile': profile,
        'is_admin': is_admin
    })

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

class PostLikeView(APIView):
    """Handle likes for a specific post"""
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """Get likes for a post"""
        post = get_object_or_404(Post, pk=pk)
        likes = Like.objects.filter(post=post)
        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        """Like a post"""
        post = get_object_or_404(Post, pk=pk)
        
        data = {
            'user': request.user.id,
            'post': post.id
        }
        
        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            like = serializer.save()
            return Response(
                LikeSerializer(like).data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
        
    def delete(self, request, pk):
        """Unlike a post"""
        post = get_object_or_404(Post, pk=pk)
        like = get_object_or_404(Like, user=request.user, post=post)
        like.delete()
        
        return Response(
            {"message": "Post unliked successfully"},
            status=status.HTTP_200_OK
        )

class FeedPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 100

from rest_framework.generics import ListAPIView

class NewsFeedView(ListAPIView):
    """Get personalized news feed for authenticated user"""
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = PostSerializer
    pagination_class = FeedPagination
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def get_queryset(self):
        """Get filtered queryset based on request parameters"""
        try:
            # Get query parameters
            show_followed = self.request.query_params.get('followed', 'false').lower() == 'true'
            show_liked = self.request.query_params.get('liked', 'false').lower() == 'true'
            post_type = self.request.query_params.get('post_type', None)
            
            # Start with all posts
            queryset = Post.objects.all()
            
            # Apply filters
            if show_followed:
                followed_users = UserFollow.objects.filter(follower=self.request.user).values_list('followed', flat=True)
                queryset = queryset.filter(author__in=followed_users)
                
            if show_liked:
                liked_posts = Like.objects.filter(user=self.request.user).values_list('post', flat=True)
                queryset = queryset.filter(id__in=liked_posts)
                
            if post_type:
                queryset = queryset.filter(post_type=post_type)
            
            # Sort by most recent and optimize with prefetch
            return queryset.order_by('-created_at')\
                .select_related('author')\
                .prefetch_related('comments', 'likes')
                
        except Exception as e:
            logger = LoggerSingleton().get_logger()
            logger.error(f"Error in NewsFeedView.get_queryset: {str(e)}")
            raise
    
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger = LoggerSingleton().get_logger()
            logger.error(f"Error in NewsFeedView.list: {str(e)}")
            raise

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_comments(request, post_id):
    """Handle comments for a specific post"""
    post = get_object_or_404(Post, pk=post_id)
    
    if request.method == 'GET':
        comments = Comment.objects.filter(post=post).order_by('created_at')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
        
    elif request.method == 'POST':
        try:
            # Create the comment
            comment_data = {
                'text': request.data.get('text', ''),  # Get text from request
                'author': request.user.id,
                'post': post.id
            }
            serializer = CommentSerializer(data=comment_data)
            if serializer.is_valid():
                comment = serializer.save()
                return Response(
                    CommentSerializer(comment).data, 
                    status=status.HTTP_201_CREATED
                )
            
            # Return detailed validation errors
            return Response(
                {'error': 'Invalid comment data', 'details': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger = LoggerSingleton().get_logger()
            logger.error(f"Error creating comment: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class UserProfileView(APIView):
    """Handle user profile operations"""
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, username=None):
        """Get user profile data"""
        try:
            if username is None:
                user = request.user
            else:
                user = User.objects.get(username=username)
            
            profile = user.profile
            serializer = UserProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger = LoggerSingleton().get_logger()
            logger.error(f"Error in UserProfileView.get: {str(e)}")
            return Response(
                {'error': 'An error occurred while fetching the profile'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def post(self, request, username=None):
        """Update user profile data"""
        try:
            if username and username != request.user.username:
                return Response(
                    {"error": "Cannot update other user's profile"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
                
            user = request.user
            profile = user.profile
            data = request.data
            
            # Update basic user fields
            if 'full_name' in data:
                names = data['full_name'].split(' ', 1)
                user.first_name = names[0]
                user.last_name = names[1] if len(names) > 1 else ''
                user.save()
                
            # Update profile fields
            if 'bio' in data:
                profile.bio = data['bio']
            if 'location' in data:
                profile.location = data['location']
            if 'website' in data:
                profile.website = data['website']

            # Handle media files
            if 'avatar' in request.FILES:
                profile.avatar = request.FILES['avatar']
            if 'cover_photo' in request.FILES:
                profile.cover_photo = request.FILES['cover_photo']
                
            profile.save()
            
            # Return updated profile data
            serializer = UserProfileSerializer(profile, context={'request': request})
            return Response(serializer.data)
            
        except Exception as e:
            logger = LoggerSingleton().get_logger()
            logger.error(f"Error in UserProfileView.post: {str(e)}")
            return Response(
                {'error': 'An error occurred while updating the profile'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserProfilePostsView(APIView):
    """Handle profile-specific post operations"""
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, username):
        """Get user posts based on tab query parameter (posts/media/liked)"""
        try:
            user = get_object_or_404(User, username=username)
            tab = request.GET.get('tab', 'posts')
            
            if tab == 'posts':
                posts = Post.objects.filter(author=user)
            elif tab == 'media':
                posts = Post.objects.filter(author=user, post_type__in=['image', 'video'])
            elif tab == 'liked':
                liked_posts = Like.objects.filter(user=user).values_list('post', flat=True)
                posts = Post.objects.filter(id__in=liked_posts)
            else:
                return Response({"error": "Invalid tab"}, status=status.HTTP_400_BAD_REQUEST)
            
            posts = posts.order_by('-created_at')
            serializer = PostSerializer(posts, many=True, context={'request': request})
            return Response({'results': serializer.data})
            
        except Exception as e:
            logger = LoggerSingleton().get_logger()
            logger.error(f"Error in UserProfilePostsView.get: {str(e)}")
            return Response(
                {'error': 'An error occurred while fetching posts'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserFollowView(APIView):
    """Handle follow/unfollow operations"""
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, username):
        """Follow a user"""
        target_user = get_object_or_404(User, username=username)
        
        if target_user == request.user:
            return Response({"error": "Cannot follow yourself"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Create follow relationship if it doesn't exist    
        UserFollow.objects.get_or_create(follower=request.user, followed=target_user)
        
        # Get updated followers count
        followers_count = UserFollow.objects.filter(followed=target_user).count()
            
        return Response({
            'success': True,
            'followers_count': followers_count
        })

    def delete(self, request, username):
        """Unfollow a user"""
        target_user = get_object_or_404(User, username=username)
        
        if target_user == request.user:
            return Response({"error": "Cannot unfollow yourself"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Remove follow relationship if it exists
        UserFollow.objects.filter(follower=request.user, followed=target_user).delete()
        
        # Get updated followers count  
        followers_count = UserFollow.objects.filter(followed=target_user).count()
            
        return Response({
            'success': True,
            'followers_count': followers_count
        })

class APIDocsView(APIView):
    """API Documentation view"""
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
            },
            "likes": {
                "like_post": "/api/posts/{id}/like/ [POST]",
                "unlike_post": "/api/posts/{id}/like/ [DELETE]"
            }
        }
    })
