from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    name = forms.CharField(max_length=100)
    verification_photo = forms.ImageField(required=True)
    membership_term = forms.ChoiceField(choices=[(i, f"{i}기") for i in range(1, 13)], required=True)  # 드롭다운 설정

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'name', 'nickname', 'password1', 'password2', 'verification_photo', 'membership_term')

class AdditionalInfoForm(forms.ModelForm):
    membership_term = forms.ChoiceField(choices=[(i, f"{i}기") for i in range(1, 13)], required=True)  # 드롭다운 설정
    class Meta:
        model = CustomUser
        fields = ['name', 'nickname', 'membership_term', 'verification_photo']

class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100, label="아이디")
    password = forms.CharField(widget=forms.PasswordInput, label="비밀번호")

