from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django import forms

# get_user_model() 사용을 제거하고, CustomUser 직접 참조
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, name=None, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일 주소가 필요합니다.')
        
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            name=name,  # 기본값 'Unknown' 제거
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user


    def create_superuser(self, username, email, name=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, name, password, **extra_fields)
    

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True) 
    verification_photo = models.ImageField(upload_to='verification_photos/', blank=True, null=True)
    membership_term = models.PositiveSmallIntegerField(choices=[(i, f"{i}기") for i in range(1, 13)], blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)  # 프로필 완성 여부


    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name', 'nickname']
    
    def __str__(self):
        return self.username
