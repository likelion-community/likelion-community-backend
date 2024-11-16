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
from signup.serializers import CustomUserSerializer
from django.db.models import Count


class AttendanceMainView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        return Attendance.objects.filter(created_by__school_name=self.request.user.school_name)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        attendance_data = self.get_serializer(queryset, many=True).data

        # CustomUserSerializer로 사용자 정보 자동 처리
        user_serializer = CustomUserSerializer(request.user)
        user_data = user_serializer.data

        response_data = {
            "attendances": attendance_data,
            "user_info": user_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    

class AttendanceSetView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly, IsSchoolVerifiedAndSameGroup]
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("출석 등록은 staff만 할 수 있습니다.")
        
        
        # 출석 코드는 운영진(작성자)이 직접 생성하도록
        serializer.save(
            created_by=self.request.user,
            creator_name=self.request.user.name,
            creator_term=self.request.user.membership_term,
            creator_position='운영진'
        )

    def perform_update(self, serializer):
        # 수정 시에도 created_by가 현재 사용자로 설정되도록 설정
        serializer.save(created_by=self.request.user)

class CreatorInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # 현재 로그인된 사용자의 정보를 조회합니다
        user = request.user
        serializer = CreatorProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AttendanceDetailView(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    serializer_class = AttendanceSerializer

    def retrieve(self, request, *args, **kwargs):
        attendance = self.get_object()
        # 현재 사용자의 학교 그룹과 일치하는 출석 상태 데이터만 반환
        attendance_statuses = AttendanceStatus.objects.filter(
            attendance=attendance, user__school_name=request.user.school_name
        )
        attendance_data = {
            "attendance": self.get_serializer(attendance).data,
            "attendance_statuses": AttendanceStatusSerializer(attendance_statuses, many=True).data
        }
        return Response(attendance_data)
    


class AttendanceCheckView(APIView):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]

    def post(self, request, *args, **kwargs):
        attendance_id = kwargs.get('id')
        input_code = request.data.get('auth_code')

        try:
            attendance = Attendance.objects.get(id=attendance_id)
            current_time = timezone.now()

            # 세션 시작 시간을 기준으로 시간 차이 계산
            session_start = timezone.make_aware(timezone.datetime.combine(attendance.date, attendance.time))
            time_difference = (current_time - session_start).total_seconds() / 60  # 분 단위로 계산

            # 출석 코드 일치 여부 확인
            if attendance.auth_code != input_code:
                return Response({'error': '출석코드가 일치하지 않아요'}, status=status.HTTP_400_BAD_REQUEST)

            # 출석 상태 결정
            if time_difference <= attendance.late_threshold:
                status_type = '출석'  # 정상 출석
            elif time_difference <= attendance.absent_threshold:
                status_type = '지각'     # 지각
            else:
                status_type = '결석'   # 결석

            # AttendanceStatus 생성
            AttendanceStatus.objects.create(
                attendance=attendance,
                user=request.user,
                status=status_type,
                date=current_time.date()
            )
            return Response({'message': f"{current_time.date()} 출석 상태: {status_type}"}, status=status.HTTP_200_OK)
            
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
        
        
class UserTrackAttendanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Attendance.objects.filter(created_by__school_name=self.request.user.school_name)

    def get(self, request, *args, **kwargs):
        user = request.user
        current_time = timezone.now()

        # 사용자 트랙과 '전체' 트랙을 포함한 출석 데이터 필터링
        all_attendances = Attendance.objects.filter(
            track__in=[user.track, '전체트랙'],
            created_by__school_name=user.school_name
        ).order_by('-date')

        # 출석 코드 입력이 없는 경우 결석으로 기록
        for attendance in all_attendances:
            session_start = timezone.make_aware(timezone.datetime.combine(attendance.date, attendance.time))
            if current_time > session_start and not AttendanceStatus.objects.filter(attendance=attendance, user=user).exists():
                # 사용자의 출석 상태가 없으면 결석으로 기록
                AttendanceStatus.objects.create(
                    attendance=attendance,
                    user=user,
                    status='결석',
                    date=current_time.date()
                )

        attendance_serializer = AttendanceSerializer(all_attendances, many=True)

        # 사용자의 출석 상태 데이터 필터링
        user_attendance = AttendanceStatus.objects.filter(user=user).order_by('-date')
        status_serializer = AttendanceStatusSerializer(user_attendance, many=True)
        attendance_count = user_attendance.values('status').annotate(count=Count('status'))
        status_count = {
            '출석': 0,
            '지각': 0,
            '결석': 0
        }
        for entry in attendance_count:
            status_count[entry['status']] = entry['count']

        response_data = {
            "all_attendances": attendance_serializer.data,
            "user_attendance": status_serializer.data,
            "status_count": status_count
        }

        return Response(response_data, status=status.HTTP_200_OK)
