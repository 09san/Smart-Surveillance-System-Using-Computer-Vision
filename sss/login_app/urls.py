from django.urls import path
from . import views

from admin_app import views as admin_views

urlpatterns = [
    path('', admin_views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
     path('home/', views.home, name='home')
]
