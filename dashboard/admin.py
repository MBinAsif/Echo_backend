from django.contrib import admin
from .models import AdminUser, User, Alarm, BatteryMonitoring, BeltTracking

# AdminUser Model Admin
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'password', 'status', 'created_at', 'last_login', 'updated_at', 'updated_by')
    search_fields = ('name', 'email')
    list_filter = ('status',)

# User Model Admin
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'password', 'status', 'created_at', 'last_login', 'updated_at', 'updated_by')
    search_fields = ('name', 'email')
    list_filter = ('status',)

# Alarm Model Admin
class AlarmAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'alarm_time', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)

# Battery Monitoring Model Admin
class BatteryMonitoringAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'threshold', 'updated_at')

# Belt Tracking Model Admin
class BeltTrackingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'belt_name', 'mac_address', 'uuid', 'last_connected', 'device_name', 'status')
    list_filter = ('status',)

# Registering Models
admin.site.register(AdminUser, AdminUserAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Alarm, AlarmAdmin)
admin.site.register(BatteryMonitoring, BatteryMonitoringAdmin)
admin.site.register(BeltTracking, BeltTrackingAdmin)

