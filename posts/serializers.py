import json
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Like

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
                 'can_edit']
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
    content = serializers.CharField(source='text', required=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'author_username', 'post', 'created_at']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        validated_data['text'] = validated_data.pop('content')
        return Comment.objects.create(**validated_data)
