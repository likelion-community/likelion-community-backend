# home/views.py
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response

@method_decorator(login_required(login_url='/signup/login/home/'), name='dispatch')
class HomeAPIView(APIView):
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
