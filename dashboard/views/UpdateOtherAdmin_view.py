from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from ..models import AdminUser
from django.conf import settings
import bcrypt
import jwt
from datetime import datetime
from .ContactAdmin_view import update_loggedin_email

SECRET_KEY = settings.SECRET_KEY

@api_view(['PATCH'])
def update_other_admin(request, id):
    try:
        admin_user = AdminUser.objects.get(id=id)
    except AdminUser.DoesNotExist:
        return Response({"error": "Admin user not found"}, status=status.HTTP_404_NOT_FOUND)

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
    if 'email' in request.data and request.data['email'] != admin_user.email:
        return Response({"error": "Email cannot be changed"}, status=status.HTTP_400_BAD_REQUEST)

    # Update other fields
    admin_user.name = request.data.get('username', admin_user.name)

    # Hash password if provided
    if 'password' in request.data and request.data['password']:
        password = request.data['password']
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_user.password = hashed_password

    admin_user.status = request.data.get('status', admin_user.status)
    admin_user.updated_at = datetime.now()
    admin_user.updated_by = updated_by

    email = request.data.get('email')  # Get the email from request data
    name = request.data.get('name')    # Get the name from request data

    # If password is updated, pass it too
    email_password = password if 'password' in request.data else None

    # Call the function with necessary arguments
    update_loggedin_email(name, email, email_password)

    try:
        admin_user.save(update_fields=['name', 'password', 'status', 'updated_at', 'updated_by'])
        return Response({"message": "Admin user updated successfully!"}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
