from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from datetime import timedelta
from ..models import AdminUser
import jwt
from django.conf import settings
from .ContactAdmin_view import login_email


@api_view(['POST'])
def admin_login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    try:
        admin_user = AdminUser.objects.filter(email=email).first()

        if admin_user is None or not admin_user.check_password(password):
            return Response({"error": "Incorrect Username or Password"}, status=status.HTTP_401_UNAUTHORIZED)

        # Update login time & status
        admin_user.last_login = timezone.now()
        admin_user.status = "active"
        admin_user.save()

        # Generate Refresh Token
        refresh_payload = {
            'user_id': admin_user.id,
            'name': admin_user.name,  
            'email': admin_user.email,
            'exp': int((timezone.now() + timedelta(hours=1)).timestamp())  # Ensure integer timestamp
        }
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

        login_email(email)

        # Prepare response with success message
        response = Response({
            "message": "Login successful",  # Added success message
            "refresh_token": refresh_token
        }, status=status.HTTP_200_OK)
        
        return response

    except Exception as e:
        return Response({"error": "Internal Server Error", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
