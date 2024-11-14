# signup/urls.py
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import (
    LoginHomeAPIView, CustomLoginAPIView, SignupAPIView, CompleteProfileAPIView, ClearIncompleteSessionAPIView,
    LogoutAPIView, CheckPasswordAPIView, DeleteUserAPIView, TokenLoginAPIView, photo_validation_view, SetCSRFCookieView
)
from social_django import views as social_views

app_name = 'signup'

urlpatterns = [
    # 로그인 홈 (카카오, 일반 선택 화면)
    path('login/home/', LoginHomeAPIView.as_view(), name='login_home'),

    # 일반 로그인 및 로그아웃
    path('login/custom/', CustomLoginAPIView.as_view(), name='custom_login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('login/token/', TokenLoginAPIView.as_view(), name='token_login'),

    # 회원가입 및 프로필 완성
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('complete_profile/', CompleteProfileAPIView.as_view(), name='complete_profile'),
    path('photo_validation/', photo_validation_view, name='photo_validation'),
    path('clear_incomplete_session/', ClearIncompleteSessionAPIView.as_view(), name='clear_incomplete_session'),

    # 비밀번호 유효성 검사
    path('check-password/', CheckPasswordAPIView.as_view(), name='check_password'),  

    # 회원 탈퇴
    path('delete_user/', DeleteUserAPIView.as_view(), name='delete_user'),

    # 카카오 소셜 로그인
    path('login/kakao/', social_views.auth, name='kakao-login', kwargs={'backend': 'kakao'}),
    path('complete/kakao/', social_views.complete, name='kakao-complete', kwargs={'backend': 'kakao'}),
    path('set-csrf-cookie/', SetCSRFCookieView.as_view(), name='set_csrf_cookie'),
    
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
