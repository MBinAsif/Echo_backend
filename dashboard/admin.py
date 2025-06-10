# dashboard/admin.py

from django.contrib import admin
from django.contrib.auth import get_user_model
from accounts.models import User, AdminUser  # Update with correct path
from accounts.models import Alarm, BatteryMonitoring, BeltTracking  # Import your models

User = get_user_model()


# ========== Custom Admin for User ==========

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'is_admin', 'status', 'created_at', 'last_login', 'updated_at')
    search_fields = ('name', 'email',)
    list_filter = ('is_admin', 'status',)
    readonly_fields = ('created_at', 'updated_at', 'last_login')


# ========== Optional: AdminUser Proxy Admin ==========

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'status', 'created_at', 'last_login', 'updated_at', 'updated_by')
    search_fields = ('name', 'email',)
    list_filter = ('status',)
    ordering = ('-created_at',)


# ========== Supporting Models Admins ==========

@admin.register(Alarm)
class AlarmAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'alarm_time', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('user__email',)


@admin.register(BatteryMonitoring)
class BatteryMonitoringAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'threshold', 'updated_at')
    search_fields = ('user__email',)


@admin.register(BeltTracking)
class BeltTrackingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'belt_name', 'mac_address', 'uuid', 'last_connected', 'device_name', 'status')
    list_filter = ('status',)
    search_fields = ('user__email', 'mac_address', 'device_name')