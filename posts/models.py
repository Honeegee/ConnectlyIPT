from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from singletons.config_manager import ConfigManager

class Post(models.Model):
    POST_TYPES = [
        ('text', 'Text Post'),
        ('image', 'Image Post'),
        ('video', 'Video Post'),
    ]
    
    title = models.CharField(max_length=200, null=True, blank=True, default="Untitled Post")
    content = models.TextField()
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')
    metadata = models.JSONField(null=True, blank=True)

    def clean(self):
        config = ConfigManager()
        
        # Validate post length
        if len(self.content) > config.get_setting('MAX_POST_LENGTH'):
            raise ValidationError('Post content exceeds maximum length')
            
        # Validate post type
        if self.post_type not in dict(self.POST_TYPES):
            raise ValidationError('Invalid post type')
            
        # Validate metadata based on post type
        if self.post_type == 'image':
            if not self.metadata or 'file_size' not in self.metadata:
                raise ValidationError('Image posts require file size metadata')
            if self.metadata['file_size'] > config.get_setting('MAX_FILE_SIZE'):
                raise ValidationError('File size exceeds maximum limit')
                
        if self.post_type == 'video':
            if not self.metadata or 'duration' not in self.metadata:
                raise ValidationError('Video posts require duration metadata')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.post_type} post by {self.author.username} at {self.created_at}"

class Like(models.Model):
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Prevent multiple likes from same user

    def __str__(self):
        return f"Like by {self.user.username} on Post {self.post.id}"

class UserFollow(models.Model):
    follower = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')

    def __str__(self):
        return f"{self.follower.username} follows {self.followed.username}"

class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"
