# utils/tokenvalidation.py
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

def validate_token(refresh_token):
    """
    Validate the refresh token and decode it to extract the payload.
    Raises AuthenticationFailed if the token is invalid or expired.
    """
    try:
        # Decode the token using your secret key
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload  # Return the decoded payload (contains user info, etc.)
    
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")
