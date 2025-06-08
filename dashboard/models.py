import bcrypt
from django.db import models

class AdminUser(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=10, default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    # Corrected set_password method
    def set_password(self, raw_password):
        self.password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Corrected check_password method
    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))

    def __str__(self):
        return self.name or self.email

    class Meta:
        verbose_name = "Admins"
        verbose_name_plural = "Admins"


from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=10, default='inactive')
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.name} / {self.id}"

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
