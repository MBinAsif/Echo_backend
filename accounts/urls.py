# accounts/urls.py
from django.urls import path
from .views import (
    UserRegisterView,
    UserLoginView,
    UserProfileView,
    CustomTokenRefreshView
)

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='user_register'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]