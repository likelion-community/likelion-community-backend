from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Attendance, AttendanceStatus
from signup.models import CustomUser
from .serializers import AttendanceSerializer, AttendanceStatusSerializer, CreatorProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .permissions import IsStaffOrReadOnly, IsSchoolVerifiedAndSameGroup
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from django.utils import timezone
import random

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
        
        # 4자리 출석 코드 자동 생성
        auth_code = ''.join(random.choices('0123456789', k=4))
        
        # 출석 코드는 운영진(작성자)이 생성하도록 자동으로 할당
        serializer.save(created_by=self.request.user, auth_code=auth_code)

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
    
class AttendanceCheckView(APIView):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]

    def post(self, request, *args, **kwargs):
        attendance_id = kwargs.get('id')
        input = request.data.get('auth_code')

        try:
            attendance = Attendance.objects.get(id = attendance_id)
            date = timezone.now().date()

            if attendance.auth_code == input:
                AttendanceStatus.objects.create(
                    attendance=attendance,
                    user=request.user,
                    status='present',
                    date=date
                )
                return Response({'message': f"{date} 출석 완료"}, status=status.HTTP_200_OK)
            else:
                return Response({'error': '출석코드가 일치하지 않아요'}, status=status.HTTP_400_BAD_REQUEST)
            
        except Attendance.DoesNotExist:
            return Response({'error': '해당 출석 정보가 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)
        
class CreatorProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')

        try:
            user = CustomUser.objects.get(id=user_id)
            serializer = CreatorProfileSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({'message': '사용자를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)