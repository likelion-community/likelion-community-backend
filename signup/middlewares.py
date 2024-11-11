from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout


class CompleteProfileRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 관리자는 검사 없이 통과
        if request.user.is_authenticated and request.user.is_superuser:
            return None

        if request.user.is_authenticated:
            if request.user.is_profile_complete:
                return None  # 프로필이 완료된 경우 아무 작업 없이 통과

            # 프로필이 미완료된 경우 로그인 페이지로 리디렉션
            if request.path != '/kakaoSignup':
                print("User profile not complete, redirecting to login.")
                logout(request)
                return redirect('https://localhost:5173')

        return None
