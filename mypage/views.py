from django.shortcuts import render
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from signup.models import CustomUser
from .serializers import *
from post.models import *
from post.serializers import *
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.conf import settings
from .serializers import UserSerializer
from rest_framework.reverse import reverse_lazy 
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import VerificationPhoto, Verification
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Max


class MyPageOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user_serializer = UserSerializer(user)

        # Verification 정보 가져오기
        try:
            verification = Verification.objects.get(user=user)
        except Verification.DoesNotExist:
            verification = None

        # Verification에 연결된 사진 목록 가져오기
        verification_photos = (
            VerificationPhoto.objects.filter(verifications=verification)
            if verification
            else []
        )
        photo_serializer = VerificationPhotoSerializer(verification_photos, many=True)

        # 데이터 구조 정리 및 URL 반환
        response_data = {
            "user_info": user_serializer.data,
            "verification_status": {
                "school_status": verification.school_status if verification else "none",
                "executive_status": verification.executive_status if verification else "none",
            },
            "details": {
                "school_name": user.school_name if verification and verification.school_status == "approved" else None,
                "track": verification.track if verification and verification.school_status == "approved" else None,
            },
            "actions": {
                "update_profile_image": request.build_absolute_uri(reverse_lazy('mypage:profileimage')),
                "view_scraps": request.build_absolute_uri(reverse_lazy('mypage:myscraps')),
                "view_posts": request.build_absolute_uri(reverse_lazy('mypage:myposts')),
                "view_comments": request.build_absolute_uri(reverse_lazy('mypage:mycomments')),
                "verification_status": request.build_absolute_uri(reverse_lazy('mypage:verification_status')),
                "upload_verification_photos": request.build_absolute_uri(reverse_lazy('mypage:upload_verification_photos')),
            },
            "verification_photos": photo_serializer.data,
            "is_staff": user.is_staff,
        }

        return Response(response_data, status=status.HTTP_200_OK)



class ProfileImageUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        user = request.user
        serializer = ProfileImageSerializer(user, data = request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({'message': '프로필 사진이 변경되었습니다.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MyScrapView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        mainscrap = MainBoard.objects.filter(scrap=user)
        schoolscrap = SchoolBoard.objects.filter(scrap=user)
        questionscrap = QuestionBoard.objects.filter(scrap=user)

        mainscrap_serializer = MainBoardSerializer(mainscrap, many=True, context={'request': request})
        schoolscrap_serializer = SchoolBoardSerializer(schoolscrap, many=True, context={'request': request})
        questionscrap_serializer = QuestionBoardSerializer(questionscrap, many=True, context={'request': request})

        return Response({
            "mainscrap": mainscrap_serializer.data,
            "schoolscrap": schoolscrap_serializer.data,
            "questionscrap": questionscrap_serializer.data
        }, status=status.HTTP_200_OK)

    
class MyPostView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        mainpost = MainBoard.objects.filter(writer=user)
        schoolpost = SchoolBoard.objects.filter(writer=user)
        questionpost = QuestionBoard.objects.filter(writer=user)

        mainpost_serializer = MainBoardSerializer(mainpost, many=True, context={'request': request})
        schoolpost_serializer = SchoolBoardSerializer(schoolpost, many=True, context={'request': request})
        questionpost_serializer = QuestionBoardSerializer(questionpost, many=True, context={'request': request})

        return Response({
            "mainpost": mainpost_serializer.data,
            "schoolpost": schoolpost_serializer.data,
            "questionpost": questionpost_serializer.data
        }, status=status.HTTP_200_OK)



class MyCommentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        # MainComment, SchoolComment, QuestionComment에서 최신 댓글만 가져오기
        maincomment = (
            MainComment.objects.filter(writer=user)
            .values("board")  # board로 그룹화
            .annotate(latest_comment_time=Max("time"))  # 최신 댓글 시간 가져오기
            .order_by("-latest_comment_time")  # 최신 댓글 순 정렬
        )
        schoolcomment = (
            SchoolComment.objects.filter(writer=user)
            .values("board")
            .annotate(latest_comment_time=Max("time"))
            .order_by("-latest_comment_time")
        )
        questioncomment = (
            QuestionComment.objects.filter(writer=user)
            .values("board")
            .annotate(latest_comment_time=Max("time"))
            .order_by("-latest_comment_time")
        )

        maincomment_with_post = [
            {
                "latest_comment_time": comment["latest_comment_time"],
                "post_id": comment["board"],  
                "post_title": MainBoard.objects.get(id=comment["board"]).title,
                "post_created_at": MainBoard.objects.get(id=comment["board"]).time,
                "writer_id": user.id,  # 작성자 ID
            }
            for comment in maincomment
        ]
        schoolcomment_with_post = [
            {
                "latest_comment_time": comment["latest_comment_time"],
                "post_id": comment["board"],  
                "post_title": SchoolBoard.objects.get(id=comment["board"]).title,
                "post_created_at": SchoolBoard.objects.get(id=comment["board"]).time,
                "writer_id": user.id,
            }
            for comment in schoolcomment
        ]
        questioncomment_with_post = [
            {
                "latest_comment_time": comment["latest_comment_time"],
                "post_id": comment["board"], 
                "post_title": QuestionBoard.objects.get(id=comment["board"]).title,
                "post_created_at": QuestionBoard.objects.get(id=comment["board"]).time,
                "writer_id": user.id,
            }
            for comment in questioncomment
        ]

        return Response(
            {
                "main_comments": maincomment_with_post,
                "school_comments": schoolcomment_with_post,
                "question_comments": questioncomment_with_post,
            },
            status=status.HTTP_200_OK,
        )



class UploadVerificationPhotosView(APIView):
    """
    사용자가 사진을 업로드하고 Verification 객체와 연결
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # 파일 업로드 지원

    def post(self, request, *args, **kwargs):
        user = request.user
        files = request.FILES.getlist('photos')  # 여러 파일 가져오기

        if not files:
            return Response({"error": "사진을 업로드해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verification 객체 가져오기 또는 생성
            verification, created = Verification.objects.get_or_create(user=user)

            # 업로드된 파일 저장
            for file in files:
                photo = VerificationPhoto.objects.create(photo=file)
                verification.verification_photos.add(photo)

            verification.save()

            return Response({
                "message": "사진이 성공적으로 업로드되었습니다.",
                "verification": VerificationSerializer(verification).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": f"업로드 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



 #사용자가 이미 인증 정보를 가지고 있는 경우 기존 객체를 업데이트하도록 수정   
class VerificationStatusView(APIView):
    #Verification 상태를 확인하고 필요시 필드를 업데이트

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            verification = Verification.objects.get(user=user)
            serializer = VerificationSerializer(verification)
            return Response({
                "user_info": UserSerializer(user).data,
                "verification_status": serializer.data
            }, status=status.HTTP_200_OK)
        except Verification.DoesNotExist:
            return Response({
                "user_info": UserSerializer(user).data,
                "verification_status": "none"
            }, status=status.HTTP_200_OK)

    def patch(self, request, *args, **kwargs):
        #Verification 상태나 다른 필드를 업데이트
        user = request.user

        try:
            # Verification 객체 가져오기
            verification = Verification.objects.get(user=user)
        except Verification.DoesNotExist:
            return Response({"error": "Verification 객체가 존재하지 않습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = VerificationSerializer(verification, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "detail": "Verification 정보가 성공적으로 업데이트되었습니다.",
                "verification_status": serializer.data
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UpdateVerificationPhotosView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        files = request.FILES.getlist('photos')  # 여러 파일 가져오기

        if not files:
            return Response({"error": "수정할 사진을 업로드해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Verification 객체 가져오기
            verification = Verification.objects.get(user=user)
            print("Verification 객체 가져오기 성공")  # 디버깅 로그 추가

            # 기존 사진 삭제
            verification.verification_photos.clear()
            print("기존 사진 삭제 완료")  # 디버깅 로그 추가

            # 새로운 사진 추가
            for file in files:
                print(f"업로드된 파일: {file}")  # 업로드된 파일 확인
                photo = VerificationPhoto.objects.create(photo=file)
                verification.verification_photos.add(photo)
            print("새로운 사진 추가 완료")  # 디버깅 로그 추가

            # 상태 초기화
            verification.reset_status()
            verification.save()
            print("Verification 상태 초기화 및 저장 완료")  # 디버깅 로그 추가

            return Response({
                "message": "사진이 성공적으로 수정되었습니다.",
                "verification": VerificationSerializer(verification).data
            }, status=status.HTTP_200_OK)

        except Verification.DoesNotExist:
            print("Verification 객체가 존재하지 않음")  # 디버깅 로그 추가
            return Response({"error": "Verification 객체를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            import traceback
            print("업로드 중 예외 발생:", traceback.format_exc())  # 전체 예외 출력
            return Response({"error": f"업로드 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FindIDEmailView(APIView):
    def post (self, request, *args, **kwargs):
            email = request.data.get('email')
            if email:
                try:
                    user = CustomUser.objects.get(email=email)
                    verification_code = get_random_string(6, allowed_chars='0123456789')    # 6자리의 랜덤한 인증코드 값

                    send_mail(
                        '[이메일 인증] Everion 아이디 찾기 인증 코드',
                        f'인증 코드는 {verification_code}입니다.',
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )

                    request.session['verification_code'] = verification_code
                    request.session['user_id'] = user.id

                    return Response({"detail": "인증 코드가 이메일로 전송되었습니다."}, status=status.HTTP_200_OK)
                except CustomUser.DoesNotExist:
                    return Response({"error": "해당 이메일을 가진 사용자가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "이메일을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)
            
class FindPasswordEmailView(APIView):
    def post (self, request, *args, **kwargs):
            email = request.data.get('email')
            if email:
                try:
                    user = CustomUser.objects.get(email=email)
                    verification_code = get_random_string(6, allowed_chars='0123456789')    # 6자리의 랜덤한 인증코드 값

                    send_mail(
                        '[이메일 인증] Everion 비밀번호 재설정 인증 코드',
                        f'인증 코드는 {verification_code}입니다.',
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )

                    request.session['verification_code'] = verification_code
                    request.session['user_id'] = user.id

                    return Response({"detail": "인증 코드가 이메일로 전송되었습니다."}, status=status.HTTP_200_OK)
                except CustomUser.DoesNotExist:
                    return Response({"error": "해당 이메일을 가진 사용자가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "이메일을 입력하세요."}, status=status.HTTP_400_BAD_REQUEST)

class VerifyIDView(APIView):
    def post(self, request, *args, **kwargs):
        input_code = request.data.get('code')
        saved_code = request.session.get('verification_code')
        user_id = request.session.get('user_id')

        if input_code == saved_code:
            try:
                user = CustomUser.objects.get(id=user_id)
                return Response({"username": user.username}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "인증 코드가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        input_code = request.data.get('code')
        saved_code = request.session.get('verification_code')
        user_id = request.session.get('user_id')

        if input_code == saved_code:
            try:
                user = CustomUser.objects.get(id=user_id)
                return Response({
                    "message": "인증 성공. 새 비밀번호를 입력하세요.",
                    "username": user.username
                }, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "인증 코드가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)
        
class ResetPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        saved_code = request.session.get('verification_code')
        user_id = request.session.get('user_id')

        if new_password != confirm_password:
            return Response({"error": "비밀번호가 일치하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)

        if saved_code:
            try:
                user = CustomUser.objects.get(id=user_id)
                user.password = make_password(new_password)
                user.save()

                del request.session['verification_code']
                del request.session['user_id']

                return Response({"detail": "비밀번호가 성공적으로 재설정되었습니다."}, status=status.HTTP_200_OK)
            except CustomUser.DoesNotExist:
                return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"error": "유효하지 않은 요청입니다."}, status=status.HTTP_400_BAD_REQUEST)