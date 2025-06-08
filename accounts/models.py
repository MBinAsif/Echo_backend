# echotrail_backend\accounts\models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=10, default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    # Fix the conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='regular_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='regular_users',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return f"{self.name} / {self.id}"
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

class AdminUser(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=10, default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    # Fix the conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='admin_users',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='admin_users',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

    def __str__(self):
        return self.name or self.email

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"

# Your other models remain the same
class Alarm(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    alarm_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Alarm {self.id} - {self.user.id if self.user else 'No User'} ({self.user.name if self.user else 'No Name'})"

class BatteryMonitoring(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    threshold = models.IntegerField(default=25)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Battery {self.id} - {self.user.id if self.user else 'No User'} ({self.user.name if self.user else 'No Name'})"

class BeltTracking(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    belt_name = models.CharField(max_length=255)
    mac_address = models.CharField(max_length=255, unique=True)
    uuid = models.CharField(max_length=255)
    last_connected = models.DateTimeField(null=True, blank=True)
    device_name = models.CharField(max_length=255)
    status = models.CharField(max_length=13, default='disconnected')

    def __str__(self):
        return f"Belt {self.id} - {self.user.id if self.user else 'No User'} ({self.user.name if self.user else 'No Name'})"
