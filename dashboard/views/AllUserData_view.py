from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
import jwt
from django.conf import settings
from ..models import User, AdminUser, Alarm, BatteryMonitoring, BeltTracking
from django.db.models import CharField, F, Value
from django.db.models.functions import Concat


def authenticate_admin(request):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, Response({"error": "Authorization token is missing or invalid"}, status=status.HTTP_400_BAD_REQUEST)
    
    token = auth_header.split(' ')[1]
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        logged_in_admin_id = payload.get('user_id')
        if not logged_in_admin_id:
            return None, Response({"error": "Invalid token payload"}, status=status.HTTP_401_UNAUTHORIZED)
        
        logged_in_admin = AdminUser.objects.filter(id=logged_in_admin_id).first()
        if not logged_in_admin:
            return None, Response({"error": "Admin not found"}, status=status.HTTP_404_NOT_FOUND)
        
        return logged_in_admin, None
    except jwt.ExpiredSignatureError:
        return None, Response({"error": "Token has expired"}, status=status.HTTP_401_UNAUTHORIZED)
    except jwt.InvalidTokenError:
        return None, Response({"error": "Invalid token"}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return None, Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_all_users(request):
    logged_in_admin, error_response = authenticate_admin(request)
    if error_response:
        return error_response
    
    users = User.objects.values('id', 'name', 'email', 'status', 'created_at', 'last_login', 'updated_at')
    return Response({"message": "Users retrieved successfully", "users": list(users)}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_all_alarms(request):
    logged_in_admin, error_response = authenticate_admin(request)
    if error_response:
        return error_response
    
    # Join with User table and format the output with explicit output field
    alarms = Alarm.objects.annotate(
        user_info=Concat(F('user__name'), Value(' / '), F('user_id'), output_field=CharField())  # Explicit CharField output
    ).values('id', 'user_info', 'alarm_time', 'status', 'created_at', 'updated_at')
    return Response({"message": "Alarms retrieved successfully", "alarms": list(alarms)}, status=status.HTTP_200_OK)

from django.db.models import F, Value, CharField
from django.db.models.functions import Concat

@api_view(['GET'])
def get_all_battery_monitoring(request):
    logged_in_admin, error_response = authenticate_admin(request)
    if error_response:
        return error_response

    # Join with User table and format the output with explicit CharField
    battery_data = BatteryMonitoring.objects.annotate(
        user_info=Concat(F('user__name'), Value(' / '), F('user_id'), output_field=CharField())
    ).values('id', 'user_info', 'threshold', 'updated_at')

    return Response({"message": "Battery monitoring data retrieved successfully", "battery_data": list(battery_data)}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_all_belt_tracking(request):
    logged_in_admin, error_response = authenticate_admin(request)
    if error_response:
        return error_response

    # Join with User table and format the output with explicit CharField
    belt_tracking = BeltTracking.objects.annotate(
        user_info=Concat(F('user__name'), Value(' / '), F('user_id'), output_field=CharField())
    ).values('id', 'user_info', 'belt_name', 'mac_address', 'uuid', 'last_connected', 'device_name', 'status')

    return Response({"message": "Belt tracking data retrieved successfully", "belt_tracking": list(belt_tracking)}, status=status.HTTP_200_OK)
