from django.core.exceptions import ValidationError
from posts.models import Post
from singletons.config_manager import ConfigManager
from singletons.logger_singleton import LoggerSingleton

class PostFactory:
    @staticmethod
    def create_post(author, post_type, title, content='', metadata=None):
        """
        Factory method to create different types of posts with proper validation
        """
        logger = LoggerSingleton().get_logger()
        config = ConfigManager()
        
        try:
            # Validate post type
            if post_type not in dict(Post.POST_TYPES):
                raise ValidationError(f"Invalid post type. Allowed types: {', '.join(dict(Post.POST_TYPES).keys())}")

            # Initialize metadata if None
            metadata = metadata or {}

            # Validate and prepare metadata based on post type
            if post_type == 'image':
                if 'file_size' not in metadata:
                    raise ValidationError("Image posts require 'file_size' in metadata")
                if metadata['file_size'] > config.get_setting('MAX_FILE_SIZE'):
                    raise ValidationError(f"File size exceeds maximum limit of {config.get_setting('MAX_FILE_SIZE')} bytes")
                
            elif post_type == 'video':
                if 'duration' not in metadata:
                    raise ValidationError("Video posts require 'duration' in metadata")
                if not isinstance(metadata['duration'], (int, float)) or metadata['duration'] <= 0:
                    raise ValidationError("Video duration must be a positive number")

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
    def create_image_post(author, title, content, file_size):
        """Convenience method for creating image posts"""
        return PostFactory.create_post(
            author=author,
            post_type='image',
            title=title,
            content=content,
            metadata={'file_size': file_size}
        )

    @staticmethod
    def create_video_post(author, title, content, duration):
        """Convenience method for creating video posts"""
        return PostFactory.create_post(
            author=author,
            post_type='video',
            title=title,
            content=content,
            metadata={'duration': duration}
        )
