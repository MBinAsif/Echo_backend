from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings
from datetime import timedelta
from bcrypt import hashpw, gensalt
from django.utils import timezone
from ..models import AdminUser
from .ContactAdmin_view import update_loggedin_email

@api_view(['PATCH'])
def update_loggedin_admin(request):
    try:
        auth_header = request.headers.get('Authorization')

        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({"error": "Authorization token is missing or invalid"}, status=status.HTTP_400_BAD_REQUEST)
        
        token = auth_header.split(' ')[1]

        # Decode the token to get the user ID and email
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload['user_id']
        token_email = payload['email']  # Extract the email from the token

        # Retrieve the user from the AdminUser table using the custom model
        user = AdminUser.objects.get(id=user_id)

        # Verify if the email in the token matches the email in the databas

        # Get the new data from the request
        name = request.data.get('name')
        email = request.data.get('email')
        password = request.data.get('newPassword')
        confirm_password = request.data.get('confirmPassword')  # Get confirmPassword from the request

        

        updated_fields = []

        if name and name != user.name:
            user.name = name  # Update the name
            updated_fields.append('name')


        if email != token_email and email != user.email: 
            return Response({"error": "Use your Current email. Email can't be Changed"}, status=status.HTTP_400_BAD_REQUEST)

        if password:
            # Check if new password matches confirm password
            if password != confirm_password:
                return Response({"error": "Password dosent matches"}, status=status.HTTP_400_BAD_REQUEST)
            #if password and confirm_password == user.password:
              #return Response({"error" : "Password Already in use. Try another Combination!"}, status=status.HTTP_400_BAD_REQUEST)
        
            email_password = password

            # Hash the new password before saving
            hashed_password = hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')
            user.password = hashed_password  # Update the password
            updated_fields.append('password')

        if updated_fields:
            # Save the user with updated data
            user.updated_at = timezone.now()
            user.updated_by = name
            user.save()

            # Reload user from the database to ensure it's persisted
            user.refresh_from_db()

            update_loggedin_email(name, email, email_password)
            
            # Generate a new refresh token with a longer expiration time
            refresh_payload = {
                'user_id': user.id,  # Correct user reference
                'name': user.name,
                'email': user.email,
                'exp': int((timezone.now() + timedelta(hours=1)).timestamp())  # Ensure integer timestamp
            }
            new_refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')



            # Respond with updated data and new refresh token
            return Response({
                "message": "Your credentials have been updated successfully",
                "refresh_token": new_refresh_token
            }, status=status.HTTP_200_OK)

        else:
            return Response({"error": "No changes made to the user information. Try again later"}, status=status.HTTP_400_BAD_REQUEST)

    except jwt.ExpiredSignatureError:
        return Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    except AdminUser.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
