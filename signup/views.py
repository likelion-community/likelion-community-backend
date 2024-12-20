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
from django.middleware.csrf import get_token
from django.middleware.csrf import rotate_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_protect


logger = logging.getLogger(__name__)


class LoginHomeAPIView(APIView):
    permission_classes = [AllowAny]  # 누구나 접근 가능하게 설정

    def get(self, request):
        return Response({
            'message': '로그인 유형을 선택하세요.',
            'kakao_login_url': '/signup/login/kakao/',
            'custom_login_url': '/signup/login/custom/'
        }, status=status.HTTP_200_OK)

from django.utils.decorators import method_decorator

@method_decorator(ensure_csrf_cookie, name='dispatch')
class KakaoLoginAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        if request.user.is_authenticated:
            if not request.user.is_profile_complete:
                request.session['partial_pipeline_user'] = request.user.pk
                return redirect('signup:complete_profile')
            
            return JsonResponse({'message': '카카오 로그인 성공', 'redirect_url': '/home/mainpage'})
        
        # 세션 갱신 확인
        request.session.modified = True

        # 카카오 백엔드 로드 및 인증 URL로 리디렉션하는 부분은 그대로 둡니다.
        strategy = load_strategy(request)
        backend = load_backend(strategy, 'kakao', redirect_uri=settings.SOCIAL_AUTH_KAKAO_REDIRECT_URI)
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
                request.session.save()
                return JsonResponse({'message': '로그인 성공'}, status=status.HTTP_200_OK)

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


@method_decorator(csrf_protect, name='dispatch')
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

# Session clearing API view
class ClearIncompleteSessionAPIView(APIView):
    def post(self, request):
        if 'partial_pipeline_user' in request.session:
            del request.session['partial_pipeline_user']
            return Response({"message": "세션 데이터가 초기화되었습니다."}, status=status.HTTP_200_OK)
        return Response({"message": "삭제할 세션 데이터가 없습니다."}, status=status.HTTP_200_OK)

# 사진 유효성 검사 API 뷰
@api_view(['POST'])
@permission_classes([AllowAny])
def photo_validation_view(request):
    print("사진 유효성 검사 뷰 호출됨.")
    uploaded_image = request.FILES.get('verification_photo')

    if not uploaded_image:
        print("업로드된 이미지 파일이 없음.")
        return JsonResponse({'error': '사진 파일이 필요합니다.'}, status=400)

    # 유효성 검사 로직 호출 및 결과 출력
    try:
        is_verified = verify_like_a_lion_member(uploaded_image)
        request.session['photo_verified'] = is_verified
        return JsonResponse({'is_valid': bool(is_verified)})

    except Exception as e:
        print(f"사진 유효성 검사 중 오류 발생: {str(e)}")
        return JsonResponse({'error': '사진 유효성 검사 중 오류가 발생했습니다.'}, status=500)



class CompleteProfileAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_id = request.session.get('partial_pipeline_user')
        if not user_id:
            return redirect("https://localhost:5173/kakaoSignup")

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            request.session.pop('partial_pipeline_user', None)
            return redirect("https://localhost:5173/kakaoSignup")

        if user.is_profile_complete:
            user.backend = 'social_core.backends.kakao.KakaoOAuth2'
            login(request, user)
            request.session.save()
            return redirect("https://localhost:5173/main")

        # 세션에 저장된 닉네임을 가져와 쿼리 파라미터로 전달
        nickname = request.session.get('nickname')
        if nickname:
            # 닉네임을 쿼리 파라미터로 포함하여 리디렉션
            return redirect(f"https://localhost:5173/kakaoSignup?nickname={nickname}")
        
        # 닉네임이 없는 경우 기본 리디렉션
        return redirect("https://localhost:5173/kakaoSignup")
        

    def post(self, request):
        print("post가 시작")
        user_id = request.session.get('partial_pipeline_user')
        if not user_id:
            return Response({'error': "세션이 만료되었습니다. 다시 로그인해주세요."}, status=status.HTTP_403_FORBIDDEN)

        try:
            user = CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            request.session.pop('partial_pipeline_user', None)
            return Response({'error': "사용자가 존재하지 않습니다. 다시 로그인해주세요."}, status=status.HTTP_403_FORBIDDEN)

        if user.is_profile_complete:
            user.backend = 'social_core.backends.kakao.KakaoOAuth2'
            login(request, user)
            request.session.save()
            return redirect("https://localhost:5173/main")

        # 이미지가 업로드되지 않은 경우 오류 메시지 반환
        uploaded_image = request.FILES.get('verification_photo')
        if not uploaded_image:
            return Response({'error': "회원 인증 이미지를 업로드해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)

        # 유효성 검사가 완료되지 않았으면 오류 반환
        if not request.session.get('photo_verified'):
            return Response({'error': "사진 유효성 검사를 먼저 완료해주세요."}, status=status.HTTP_400_BAD_REQUEST)

        # 유효성 검사를 통과한 경우 추가 정보 저장
        serializer = AdditionalInfoSerializer(data=request.data, instance=user)
        if serializer.is_valid():
            serializer.save()
            user.is_profile_complete = True
            user.verification_photo = uploaded_image
            user.save()
            
            user.backend = 'social_core.backends.kakao.KakaoOAuth2'
            login(request, user)
            request.session.save()
            request.session.pop('partial_pipeline_user', None)
            request.session.pop('photo_verified', None)
            return Response({'is_valid': True, 'message': "프로필이 성공적으로 완성되었습니다."}, status=status.HTTP_200_OK)
        else:
            return Response({'is_valid': False, 'errors': serializer.errors, 'message': "프로필 업데이트 중 오류가 발생했습니다."}, status=status.HTTP_400_BAD_REQUEST)

    
    
    
    
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


@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        csrf_token = get_token(request)
        return JsonResponse({'csrfToken': csrf_token})
