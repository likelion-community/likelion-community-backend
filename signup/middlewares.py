# signup/middlewares.py
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout

print("Middleware file is loaded")

class CompleteProfileRequiredMiddleware(MiddlewareMixin):
    def process_request(self, request):
        
        if request.user.is_authenticated:
            
            if request.user.is_profile_complete:
                return None  # 프로필이 완료된 경우 아무 작업 없이 통과
            
            if request.path != reverse('signup:complete_profile'):
                print("User profile not complete, redirecting to login.")
                logout(request)
                return redirect('signup:login_home')

        return None
