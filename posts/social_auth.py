from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from google.oauth2 import id_token
from google.auth.transport import requests
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.conf import settings
from singletons.logger_singleton import LoggerSingleton

logger = LoggerSingleton().get_logger()

def verify_google_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            settings.GOOGLE_OAUTH2_KEY
        )
        
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')
            
        return idinfo
    except Exception as e:
        logger.error(f"Token verification failed: {str(e)}")
        return None

class GoogleOAuth2LoginView(APIView):
    """
    Handle Google OAuth2 login
    """
    permission_classes = [AllowAny]
    authentication_classes = []
    
    def post(self, request):
        try:
            # Get and validate token
            token = request.data.get('id_token')
            if not token:
                return Response(
                    {'error': 'ID token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Verify the token
            idinfo = verify_google_token(token)
            if not idinfo:
                return Response(
                    {'error': 'Invalid token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Get or create user
            email = idinfo['email']
            if not email.endswith('@mmdc.mcl.edu.ph'):
                return Response(
                    {'error': 'Only @mmdc.mcl.edu.ph email addresses are allowed'},
                    status=status.HTTP_403_FORBIDDEN
                )

            try:
                user = User.objects.get(email=email)
                logger.info(f"Existing user logged in: {email}")
            except User.DoesNotExist:
                # Create new user
                user = User.objects.create_user(
                    username=email.split('@')[0],
                    email=email,
                    first_name=idinfo.get('given_name', ''),
                    last_name=idinfo.get('family_name', '')
                )
                logger.info(f"Created new user: {email}")

            # Get or create token
            token, _ = Token.objects.get_or_create(user=user)
            
            # Log the user in
            login(request, user)
            
            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email,
                'username': user.username
            })

        except Exception as e:
            logger.error(f"Error in Google OAuth login: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class OAuthCompleteView(APIView):
    """
    OAuth completion endpoint
    Handles the OAuth callback and returns success/error message
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            logger.info(f"OAuth completed successfully for user: {request.user.email}")
            return Response({
                'message': 'Authentication successful',
                'user': request.user.username
            })
        
        logger.error("OAuth completion failed - user not authenticated")
        return Response(
            {'error': 'Authentication failed'}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
