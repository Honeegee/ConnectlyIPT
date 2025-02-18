from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.contrib.auth.models import User
from singletons.logger_singleton import LoggerSingleton

logger = LoggerSingleton().get_logger()

def verify_google_token(token):
    """
    Verify the Google OAuth token and return user info
    """
    try:
        # Verify the token
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request(), 
            settings.GOOGLE_OAUTH2_KEY
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        email = idinfo['email']
        if not email.endswith('@mmdc.mcl.edu.ph'):
            raise ValueError('Only @mmdc.mcl.edu.ph email addresses are allowed')

        # Get user info from token
        user_info = {
            'email': email,
            'username': idinfo['email'].split('@')[0],  
            'first_name': idinfo.get('given_name', ''),
            'last_name': idinfo.get('family_name', '')
        }

        return user_info
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None

def get_or_create_user_from_google(user_info):
    """
    Get existing user or create new one from Google user info
    """
    try:
        # Try to get existing user
        user = User.objects.get(email=user_info['email'])
        logger.info(f"Found existing user: {user.email}")
        
    except User.DoesNotExist:
        # Create new user
        username = user_info['username']
        base_username = username
        counter = 1
        
        # Handle username conflicts
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=user_info['email'],
            first_name=user_info['first_name'],
            last_name=user_info['last_name']
        )
        logger.info(f"Created new user from Google OAuth: {user.email}")
    
    # Get or create token
    token, _ = Token.objects.get_or_create(user=user)
    
    return user, token.key

def handle_google_token(token):
    """
    Main function to handle Google OAuth token
    """
    user_info = verify_google_token(token)
    if user_info:
        user, token = get_or_create_user_from_google(user_info)
        return {
            'token': token,
            'user_id': user.id,
            'email': user.email,
            'username': user.username
        }
    return None
