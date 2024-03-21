from django.urls import path
from . import views

urlpatterns = [
   
    path('home/in_and_out/', views.in_and_out, name='in_and_out'),
    path('home/in_and_out/in_and_out_feed', views.in_and_out_feed, name='in_and_out_feed'),
]
