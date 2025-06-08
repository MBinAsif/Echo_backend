from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from ..models import User  # Change AdminUser to User
from django.conf import settings
import bcrypt
import jwt
from datetime import datetime
from .ContactAdmin_view import update_OtherUser_email

SECRET_KEY = settings.SECRET_KEY

@api_view(['PATCH'])
def update_other_user(request, id):
    try:
        user = User.objects.get(id=id)  # Fetch the user instead of AdminUser
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    # Extract updated_by from refresh_token
    token = request.headers.get('Authorization', None)
    if token and token.startswith('Bearer '):
        token = token.split(' ')[1]
        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            updated_by = decoded_token.get('name', 'Unknown')
        except jwt.ExpiredSignatureError:
            return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        updated_by = 'Unknown'

    # Check if email is in request and if it is different from the current email
    if 'email' in request.data and request.data['email'] != user.email:
        return Response({"error": "Email cannot be changed"}, status=status.HTTP_400_BAD_REQUEST)

    # Update other fields
    user.name = request.data.get('username', user.name)  # Change 'username' to 'name' or your actual field name

    # Hash password if provided
    if 'password' in request.data and request.data['password']:
        password = request.data['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user.password = hashed_password

    user.status = request.data.get('status', user.status)
    user.updated_at = datetime.now()
    user.updated_by = updated_by

    email = request.data.get('email')  # Get the email from request data
    name = request.data.get('name')    # Get the name from request data

    # If password is updated, pass it too
    email_password = password if 'password' in request.data else None

    # Call the function with necessary arguments
    update_OtherUser_email(name, email, email_password)

    try:
        user.save(update_fields=['name', 'password', 'status', 'updated_at', 'updated_by'])
        return Response({"message": "User updated successfully!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
