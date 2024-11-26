from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout
from django.middleware.csrf import CsrfViewMiddleware

class CompleteProfileRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 관리자는 검사 없이 통과
        if request.user.is_authenticated and request.user.is_superuser:
            return None

        if request.user.is_authenticated:
            if request.user.is_profile_complete:
                return None  # 프로필이 완료된 경우 아무 작업 없이 통과

            # 프로필이 미완료된 경우 로그인 페이지로 리디렉션
            if request.path != reverse('signup:complete_profile'):
                print("User profile not complete, redirecting to login.")
                logout(request)
                return redirect('signup:login_home')

        return None


class CustomCsrfViewMiddleware(CsrfViewMiddleware):
    """
    CSRF 검증 실패 시 추가 디버깅 로그를 출력하는 Custom Middleware
    """
    def process_view(self, request, callback, callback_args, callback_kwargs):
        print("CSRF 검증 이전 단계")
        print("요청 메서드:", request.method)
        print("요청 경로:", request.path)
        print("요청 헤더:", dict(request.headers))
        return super().process_view(request, callback, callback_args, callback_kwargs)

    def _reject(self, request, reason):
        print("CSRF 검증 실패 이유:", reason)
        print("요청 메서드:", request.method)
        print("요청 경로:", request.path)
        print("요청 헤더:", dict(request.headers))
        return super()._reject(request, reason)
    

class CompleteProfileRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        print("CompleteProfileRequiredMiddleware: 요청 처리 시작")
        print("요청 사용자:", request.user)
        print("요청 경로:", request.path)

        if request.user.is_authenticated and request.user.is_superuser:
            print("관리자는 통과")
            return None

        if request.user.is_authenticated:
            if request.user.is_profile_complete:
                print("프로필이 완료된 사용자, 통과")
                return None

            print("프로필 미완료 사용자, 리디렉션")
            if request.path != reverse('signup:complete_profile'):
                logout(request)
                return redirect('signup:login_home')

        return None
