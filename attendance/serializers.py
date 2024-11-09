from rest_framework import serializers
from .models import Attendance, AttendanceStatus

class AttendanceSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    file = serializers.FileField(allow_null=True, required=False)
    track = serializers.ChoiceField(choices=Attendance.TRACK_CHOICES)  # 모델의 TRACK_CHOICES와 통일
    auth_code = serializers.CharField(write_only=True, required=True)  # 운영진이 출석 코드를 생성
    time = serializers.TimeField(required=True) 

    class Meta:
        model = Attendance
        fields = ['id', 'date', 'time', 'title', 'auth_code', 'description', 'file', 'track', 'created_by']



class AttendanceStatusSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)  # 사용자 이름을 추가로 보여주기

    class Meta:
        model = AttendanceStatus
        fields = ['id', 'attendance', 'user', 'user_name', 'status', 'date']
