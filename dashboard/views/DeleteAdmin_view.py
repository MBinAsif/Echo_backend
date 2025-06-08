from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import jwt
from django.conf import settings
from ..models import AdminUser
from .ContactAdmin_view import delete_admin as notify_admin_deletion



@api_view(['DELETE'])
def delete_admin(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({"error": "Authorization token is missing or invalid"}, status=status.HTTP_400_BAD_REQUEST)

    token = auth_header.split(' ')[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        logged_in_admin_id = payload.get('user_id')

        if not logged_in_admin_id:
            return Response({"error": "Invalid token payload"}, status=status.HTTP_401_UNAUTHORIZED)

        logged_in_admin = AdminUser.objects.filter(id=logged_in_admin_id).first()
        if not logged_in_admin:
            return Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)

        target_admin_id = request.data.get('admin_id')  # Use "admin_id" key like in your frontend

        if not target_admin_id:
            return Response({"error": "Admin ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        target_user = AdminUser.objects.filter(id=target_admin_id).first()
        if not target_user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if logged_in_admin.id == target_user.id:
            return Response({"error": "You cannot delete yourself"}, status=status.HTTP_400_BAD_REQUEST)
        
        deleted_user_email = target_user.email
        notify_admin_deletion(deleted_user_email)

        target_user.delete()

        return Response({"message": f"User with ID {target_admin_id} deleted successfully"}, status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

