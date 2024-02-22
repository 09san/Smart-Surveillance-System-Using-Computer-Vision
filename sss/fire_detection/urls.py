from django.urls import path
from . import views

urlpatterns = [

    path('home/firedetection/', views.fire_detection, name='firedetection'),
    path('home/firedetection/processing/', views.start_stop_backend_process, name='start_stop_backend_process'),

    
]
