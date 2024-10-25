from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=100)
    verification_photo = forms.ImageField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'name', 'nickname','password1', 'password2', 'verification_photo')


class AdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['name', 'nickname','verification_photo']


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, label="아이디")
    password = forms.CharField(widget=forms.PasswordInput, label="비밀번호")
