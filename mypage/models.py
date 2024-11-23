from django.db import models
from signup.models import CustomUser

class VerificationPhoto(models.Model):
    photo = models.ImageField(upload_to='verification_photos/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo {self.id}"
    
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
    verification_photos = models.ManyToManyField(VerificationPhoto, related_name="verifications")
    school_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    executive_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    track = models.CharField(max_length=10, choices=TRACK_CHOICES, blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    review_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"인증 - {self.user.username} - 학교: {self.school_status}, 운영진: {self.executive_status}"

    def save(self, *args, **kwargs):
        # executive_status에 따라 CustomUser의 is_staff 값 업데이트
        if self.executive_status == 'approved':
            self.user.is_staff = True
        elif self.executive_status == 'rejected':
            self.user.is_staff = False
        
        # CustomUser 저장
        self.user.save()
        
        # Verification 저장
        super().save(*args, **kwargs)