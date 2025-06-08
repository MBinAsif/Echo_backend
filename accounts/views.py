# echotrail_backend/accounts/views.py

# accounts/views.py
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .models import User
# accounts/views.py
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from .models import User
from .serializers import (
    UserRegisterSerializer,
    CustomTokenRefreshSerializer  
)
from rest_framework_simplejwt.views import TokenRefreshView  

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

class UserRegisterView(APIView):  
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)  
        if serializer.is_valid():
            user = serializer.save()
            # Optionally return tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                # Create JWT tokens
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token
                
                # Update last login
                from django.utils import timezone
                user.last_login = timezone.now()
                user.save()
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(access),
                    'user': {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'status': user.status
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except User.DoesNotExist:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)

# Also create a profile view
class UserProfileView(APIView):
    def get(self, request):
        # Extract token and get user
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return Response({'error': 'Authentication required'}, status=401)
        
        token = auth_header.split(' ')[1]
        
        try:
            from rest_framework_simplejwt.tokens import AccessToken
            access_token = AccessToken(token)
            user_id = access_token.payload.get('user_id')
            user = User.objects.get(id=user_id)
            
            return Response({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'status': user.status,
                'created_at': user.created_at
            })
            
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=401)
        
