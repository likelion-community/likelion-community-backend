# home/views.py
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect


class HomeAPIView(APIView):
    permission_classes = [AllowAny]  # 모든 사용자가 접근 가능하도록 설정

    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('/signup/login/home/')
        
        user = request.user
        data = {
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'nickname': user.nickname,
            'membership_term': user.membership_term,
        }
        return Response(data)