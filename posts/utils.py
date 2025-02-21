from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.http import Http404

def custom_exception_handler(exc, context):
    """Custom exception handler for REST framework that handles common Django exceptions."""
    
    # First try default REST framework handler
    response = exception_handler(exc, context)
    
    if response is not None:
        return response
        
    # Handle Django exceptions that REST framework doesn't catch
    if isinstance(exc, ValidationError):
        return Response(
            {'error': str(exc)},
            status=status.HTTP_400_BAD_REQUEST
        )
    elif isinstance(exc, Http404):
        return Response(
            {'error': 'Not found'},
            status=status.HTTP_404_NOT_FOUND
        )
        
    # Handle any other exceptions
    return Response(
        {'error': 'An unexpected error occurred'},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
