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
from django.db import transaction
from datetime import datetime
from django.utils.timezone import make_aware, get_default_timezone


class AttendanceMainView(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        # 최신 글이 가장 위로 오도록 정렬
        return Attendance.objects.filter(
            created_by__school_name=self.request.user.school_name
        ).order_by('-date', '-time', '-id')  # date, time, id 기준 내림차순 정렬

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        attendance_data = self.get_serializer(queryset, many=True).data

        # CustomUserSerializer로 사용자 정보 자동 처리
        user_serializer = CustomUserSerializer(request.user)
        user_data = user_serializer.data

        # AttendanceStatus 정보 포함
        attendance_statuses = AttendanceStatus.objects.filter(
            user=request.user,
            attendance__created_by__school_name=request.user.school_name
        )
        attendance_status_serializer = AttendanceStatusSerializer(attendance_statuses, many=True)

        response_data = {
            "attendances": attendance_data,
            "user_info": user_data,
            "attendance_statuses": attendance_status_serializer.data,  # 추가된 사용자 출석 상태
        }
        return Response(response_data, status=status.HTTP_200_OK)


class AttendanceSetView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly, IsSchoolVerifiedAndSameGroup]
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied("출석 등록은 운영자만 할 수 있습니다.")

        # 출석글 저장
        attendance = serializer.save(created_by=self.request.user)

        # 해당 출석글의 트랙에 따른 회원 조회
        track = attendance.track
        if track == "전체트랙":
            users = CustomUser.objects.filter(
                school_name=self.request.user.school_name,
                is_staff=False  # 운영자 제외
            )
        else:
            users = CustomUser.objects.filter(
                school_name=self.request.user.school_name,
                track=track,
                is_staff=False
            )

        # 관련된 회원들에 대해 AttendanceStatus를 '결석'으로 생성
        attendance_status_list = [
            AttendanceStatus(
                attendance=attendance,
                user=user,
                status="결석",  # 기본 상태: 결석
                date=attendance.date
            ) for user in users
        ]
        AttendanceStatus.objects.bulk_create(attendance_status_list)




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

    def get_queryset(self):
        # 로그인한 사용자의 school_name에 맞는 출석 데이터만 반환
        return Attendance.objects.filter(
            created_by__school_name=self.request.user.school_name
        )

    def retrieve(self, request, *args, **kwargs):
        attendance = self.get_object()

        # 글의 트랙 정보 가져오기
        track = attendance.track

        # 트랙과 같은 기수 조건으로 사용자 필터링
        if track == "전체트랙":
            users = CustomUser.objects.filter(
                school_name=request.user.school_name,
                membership_term=request.user.membership_term,  # 같은 기수
                is_staff=False  # 운영자를 제외
            )
        else:
            users = CustomUser.objects.filter(
                school_name=request.user.school_name,
                track=track,  # 글의 트랙과 동일한 트랙의 사용자
                membership_term=request.user.membership_term,  # 같은 기수
                is_staff=False  # 운영자를 제외
            )

        # 각 사용자에 대해 출석 상태 결합
        user_data = []
        for user in users:
            user_status = AttendanceStatus.objects.filter(
                attendance=attendance,
                user=user
            ).first()

            user_data.append({
                "id": user.id,
                "name": user.name,
                "nickname": user.nickname,
                "email": user.email,
                "attendance_status": user_status.status if user_status else "결석",  # 상태가 없으면 "결석"
                "status_id": user_status.id if user_status else None,  # status_id 추가
                "attendance_date": user_status.date if user_status else None,  # 상태 날짜 없으면 None
                "track": user.track, 
                "membership_term": user.membership_term,
            })

        # 정렬 로직: 상태 우선 순위와 이름
        status_priority = {"출석": 1, "지각": 2, "결석": 3}
        user_data.sort(
            key=lambda x: (status_priority.get(x["attendance_status"], 4), x["name"])
        )

        attendance_data = {
            "attendance": self.get_serializer(attendance).data,
            "users": user_data,  
        }

        return Response(attendance_data, status=status.HTTP_200_OK)



class AttendanceCheckView(APIView):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]

    def post(self, request, *args, **kwargs):
        attendance_id = kwargs.get('id')
        input_code = request.data.get('auth_code')
        if not input_code:
            raise ValueError("출석 코드가 제공되지 않았습니다.")

        try:
            attendance = Attendance.objects.get(id=attendance_id)
            current_time = timezone.now()

            session_start = make_aware(
                datetime.combine(attendance.date, attendance.time),
                timezone=get_default_timezone()  # 서버의 기본 타임존
            )
            time_difference = (current_time - session_start).total_seconds() / 60

            # 출석 코드 확인
            if attendance.auth_code != input_code:
                return Response({'error': '출석코드가 일치하지 않아요'}, status=status.HTTP_400_BAD_REQUEST)

            # 출석 상태 결정
            if time_difference <= attendance.late_threshold:  # 출석 기준 시간 내
                status_type = '출석'
            elif attendance.late_threshold < time_difference <= (attendance.late_threshold + attendance.absent_threshold):  # 지각 기준 시간
                status_type = '지각'
            else:  # 결석 기준 시간
                status_type = '결석'

            # AttendanceStatus 업데이트 또는 생성
            attendance_status, created = AttendanceStatus.objects.update_or_create(
                attendance=attendance,
                user=request.user,
                defaults={
                    'status': status_type,
                    'date': current_time.date(), 
                }
            )

            # 반환 데이터에서 date를 ISO 형식 문자열로 변환
            return Response(
                {
                    'message': f"{current_time.date()} 출석 상태: {status_type}",
                    'date': current_time.date().isoformat(),
                    'status': status_type,
                },
                status=status.HTTP_200_OK
            )
        except Attendance.DoesNotExist:
            return Response({'error': '해당 출석 정보가 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error in AttendanceCheckView: {e}")
            return Response({'error': '서버 오류가 발생했습니다.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AttendanceStatusUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsStaffOrReadOnly, IsSchoolVerifiedAndSameGroup]

    def patch(self, request, *args, **kwargs):
        status_id = kwargs.get('status_id')  # 항상 존재하는 status_id
        new_status = request.data.get('status')  # 변경할 출석 상태

        print(f"Request Data - status_id: {status_id}, status: {new_status}")  # 디버깅용 로그

        try:
            with transaction.atomic():
                # `status_id`로 AttendanceStatus 객체 가져오기
                attendance_status = AttendanceStatus.objects.get(id=status_id)
                print(f"Found AttendanceStatus with id: {attendance_status.id}")  # 디버깅용 로그

                # 운영자 권한 확인
                if not request.user.is_staff:
                    raise PermissionDenied("운영자만 출석 상태를 수정할 수 있습니다.")

                # 같은 학교 그룹인지 확인
                if attendance_status.attendance.created_by.school_name != request.user.school_name:
                    raise PermissionDenied("같은 학교 그룹의 출석 상태만 수정할 수 있습니다.")

                # 상태 업데이트
                attendance_status.status = new_status
                attendance_status.date = timezone.now().date()
                attendance_status.save()

                # 업데이트된 데이터 반환
                serializer = AttendanceStatusSerializer(attendance_status)
                print(f"Updated AttendanceStatus: {attendance_status.status}")  # 디버깅용 로그
                return Response(serializer.data, status=status.HTTP_200_OK)

        except AttendanceStatus.DoesNotExist:
            return Response({'error': 'AttendanceStatus not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f"Error: {str(e)}")
            return Response({'error': f'Error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        ).order_by('-date', '-time')

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
        user_attendance = AttendanceStatus.objects.filter(user=user, user__is_staff=False).order_by('-date')
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
