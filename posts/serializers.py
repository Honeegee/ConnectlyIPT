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

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'author_username', 'created_at', 'comments', 'like_count', 'comment_count', 'post_type', 'metadata']
        read_only_fields = ['created_at']

    def validate_author(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value
        
    def get_like_count(self, obj):
        return obj.likes.count()
        
    def get_comment_count(self, obj):
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.CharField(source='author.username', read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'author_username', 'post', 'created_at']
        read_only_fields = ['created_at']

    def validate_post(self, value):
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value

    def validate_author(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value
