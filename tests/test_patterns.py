from django.test import TestCase
from django.contrib.auth.models import User
from posts.models import Post
from singletons.config_manager import ConfigManager
from singletons.logger_singleton import LoggerSingleton
from factories.post_factory import PostFactory

class DesignPatternsTest(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_config_manager_singleton(self):
        """Test that ConfigManager maintains single instance"""
        config1 = ConfigManager()
        config2 = ConfigManager()
        
        # Test same instance
        self.assertIs(config1, config2)
        
        # Test shared state
        config1.set_setting('TEST_KEY', 'test_value')
        self.assertEqual(config2.get_setting('TEST_KEY'), 'test_value')

    def test_logger_singleton(self):
        """Test that LoggerSingleton maintains single instance"""
        logger1 = LoggerSingleton()
        logger2 = LoggerSingleton()
        
        # Test same instance
        self.assertIs(logger1, logger2)
        
        # Test logging functionality
        logger = logger1.get_logger()
        logger.info("Test log message")

    def test_post_factory(self):
        """Test PostFactory creates different types of posts"""
        # Test text post
        text_post = PostFactory.create_text_post(
            author=self.user,
            title="Test Text Post",
            content="This is a test post"
        )
        self.assertEqual(text_post.post_type, 'text')
        self.assertIsNone(text_post.metadata)

        # Test image post
        image_post = PostFactory.create_image_post(
            author=self.user,
            title="Test Image Post",
            content="Image description",
            file_size=1024
        )
        self.assertEqual(image_post.post_type, 'image')
        self.assertEqual(image_post.metadata['file_size'], 1024)

        # Test video post
        video_post = PostFactory.create_video_post(
            author=self.user,
            title="Test Video Post",
            content="Video description",
            duration=120
        )
        self.assertEqual(video_post.post_type, 'video')
        self.assertEqual(video_post.metadata['duration'], 120)

    def test_post_factory_validation(self):
        """Test PostFactory validation rules"""
        config = ConfigManager()
        max_file_size = config.get_setting('MAX_FILE_SIZE')

        # Test file size validation
        with self.assertRaises(Exception):
            PostFactory.create_image_post(
                author=self.user,
                title="Large Image",
                content="Too large",
                file_size=max_file_size + 1
            )

        # Test invalid post type
        with self.assertRaises(Exception):
            PostFactory.create_post(
                author=self.user,
                post_type='invalid',
                title="Invalid Post",
                content="This should fail"
            )

        # Test missing required metadata
        with self.assertRaises(Exception):
            PostFactory.create_post(
                author=self.user,
                post_type='video',
                title="Invalid Video",
                content="Missing duration"
            )
