from django.db import models
from signup.models import CustomUser
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from django.db import models
from signup.models import CustomUser
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class Attendance(models.Model):
    TRACK_CHOICES = [
        ('백엔드', '백엔드'),
        ('프론트엔드', '프론트엔드'),
        ('기획/디자인', '기획/디자인'),
        ('전체트랙', '전체트랙')
    ]

    date = models.DateField()
    time = models.TimeField()
    title = models.CharField(max_length=100)
    auth_code = models.CharField(max_length=20)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='attendance_files/', blank=True, null=True) 
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='created_attendances')
    track = models.CharField(max_length=20, choices=TRACK_CHOICES, default='백엔드')
    place = models.CharField(max_length=100, blank=True, null=True)

    # 지각 및 결석 기준 시간 (운영진이 설정 가능)
    late_threshold = models.IntegerField()  # 지각 기준 (분)
    absent_threshold = models.IntegerField()  # 결석 기준 (분)

    def __str__(self):
        return f"{self.title} - {self.date}"

    @property
    def school_name(self):
        return self.created_by.school_name  # CustomUser의 school_name 참조

    @property
    def is_school_verified(self):
        return self.created_by.is_school_verified  # CustomUser의 is_school_verified 참조

    @property
    def membership_term(self):
        return self.created_by.membership_term  # CustomUser의 membership_term 참조

    @property
    def user_track(self):
        return self.created_by.track  # CustomUser의 track 참조


class AttendanceStatus(models.Model):
    STATUS_CHOICES = [
        ('출석', '출석'),
        ('지각', '지각'),
        ('결석', '결석')
    ]
    
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE, related_name='statuses')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='attendance_status')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    date = models.DateField()

    def __str__(self):
        return f"{self.user.name} - {self.status} on {self.date}"

    @property
    def school_name(self):
        return self.user.school_name  # CustomUser의 school_name 참조

    @property
    def is_school_verified(self):
        return self.user.is_school_verified  # CustomUser의 is_school_verified 참조

    @property
    def membership_term(self):
        return self.user.membership_term  # CustomUser의 membership_term 참조

    @property
    def user_track(self):
        return self.user.track  # CustomUser의 track 참조

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # 출석 상태 변경 시 WebSocket을 통해 전송
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'attendance_{self.attendance.id}',  # 그룹명
            {
                'type': 'attendance_status_update',
                'status': self.status,
                'user': {'id': self.user.id, 'name': self.user.name, 'school_name': self.school_name}  # 전송할 데이터
            }
        )
