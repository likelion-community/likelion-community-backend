from rest_framework import viewsets
from .models import *
from .serializers import *
from home.models import Notification
from home.serializers import NotificationSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

# Create your views here.
class MainBoardViewSet(viewsets.ModelViewSet):
    queryset = MainBoard.objects.all()
    serializer_class = MainBoardSerializer

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        main_board = self.get_object()
        main_board.like += 1
        main_board.save()

        # 알림 생성
        notification = Notification.objects.create(
            user=main_board.writer,
            message=f"'{main_board.title}' 게시글에 좋아요가 달렸습니다.",
            related_board=main_board
        )

        # WebSocket을 통해 실시간 알림 전송
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{notification.user.id}',  # 유저별 그룹명
            {
                'type': 'send_notification',
                'message': NotificationSerializer(notification).data
            }
        )

        return Response({"status": "liked"}, status=status.HTTP_200_OK)
    


class SchoolBoardViewSet(viewsets.ModelViewSet):
    queryset = SchoolBoard.objects.all()
    serializer_class = SchoolBoardSerializer

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        school_board = self.get_object()
        school_board.like += 1
        school_board.save()

        # 알림 생성
        notification = Notification.objects.create(
            user=school_board.writer,
            message=f"'{school_board.title}' 게시글에 좋아요가 달렸습니다.",
            related_board=school_board
        )

        # WebSocket을 통해 실시간 알림 전송
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{notification.user.id}',  # 유저별 그룹명
            {
                'type': 'send_notification',
                'message': NotificationSerializer(notification).data
            }
        )

        return Response({"status": "liked"}, status=status.HTTP_200_OK)
    

class MainCommentViewSet(viewsets.ModelViewSet):
    queryset = MainComment.objects.all()
    serializer_class = MainCommentSerializer

    def perform_create(self, serializer):
        main_comment = serializer.save()
        
        # 알림 생성 (댓글 작성자와 게시글 작성자가 다를 때만)
        if main_comment.writer != main_comment.board.writer:
            notification = Notification.objects.create(
                user=main_comment.board.writer,
                message=f"'{main_comment.board.title}' 게시글에 댓글이 달렸습니다.",
                related_board=main_comment.board
            )

            # WebSocket을 통해 실시간 알림 전송
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications_{notification.user.id}',
                {
                    'type': 'send_notification',
                    'message': NotificationSerializer(notification).data
                }
            )

class SchoolCommentViewSet(viewsets.ModelViewSet):
    queryset = SchoolComment.objects.all()
    serializer_class = SchoolCommentSerializer

    def perform_create(self, serializer):
        school_comment = serializer.save()
        
        # 알림 생성 (댓글 작성자와 게시글 작성자가 다를 때만)
        if school_comment.writer != school_comment.board.writer:
            notification = Notification.objects.create(
                user=school_comment.board.writer,
                message=f"'{school_comment.board.title}' 게시글에 댓글이 달렸습니다.",
                related_school_board=school_comment.board
            )

            # WebSocket을 통해 실시간 알림 전송
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications_{notification.user.id}',
                {
                    'type': 'send_notification',
                    'message': NotificationSerializer(notification).data
                }
            )