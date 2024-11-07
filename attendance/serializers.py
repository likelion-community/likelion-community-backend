from rest_framework import serializers
from .models import Attendance, AttendanceStatus

class AttendanceSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')  # 읽기 전용으로 설정
    file = serializers.FileField(allow_null=True, required=False)  # 이미지 대신 파일 필드로 사용

    class Meta:
        model = Attendance
        fields = ['id', 'date', 'title', 'auth_code', 'description', 'file', 'created_by']  # image -> file로 변경

class AttendanceStatusSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)  # 사용자 이름을 추가로 보여주기

    class Meta:
        model = AttendanceStatus
        fields = ['id', 'attendance', 'user', 'user_name', 'status', 'date']
