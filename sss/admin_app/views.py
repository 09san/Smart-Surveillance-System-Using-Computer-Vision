from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm

from . utils import send_fire_alert

from .models import *

def user_login(request):
    error_message = None  # Initialize error_message with None
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user_type = form.cleaned_data['user_type']

            user = authenticate(request, username=username, password=password)

            print("Authenticated User:", user)  # Debugging: Print authenticated user
            
            if user is not None:
                if user_type == 'admin' and user.is_staff:
                    login(request, user)
                    print("------Admin logged in.------")  # Debugging: Print admin logged in
                    return redirect('admin_home/')  # Redirect to admin dashboard
                elif (user_type == 'user' and not user.is_staff ) or (user_type == 'user' and user.is_staff):
                    login(request, user)
                    print("------User logged in.------")  # Debugging: Print user logged in
                    return redirect('home/')  # Redirect to user dashboard
                else:
                    error_message = "Access Denied. Incorrect User Type."
                    print("Access Denied. Incorrect User Type.")  # Debugging: Print access denied for incorrect user type
            else:
                error_message = "Access Denied. Invalid Credentials."
                print("Access Denied. Invalid Credentials.")  # Debugging: Print access denied for invalid credentials
        else:
            error_message = "Form is not valid."
            print("Form is not valid.")  # Debugging: Print form is not valid
            print(form.errors)  # Debugging: Print form errors

    else:
        form = LoginForm()

    return render(request, 'login_app/login.html', {'form': form, 'error_message': error_message})

def admin_home(request):
    return render(request, 'admin_home.html')

def user_mgt(request):
    normal_users = CustomUser.objects.filter(is_staff=False)
    
    context={
        'users':normal_users
    }
    return render(request, 'user_mgt.html',context)

def add_user(request):
    #add User
    if request.method == 'POST':
        data=request.POST
        
        username=data.get('username')
        email=data.get('email')
        password=data.get('password')
        
        user=CustomUser.objects.create(username=username,
                                       email=email,
        )
        user.set_password(password) #password is hasshed 
        user.save()
        return redirect('user_mgt')
    return render(request, 'add_user.html')

def email_management(request):
    return render(request, 'email_alert.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('home.html')  # Redirect to user dashboard if not admin

    # Add your admin dashboard logic here

    return render(request, 'admin_home.html')

def delete_user(request, id):
    user_to_delete = CustomUser.objects.get(id=id) 
    user_to_delete.delete()
    
    return redirect('user_mgt')


def update_user(request, id):
    user_to_update = CustomUser.objects.all().get(id=id)
    
    if request.method == 'POST':
        
        data = request.POST
        
        username=data.get('username')
        email=data.get('email')
        password=data.get('password')
        
        user_to_update.username=username
        user_to_update.email=email
        user_to_update.password=password
        
       
        user_to_update.save()
        
        return redirect('user_mgt')
    
    context={
        'user': user_to_update
    }
    
    return render(request , 'update_user.html' , context)

def email_management(request):
    
    if request.method == 'POST':
        data=request.POST
        
        newemail=data.get('newemail')
        
        Email.objects.create(email=newemail)
        return redirect('email_management')
    
    queryset = Email.objects.all()
    
    context={
        'emails':queryset
    }
    
    return render(request , 'email_alert.html', context)

def delete_email(request, id):
    email_to_delete = Email.objects.get(id=id) 
    email_to_delete.delete()
    
    return redirect('email_management')


def fire_logs(request):
    
    return render(request, 'fire_logs.html' )

def send_email(request):
    send_fire_alert()
