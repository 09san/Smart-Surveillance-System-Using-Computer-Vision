from django import forms
from .models import CustomUser

class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    user_type = forms.ChoiceField(choices=[('admin', 'Admin'), ('user', 'User')], required=False, label='User Type')

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'password',)
