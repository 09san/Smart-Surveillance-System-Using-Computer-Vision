from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to your home page
    else:
        form = AuthenticationForm()
    return render(request, 'login_app/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('/')

@login_required  # This decorator ensures that only authenticated users can access this view
def home(request):
    username = request.user.username  # Get the username of the currently logged-in user
    return render(request, 'home.html', {'username': username})
