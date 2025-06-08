# echotrail_backend/echotrail_backend/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),  # ✅ user register/login endpoints
    path('api/', include('navigation.urls')),
    path('api/admin/', include('dashboard.urls')),

]
