from django.urls import path
from . import views

from login_app import views as user_views

from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import views as auth_views


urlpatterns = [

    #path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_home/', views.admin_home, name='admin_home'),
    
    path('change_password/', views.change_password , name='change_password'),
    path('change_password_done/', views.change_password_done , name='change_password_done'),
    
    path('email_management', views.email_management, name='email_management'),
    path('delete_email/<id>/',views.delete_email , name="delete_email"),
    
    path('user_mgt/', views.user_mgt, name='user_mgt'),
    path('add_user/', views.add_user, name='add_user'),
    path('delete_user/<id>/',views.delete_user , name="delete_user"),
    path('update_user/<id>/',views.update_user , name="update_user"),
    
    path('fire_logs/', views.fire_logs, name='fire_logs'),
    path('send_fire_alert/', views.send_email, name='send_fire_alert'),
    
    path('logout/', user_views.logout_view, name='logout'),
    
    path('login/', views.user_login, name='login'),
     
    
    #path('register/',views.register, name='register'),
    #path('login/', views.user_login, name='login'),
    #path('logout/', views.user_logout, name='logout'),
]
