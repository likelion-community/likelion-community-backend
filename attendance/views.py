from rest_framework import viewsets
from rest_framework.response import Response
from .models import Attendance, AttendanceStatus
from .serializers import AttendanceSerializer, AttendanceStatusSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .permissions import IsStaffOrReadOnly, IsSchoolVerifiedAndSameGroup
from rest_framework.generics import RetrieveAPIView


class AttendanceMainView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        # 운영진의 학교 그룹과 일치하는 출석 데이터만 반환
        return Attendance.objects.filter(created_by__school_name=self.request.user.school_name)

class AttendanceSetView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly, IsSchoolVerifiedAndSameGroup]
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("출석 등록은 staff만 할 수 있습니다.")
        serializer.save(created_by=self.request.user)
    def perform_update(self, serializer):
        # 수정 시에도 created_by가 현재 사용자로 설정되도록 설정
        serializer.save(created_by=self.request.user)


class AttendanceDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    serializer_class = AttendanceSerializer

    def retrieve(self, request, *args, **kwargs):
        attendance = self.get_object()
        # 현재 사용자의 학교 그룹과 일치하는 출석 상태 데이터만 반환
        attendance_statuses = AttendanceStatus.objects.filter(attendance=attendance, user__school_name=request.user.school_name)
        attendance_data = {
            "attendance": self.get_serializer(attendance).data,
            "attendance_statuses": AttendanceStatusSerializer(attendance_statuses, many=True).data
        }
        return Response(attendance_data)