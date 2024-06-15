from django import forms
from .models import CustomUser
from django.contrib.auth import authenticate

class LoginForm(forms.Form):
    username = forms.CharField(label='Username')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')
    user_type = forms.ChoiceField(choices=[('admin', 'Admin'), ('user', 'User')], required=False, label='User Type')

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'password',)
        
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='Old Password', widget=forms.PasswordInput)
    new_password = forms.CharField(label='New Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password != confirm_password:
            raise forms.ValidationError("New password and confirm password do not match.")

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        user = authenticate(username=self.user.username, password=old_password)
        if user is None:
            raise forms.ValidationError("Your old password is incorrect.")
        return old_password