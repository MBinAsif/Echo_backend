from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import jwt
from django.conf import settings
from ..models import User  # Assuming you have a User model
from .ContactAdmin_view import delete_user as notify_user_deletion


@api_view(['DELETE'])
def delete_user(request):
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return Response({"error": "Authorization token is missing or invalid"}, status=status.HTTP_400_BAD_REQUEST)

    token = auth_header.split(' ')[1]

    try:

        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        logged_in_admin_id = payload.get('user_id')

        if not logged_in_admin_id:
            return Response({"error": "Invalid token payload"}, status=status.HTTP_401_UNAUTHORIZED)



        target_user_id = request.data.get('user_id')  # Get user_id from the request body

        if not target_user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        target_user = User.objects.filter(id=target_user_id).first()
        if not target_user:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        deleted_user_email = target_user.email
        notify_user_deletion(deleted_user_email)
        target_user.delete()


        return Response({"message": f"User with ID {target_user_id} deleted successfully"}, status=status.HTTP_200_OK)

    except jwt.ExpiredSignatureError:
        return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
