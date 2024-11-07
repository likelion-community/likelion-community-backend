# home/views.py
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notification
from .serializers import NotificationSerializer


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
    


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False).order_by('-timestamp')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class MarkNotificationAsReadView(APIView):
    permission_classes = [IsAuthenticated]  # 인증된 사용자만 접근 가능

    def post(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"status": "읽은 알림"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "알림을 찾을 수 없음"}, status=status.HTTP_404_NOT_FOUND)


class DeleteNotificationView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            notification.delete()
            return Response({"status": "알림을 삭제함"}, status=status.HTTP_204_NO_CONTENT)
        except Notification.DoesNotExist:
            return Response({"error": "알림을 찾을 수 없음"}, status=status.HTTP_404_NOT_FOUND)
        