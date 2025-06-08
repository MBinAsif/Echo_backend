from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import jwt
from django.conf import settings
from ..models import AdminUser

@api_view(['GET'])
def get_all_admins(request):
    # Extract the authorization token from the headers
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({"error": "Authorization token is missing or invalid"}, status=status.HTTP_400_BAD_REQUEST)

    token = auth_header.split(' ')[1]

    try:
        # Decode the token to extract the admin user details
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        logged_in_admin_id = payload.get('user_id')

        if not logged_in_admin_id:
            return Response({"error": "Invalid token payload"}, status=status.HTTP_401_UNAUTHORIZED)

        # Retrieve the logged-in admin user
        logged_in_admin = AdminUser.objects.filter(id=logged_in_admin_id).first()
        if not logged_in_admin:
            return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

        # Retrieve all admins excluding the current logged-in user
        admins = AdminUser.objects.exclude(id=logged_in_admin_id).values('id','name', 'email','status', 'created_at','last_login','updated_at', 'updated_by')

        # Return all admins except the logged-in admin
        return Response({
            "message": "Admins retrieved successfully",
            "admins": list(admins)  # Convert queryset to list
        }, status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
    
    except jwt.InvalidTokenError:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
