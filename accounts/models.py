# accounts/models.py

import bcrypt
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    status = models.CharField(max_length=10, default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    # Role-based field
    is_admin = models.BooleanField(default=False)

    # Use email as the unique identifier for login
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def set_password(self, raw_password):
        """Hash password using bcrypt."""
        self.password = bcrypt.hashpw(
            raw_password.encode('utf-8'), bcrypt.gensalt()
        ).decode('utf-8')

    def check_password(self, raw_password):
        """Check hashed password using bcrypt."""
        return bcrypt.checkpw(
            raw_password.encode('utf-8'), self.password.encode('utf-8')
        )

    def __str__(self):
        return f"{self.name} / {self.id}"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"


# Optional: Proxy model to show Admins separately in Django Admin
class AdminUser(User):
    class Meta:
        proxy = True
        verbose_name = "Admin"
        verbose_name_plural = "Admins"


# ========== Supporting Models ==========

class Alarm(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    alarm_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Alarm {self.id} - {self.user.id if self.user else 'No User'} ({self.user.name if self.user else 'No Name'})"


class BatteryMonitoring(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    threshold = models.IntegerField(default=25)
    updated_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Battery {self.id} - {self.user.id if self.user else 'No User'} ({self.user.name if self.user else 'No Name'})"


class BeltTracking(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    belt_name = models.CharField(max_length=255)
    mac_address = models.CharField(max_length=255, unique=True)
    uuid = models.CharField(max_length=255)
    last_connected = models.DateTimeField(null=True, blank=True)
    device_name = models.CharField(max_length=255)
    status = models.CharField(max_length=13, default='disconnected')

    def __str__(self):
        return f"Belt {self.id} - {self.user.id if self.user else 'No User'} ({self.user.name if self.user else 'No Name'})"