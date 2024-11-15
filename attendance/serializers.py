from rest_framework import serializers
from .models import Attendance, AttendanceStatus
from signup.models import CustomUser

class AttendanceSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')
    creator_name = serializers.CharField(source='created_by.name', read_only=True)
    creator_term = serializers.IntegerField(source='created_by.membership_term', read_only=True)
    creator_position = serializers.CharField(source='created_by.is_staff', read_only=True)
    file = serializers.FileField(allow_null=True, required=False)
    track = serializers.ChoiceField(choices=Attendance.TRACK_CHOICES)
    auth_code = serializers.CharField(write_only=True, required=True)
    time = serializers.TimeField(required=True)
    late_threshold = serializers.IntegerField(required=True)
    absent_threshold = serializers.IntegerField(required=True)
    place = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Attendance
        fields = ['id', 'date', 'time', 'title', 'auth_code', 'description', 'file', 'track', 'created_by', 'creator_name', 'creator_term', 'creator_position', 'late_threshold', 'absent_threshold', 'place']


class AttendanceStatusSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)  # 사용자 이름을 추가로 보여주기

    class Meta:
        model = AttendanceStatus
        fields = ['id', 'attendance', 'user', 'user_name', 'status', 'date']

class CreatorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'nickname', 'school_name', 'profile_image', 'membership_term']