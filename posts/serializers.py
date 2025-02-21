import json
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Like, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.SerializerMethodField()
    posts_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ['username', 'full_name', 'bio', 'location', 'website', 
                 'avatar_url', 'cover_url', 'posts_count', 'followers_count', 
                 'following_count', 'is_following']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_posts_count(self, obj):
        return obj.user.posts.count()

    def get_followers_count(self, obj):
        return obj.user.followers.count()

    def get_following_count(self, obj):
        return obj.user.following.count()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return obj.user.followers.filter(follower=request.user).exists()

    def get_avatar_url(self, obj):
        request = self.context.get('request')
        if obj.avatar and request:
            return request.build_absolute_uri(obj.avatar.url)
        return None

    def get_cover_url(self, obj):
        request = self.context.get('request')
        if obj.cover_photo and request:
            return request.build_absolute_uri(obj.cover_photo.url)
        return None

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['date_joined']

class LikeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'user_username', 'post', 'created_at']
        read_only_fields = ['created_at']
        
    def validate(self, data):
        # Check if user already liked the post
        if Like.objects.filter(user=data['user'], post=data['post']).exists():
            raise serializers.ValidationError("User has already liked this post.")
        return data

class PostSerializer(serializers.ModelSerializer):
    comments = serializers.StringRelatedField(many=True, read_only=True)
    author_username = serializers.CharField(source='author.username', read_only=True)
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    def get_is_following(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or obj.author == request.user:
            return False
        return obj.author.followers.filter(follower=request.user).exists()

    def get_can_edit(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        # User can edit if they're the author or an admin
        return (obj.author == request.user or 
                request.user.groups.filter(name='Admin').exists())

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_username', 'created_at', 'comments', 
                 'like_count', 'comment_count', 'post_type', 'metadata', 'media', 'media_url',
                 'can_edit', 'is_following']
        read_only_fields = ['created_at', 'media_url']
        
    def get_media_url(self, obj):
        if obj.media:
            return self.context['request'].build_absolute_uri(obj.media.url)
        return None

    def validate(self, data):
        post_type = data.get('post_type', 'text')
        
        # Skip author validation since it's added in the view
        if 'author' in data and not User.objects.filter(id=data['author'].id).exists():
            raise serializers.ValidationError({"author": "Author not found."})

        # Handle metadata validation
        metadata = data.get('metadata')
        if metadata is not None:
            # If metadata is a string (from form data), try to parse it
            if isinstance(metadata, str):
                try:
                    parsed = json.loads(metadata)
                    if not isinstance(parsed, dict):
                        raise serializers.ValidationError({"metadata": "Value must be a valid JSON object"})
                    metadata = parsed
                except json.JSONDecodeError:
                    raise serializers.ValidationError({"metadata": "Value must be a valid JSON object"})
            elif not isinstance(metadata, dict):
                raise serializers.ValidationError({"metadata": "Value must be a JSON object"})
            
            data['metadata'] = metadata

        # Media validation is handled in the model's clean method
        return data

    def create(self, validated_data):
        # Create post instance (media is handled in the view)
        return Post.objects.create(**validated_data)
        
    def get_like_count(self, obj):
        return obj.likes.count()
        
    def get_comment_count(self, obj):
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    text = serializers.CharField(required=True, allow_blank=False, error_messages={
        'required': 'Comment text is required.',
        'blank': 'Comment cannot be empty.'
    })
    
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'author_username', 'post', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, data):
        if not data.get('text', '').strip():
            raise serializers.ValidationError({'text': 'Comment cannot be empty.'})
        return data
