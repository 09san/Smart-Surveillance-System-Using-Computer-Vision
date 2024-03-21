from django.urls import path
from . import views
from . import consumers

urlpatterns = [

    path('home/firedetection/', views.fire_detection, name='firedetection'),
    #path('home/firedetection/processing/', views.start_stop_backend_process, name='start_stop_backend_process'), #terminate
    path('home/firedetection/fire_detection_feed', views.fire_detection_feed, name='fire_detection_feed'),
    #path('home/firedetection/processing/backend', views.fire_detection_backend, name='fire_detection_backend')
    path('home/firedetection/fire_detection_feed/fire_detection_events/', consumers.FireDetectionConsumer.as_asgi())
    
]
