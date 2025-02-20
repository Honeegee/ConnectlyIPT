from django.core.exceptions import ValidationError
from posts.models import Post
from singletons.config_manager import ConfigManager
from singletons.logger_singleton import LoggerSingleton

class PostFactory:
    @staticmethod
    def create_post(author, post_type, title, content='', metadata=None, media=None):
        """
        Factory method to create different types of posts with proper validation
        """
        logger = LoggerSingleton().get_logger()
        config = ConfigManager()

        # Initialize metadata if None
        metadata = metadata or {}
        
        try:
            # Validate post type
            if post_type not in dict(Post.POST_TYPES):
                raise ValidationError(f"Invalid post type. Allowed types: {', '.join(dict(Post.POST_TYPES).keys())}")

            # Validate media requirements based on post type
            if post_type in ['image', 'video']:
                if not media:
                    raise ValidationError(f"{post_type.capitalize()} post requires a media file")
                
                max_size = config.get_setting('MAX_FILE_SIZE', 10485760)  # Default 10MB
                if hasattr(media, 'size') and media.size > max_size:
                    raise ValidationError(f"File size exceeds maximum limit of {max_size/1024/1024:.1f}MB")

                # Update metadata with file info
                metadata.update({
                    'file_size': media.size if hasattr(media, 'size') else 0,
                    'file_type': media.name.split('.')[-1].lower() if hasattr(media, 'name') else ''
                })

            # Create and validate the post
            post = Post(
                title=title,
                content=content,
                author=author,
                post_type=post_type,
                metadata=metadata
            )
            
            # This will run all model validations
            post.full_clean()
            post.save()

            # Save media after post is created
            if media:
                post.media = media
                post.save()

            logger.info(f"Created {post_type} post: {post.id} by {author.username}")
            return post

        except ValidationError as e:
            logger.error(f"Post creation failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in post creation: {str(e)}")
            raise ValidationError(f"Post creation failed: {str(e)}")

    @staticmethod
    def create_text_post(author, title, content):
        """Convenience method for creating text posts"""
        return PostFactory.create_post(
            author=author,
            post_type='text',
            title=title,
            content=content
        )

    @staticmethod
    def create_image_post(author, title, content, media):
        """Convenience method for creating image posts"""
        return PostFactory.create_post(
            author=author,
            post_type='image',
            title=title,
            content=content,
            media=media
        )

    @staticmethod
    def create_video_post(author, title, content, media):
        """Convenience method for creating video posts"""
        return PostFactory.create_post(
            author=author,
            post_type='video',
            title=title,
            content=content,
            media=media
        )
