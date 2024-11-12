# signup/views.py
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
import uuid
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect
from django.http import JsonResponse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.contrib import messages
from .serializers import CustomUserCreationSerializer, AdditionalInfoSerializer, CustomLoginSerializer
from .models import CustomUserToken, CustomUser
from ai_verifier import verify_like_a_lion_member
import logging
from rest_framework.permissions import AllowAny
from social_django.utils import load_strategy, load_backend
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from django.core.exceptions import ObjectDoesNotExist


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
        
        # 카카오 백엔드 로드
        strategy = load_strategy(request)
        backend = load_backend(strategy, 'kakao', redirect_uri=settings.SOCIAL_AUTH_KAKAO_REDIRECT_URI)

        # 카카오 인증 URL로 리디렉션
        auth_url = backend.auth_url()
        return redirect(auth_url)

class TokenLoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 기존 토큰이 있다면 반환, 없으면 생성
            token, created = CustomUserToken.objects.get_or_create(user=user)
            if not created:
                # 기존 토큰이 있는 경우 새로운 UUID로 갱신
                token.token = uuid.uuid4()
                token.save()
            return Response({'token': str(token.token), 'user_id': user.pk}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
        
class CustomLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data.get('username')
            password = serializer.validated_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return Response({'message': '로그인 성공'}, status=status.HTTP_200_OK)
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
                user = serializer.save()
                user.is_profile_complete = True  
                user.verification_photo = uploaded_image
                user.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error': '이미지 인증 실패'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CompleteProfileAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_id = request.session.get("partial_pipeline_user")
        if not user_id:
            return Response({"error": "세션이 만료되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(pk=user_id)
            if user.is_profile_complete:
                return redirect("https://localhost:5173/main")
            return Response({"nickname": user.nickname}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        user_id = request.session.get("partial_pipeline_user")
        if not user_id:
            return Response({"error": "세션이 만료되었습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(pk=user_id)
        except ObjectDoesNotExist:
            return Response({"error": "사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AdditionalInfoSerializer(data=request.data, instance=user)
        if serializer.is_valid():
            serializer.save()
            user.is_profile_complete = True
            user.save()
            login(request, user)
            return Response({"message": "추가 정보 입력이 완료되었습니다."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def photo_validation_view(request):
    uploaded_image = request.FILES.get('verification_photo')
    if not uploaded_image:
        return JsonResponse({'error': '사진 파일이 필요합니다.'}, status=400)

    # 사진 유효성 검사 로직 호출
    is_verified = verify_like_a_lion_member(uploaded_image)
    return JsonResponse({'is_valid': is_verified})

    
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
