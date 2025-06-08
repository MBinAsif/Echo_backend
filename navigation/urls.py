from django.urls import path
from .views import ObstacleDetectView

urlpatterns = [
    path('obstacle-detect/', ObstacleDetectView.as_view(), name='obstacle_detect'),
]
