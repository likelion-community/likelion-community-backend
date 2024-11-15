from django.db import models
from signup.models import CustomUser

class Verification(models.Model):
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('approved', '승인'),
        ('rejected', '거부'),
    ]

    TRACK_CHOICES = [
        ('backend', '백엔드'),
        ('frontend', '프론트엔드'),
        ('design', '기획/디자인'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='verification')
    school_verification_photo = models.ImageField(upload_to='school_verifications/', blank=True, null=True)
    executive_verification_photo = models.ImageField(upload_to='executive_verifications/', blank=True, null=True)
    school_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    executive_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    track = models.CharField(max_length=10, choices=TRACK_CHOICES, blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    review_date = models.DateTimeField(null=True, blank=True)

    is_school_verified = models.BooleanField(default=False)  

    def __str__(self):
        return f"인증 - {self.user.username} - 학교: {self.school_status}, 운영진: {self.executive_status}"
    