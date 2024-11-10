from django.db import models
from signup.models import CustomUser

# Create your models here.
class SchoolVerification(models.Model):
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('approved', '승인'),
        ('rejected', '거부'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='school_verification')
    verification_photo = models.ImageField(upload_to='school_verifications/', blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    submission_date = models.DateTimeField(auto_now_add=True)  # 제출 날짜
    review_date = models.DateTimeField(null=True, blank=True)  # 관리자가 검토한 날짜

    def __str__(self):
        return f"학교 인증 - {self.user.username} - {self.status}"