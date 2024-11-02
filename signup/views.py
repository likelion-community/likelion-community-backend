# signup/views.py
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.contrib import messages
from .serializers import CustomUserCreationSerializer, AdditionalInfoSerializer, CustomLoginSerializer
from .models import CustomUser
from ai_verifier import verify_like_a_lion_member
import logging
from rest_framework.permissions import AllowAny


logger = logging.getLogger(__name__)


class LoginHomeAPIView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능하게 설정

    def get(self, request):
        return Response({
            'message': '로그인 유형을 선택하세요.',
            'kakao_login_url': '/signup/login/kakao/',
            'custom_login_url': '/signup/login/custom/'
        }, status=status.HTTP_200_OK)

class KakaoLoginAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        if request.user.is_authenticated:
            if not request.user.is_profile_complete:
                request.session['partial_pipeline_user'] = request.user.pk
                return redirect('signup:complete_profile')
            login(request, request.user)
            return redirect('home:mainpage')
        return redirect('signup:login_home')



class CustomLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # 이미 인증된 사용자인 경우
        if request.user.is_authenticated:
            # 슈퍼유저 또는 프로필이 완성된 사용자만 메인 페이지로 리디렉트
            if request.user.is_superuser or request.user.is_profile_complete:
                return redirect('home:mainpage')
            else:
                return redirect('signup:complete_profile')

        serializer = CustomLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                # 로그인 후 슈퍼유저는 프로필 검사 없이 통과
                if user.is_superuser or user.is_profile_complete:
                    return Response({'message': '로그인 성공'}, status=status.HTTP_200_OK)
                else:
                    return redirect('signup:complete_profile')
        return Response({'error': '아이디 또는 비밀번호가 잘못되었습니다.'}, status=status.HTTP_400_BAD_REQUEST)



class CheckPasswordAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        password = request.data.get('password')
        try:
            validate_password(password)
            return Response({'is_valid': True, 'message': '유효한 비밀번호입니다.'}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({'is_valid': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        request.session.flush()
        cache.clear()
        return Response({'message': '로그아웃 성공'}, status=status.HTTP_200_OK)

class SignupAPIView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # AJAX 요청인 경우 사진 유효성 검사
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            uploaded_image = request.FILES.get('verification_photo')
            is_verified = verify_like_a_lion_member(uploaded_image)
            return JsonResponse({'is_valid': bool(is_verified)})

        # 회원가입 시 모든 정보가 유효한지 확인
        serializer = CustomUserCreationSerializer(data=request.data)
        if serializer.is_valid():
            uploaded_image = request.FILES.get('verification_photo')
            is_verified = verify_like_a_lion_member(uploaded_image)
            if is_verified:
                # 프로필이 완성된 상태로 설정
                user = serializer.save(is_profile_complete=True)
                user.verification_photo = uploaded_image
                user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error': '이미지 인증 실패'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CompleteProfileAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        nickname = request.session.get('nickname')
        initial_data = {'nickname': nickname} if nickname else {}
        form_data = {'initial': initial_data}
        return Response(form_data, status=status.HTTP_200_OK)

    def post(self, request):
        user_id = request.session.get('partial_pipeline_user')
        if not user_id:
            return redirect('signup:login_home')

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            request.session.pop('partial_pipeline_user', None)
            return redirect('signup:login_home')

        if user.is_profile_complete:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home:mainpage')

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            uploaded_image = request.FILES.get('verification_photo')
            is_verified = verify_like_a_lion_member(uploaded_image)
            if is_verified:
                request.session['photo_verified'] = True
            return JsonResponse({'is_valid': bool(is_verified)})

        if request.session.get('photo_verified', False):
            serializer = AdditionalInfoSerializer(data=request.data, instance=user)
            if serializer.is_valid():
                user.is_profile_complete = True
                serializer.save()
                login(request, user, backend='social_core.backends.kakao.KakaoOAuth2')
                request.session.pop('partial_pipeline_user', None)
                request.session.pop('photo_verified', None)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        messages.error(request, "사진 유효성 검사에 실패했습니다. 다시 시도해 주세요.")
        return Response({'error': "사진 유효성 검사에 실패했습니다."}, status=status.HTTP_400_BAD_REQUEST)

class DeleteIncompleteUserAPIView(APIView):
    def delete(self, request):
        user_id = request.session.get('partial_pipeline_user')
        if user_id:
            user = CustomUser.objects.filter(pk=user_id, is_profile_complete=False).first()
            if user:
                user.delete()
                request.session.pop('partial_pipeline_user', None)
                logger.info(f"Deleted incomplete user: {user.username}")
        return Response({'message': '미완성 계정이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)

class DeleteUserAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        logout(request)
        request.session.flush()
        cache.clear()
        return Response({'message': '계정이 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
