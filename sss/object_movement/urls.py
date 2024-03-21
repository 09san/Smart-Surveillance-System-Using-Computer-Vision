# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('object_monitoring/', views.object_monitoring, name='object_monitoring'),
    path('object_monitoring/video_feed/', views.object_monitoring_feed, name='object_monitoring_video_feed'),
]