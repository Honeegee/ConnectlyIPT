class ConfigManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ConfigManager, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.settings = {
            "DEFAULT_PAGE_SIZE": 20,
            "ENABLE_ANALYTICS": True,
            "RATE_LIMIT": 100,
            "MAX_POST_LENGTH": 5000,
            "MAX_COMMENT_LENGTH": 1000,
            "ALLOWED_POST_TYPES": ["text", "image", "video"],
            "MAX_FILE_SIZE": 10 * 1024 * 1024  # 10MB
        }

    def get_setting(self, key):
        return self.settings.get(key)

    def set_setting(self, key, value):
        self.settings[key] = value
        
    def get_all_settings(self):
        return self.settings.copy()  # Return a copy to prevent direct modification
