from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..models import AdminUser
import bcrypt
from .ContactAdmin_view import create_admin

@api_view(['POST'])
def register_admin(request):
    isCreated = None  # Initialize as None for unknown errors
    
    try:
        name = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        email_password = password

        if not name or not email or not password:
            return Response({"error": "All fields are required"}, status=400)

        if AdminUser.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists"}, status=400)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        admin_user = AdminUser(name=name, email=email, password=hashed_password, status="inactive")
        admin_user.save()

        create_admin(name, email, email_password)

        return Response({"message": "Admin registered successfully"}, status=201)
    
    except Exception as e:
        return Response({"error": str(e)}, status=500)
