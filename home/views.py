# home/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class HomeAPIView(APIView):
    permission_classes = [IsAuthenticated]  # 로그인된 사용자만 접근 가능

    def get(self, request):
        user = request.user
        data = {
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'nickname': user.nickname,
            'membership_term': user.membership_term,
        }
        return Response(data)
