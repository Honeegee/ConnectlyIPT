import json
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from singletons.config_manager import ConfigManager
from django.core.files.uploadedfile import InMemoryUploadedFile

class Post(models.Model):
    POST_TYPES = [
        ('text', 'Text Post'),
        ('image', 'Image Post'),
        ('video', 'Video Post'),
    ]
    
    title = models.CharField(max_length=200, null=True, blank=True, default="Untitled Post")
    content = models.TextField()
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    media = models.FileField(upload_to='post_media/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')
    metadata = models.JSONField(null=True, blank=True)

    def clean(self):
        config = ConfigManager()
        
        # Handle metadata field
        if self.metadata is None or self.metadata == '':
            self.metadata = {}
        elif isinstance(self.metadata, str):
            try:
                # Try to parse the string as JSON
                parsed_metadata = json.loads(self.metadata)
                if not isinstance(parsed_metadata, dict):
                    raise ValidationError('Metadata must be a valid JSON object')
                self.metadata = parsed_metadata
            except json.JSONDecodeError:
                raise ValidationError('Metadata must be a valid JSON object')
        elif not isinstance(self.metadata, dict):
            raise ValidationError('Metadata must be a dictionary')

        # Validate post length
        if len(self.content) > config.get_setting('MAX_POST_LENGTH'):
            raise ValidationError('Post content exceeds maximum length')
            
        # Validate post type
        if self.post_type not in dict(self.POST_TYPES):
            raise ValidationError('Invalid post type')
                
        # Handle media validation based on post type
        if self.post_type in ['image', 'video']:
            if not self.media:
                raise ValidationError(f'{self.post_type.capitalize()} posts require a media file')
                
            # For new posts requiring media
            if not self.pk and not self.media:
                raise ValidationError(f'{self.post_type.capitalize()} posts require a media file')
            
            # Skip validation if no media is present (could be an update)
            if not self.media:
                return
            
            max_size = config.get_setting('MAX_FILE_SIZE')
            if hasattr(self.media, 'size') and self.media.size > max_size:
                raise ValidationError(f'File size exceeds maximum limit of {max_size/1024/1024:.1f}MB')
            
            # Initialize metadata dict if needed
            if self.metadata is None:
                self.metadata = {}

            # Add file metadata
            if hasattr(self.media, 'size'):
                file_info = {
                    'file_size': self.media.size,
                    'file_type': str(self.media.name).split('.')[-1].lower() if hasattr(self.media, 'name') else '',
                    'content_type': getattr(self.media, 'content_type', None)
                }
                self.metadata.update(file_info)
            
            if self.post_type == 'image':
                allowed_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.webp')
                if hasattr(self.media, 'name') and not str(self.media.name).lower().endswith(allowed_extensions):
                    raise ValidationError(f'Invalid image format. Please use: {", ".join(allowed_extensions)}')
                
            elif self.post_type == 'video':
                allowed_extensions = ('.mp4', '.mov', '.avi', '.wmv', '.webm')
                if hasattr(self.media, 'name') and not str(self.media.name).lower().endswith(allowed_extensions):
                    raise ValidationError(f'Invalid video format. Please use: {", ".join(allowed_extensions)}')
                    
                # Update metadata with video info if media has size attribute
                if hasattr(self.media, 'size'):
                    self.metadata.update({
                        'file_size': self.media.size,
                        'file_type': str(self.media.name).split('.')[-1].lower() if hasattr(self.media, 'name') else ''
                    })

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
