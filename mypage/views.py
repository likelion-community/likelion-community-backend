from django.shortcuts import render
from django.urls import reverse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from signup.models import CustomUser
from .serializers import *
from post.models import MainBoard, SchoolBoard, QuestionBoard
from post.serializers import MainBoardSerializer, SchoolBoardSerializer, QuestionBoardSerializer
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.conf import settings
from .serializers import UserSerializer

from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.urls import reverse

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

        return Response({
            "user_info": user_serializer.data,
            "school_verification_status": verification.school_status if verification else "none",
            "executive_verification_status": verification.executive_status if verification else "none",
            "school_name": user.school_name if verification and verification.school_status == "approved" else None,
            "track": verification.track if verification and verification.school_status == "approved" else None,
            "profile_image_update": request.build_absolute_uri(reverse('mypage:profileimage')),
            "my_scraps": request.build_absolute_uri(reverse('mypage:myscraps')),
            "my_posts": request.build_absolute_uri(reverse('mypage:myposts')),
            "my_comments": request.build_absolute_uri(reverse('mypage:mycomments')),
            "school_verification": request.build_absolute_uri(reverse('mypage:schoolverification')),
            "executive_verification": request.build_absolute_uri(reverse('mypage:executiveverification')),
        }, status=status.HTTP_200_OK)


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

        mainscrap_serializer = MainBoardSerializer(mainscrap, many=True)
        schoolscrap_serializer = SchoolBoardSerializer(schoolscrap, many=True)
        questionscrap_serializer = QuestionBoardSerializer(questionscrap, many=True)

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

        mainpost_serializer = MainBoardSerializer(mainpost, many=True)
        schoolpost_serializer = SchoolBoardSerializer(schoolpost, many=True)
        questionpost_serializer = QuestionBoardSerializer(questionpost, many=True)

        return Response({
            "mainscrap": mainpost_serializer.data,
            "schoolscrap": schoolpost_serializer.data,
            "questionscrap": questionpost_serializer.data
        }, status=status.HTTP_200_OK)
    
class MyCommentView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user

        maincomment = MainBoard.objects.filter(writer=user)
        schoolcomment = SchoolBoard.objects.filter(writer=user)
        questioncomment = QuestionBoard.objects.filter(writer=user)

        maincomment_serializer = MainBoardSerializer(maincomment, many=True)
        schoolcomment_serializer = SchoolBoardSerializer(schoolcomment, many=True)
        questioncomment_serializer = QuestionBoardSerializer(questioncomment, many=True)

        return Response({
            "mainscrap": maincomment_serializer.data,
            "schoolscrap": schoolcomment_serializer.data,
            "questionscrap": questioncomment_serializer.data
        }, status=status.HTTP_200_OK)


 #사용자가 이미 인증 정보를 가지고 있는 경우 기존 객체를 업데이트하도록 수정   
class VerificationStatusView(APIView):
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

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = VerificationSerializer(data=request.data, context={'user': user})

        if serializer.is_valid():
            try:
                # 기존 인증 요청이 있는 경우 업데이트, 없는 경우 생성
                verification, created = Verification.objects.get_or_create(user=user)
                for field, value in serializer.validated_data.items():
                    setattr(verification, field, value)
                verification.save()

                return Response({
                    "detail": "인증 요청이 성공적으로 제출되었습니다.",
                    "verification_status": VerificationSerializer(verification).data
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"error": f"인증 요청 중 오류가 발생했습니다: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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