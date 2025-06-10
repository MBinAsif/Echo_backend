from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from accounts.models import User
import bcrypt
from .ContactAdmin_view import create_user

@api_view(['POST'])
def register_user(request):
    try:
        name = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        email_password = password

        # Validate the required fields
        if not name or not email or not password:
            return Response({"error": "All fields are required"}, status=400)

        # Check if the user with the same email already exists
        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists"}, status=400)

        # Hash the password before storing
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create the user instance and save it
        user = User(name=name, email=email, password=hashed_password, status="inactive")  # status set to 'inactive' by default
        user.save()

        create_user(name, email, email_password)

        return Response({"message": "User registered successfully"}, status=201)
    
    except Exception as e:
        return Response({"error": str(e)}, status=500)
