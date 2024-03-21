from django.urls import path
from . import views

urlpatterns = [
    path('video_feed', views.video_feed, name='video_feed'),
    path('video_feed_view', views.video_feed_view, name='video_feed_view'),
]
