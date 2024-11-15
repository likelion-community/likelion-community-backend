# signup/models.py
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, name=None, password=None, **extra_fields):
        if not email:
            raise ValueError('이메일 주소가 필요합니다.')
        
        user = self.model(
            username=username,
            email=self.normalize_email(email),
            name=name,
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
    TRACK_CHOICES = [
        ('백엔드', '백엔드'),
        ('프론트엔드', '프론트엔드'),
        ('기획/디자인', '기획/디자인'),
    ]
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    nickname = models.CharField(max_length=50, blank=True, null=True)
    school_name = models.CharField(max_length=100, blank=True, null=True)  
    verification_photo = models.ImageField(upload_to='verification_photos/', blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    membership_term = models.PositiveSmallIntegerField(choices=[(i, f"{i}기") for i in range(1, 13)], blank=True, null=True)
    track = models.CharField(max_length=20, choices=TRACK_CHOICES, blank=True, null=True, default='백엔드')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_profile_complete = models.BooleanField(default=False)
    is_school_verified = models.BooleanField(default=False)  # 학교 인증 여부 필드 추가

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'name', 'nickname']

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        # school_name이 입력되면 is_school_verified를 True로 설정
        if self.school_name:
            self.is_school_verified = True
        super().save(*args, **kwargs)

class CustomUserToken(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return f"Token for {self.user.username}"
