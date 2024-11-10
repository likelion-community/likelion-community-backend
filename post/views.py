from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import action
from .models import *
from .serializers import *
from home.models import Notification
from home.serializers import NotificationSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

# 알림 한번에
def send_notification(notification):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{notification.user.id}',
        {
            'type': 'send_notification',
            'message': NotificationSerializer(notification).data
        }
    )

class BaseBoardViewSet(viewsets.ModelViewSet):
    def handle_like(self, request, post):
        user = request.user
        liked = not user in post.like.all()
        
        if liked:
            post.like.add(user)
        else:
            post.like.remove(user)
        return liked

    def handle_scrap(self, request, post):
        user = request.user
        scraped = not user in post.scrap.all()
        
        if scraped:
            post.scrap.add(user)
        else:
            post.scrap.remove(user)
        return scraped

    @action(detail=True, methods=['post'])
    def likes(self, request, pk=None):
        try:
            post = self.get_object()
            liked = self.handle_like(request, post)

            if liked:
                notification = Notification.objects.create(
                    user=post.writer,
                    message=f"'{post.title}' 게시글에 좋아요가 달렸습니다.",
                    related_board=post
                )
                send_notification(notification)

            return Response({'liked': liked, 'like_count': post.like.count()}, status=status.HTTP_200_OK)
        except self.queryset.model.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['post'])
    def scraps(self, request, pk=None):
        try:
            post = self.get_object()
            scraped = self.handle_scrap(request, post)
            return Response({'scraped': scraped, 'scrap_count': post.scrap.count()}, status=status.HTTP_200_OK)
        except self.queryset.model.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

class MainBoardViewSet(BaseBoardViewSet):
    queryset = MainBoard.objects.all()
    serializer_class = MainBoardSerializer

class SchoolBoardViewSet(BaseBoardViewSet):
    queryset = SchoolBoard.objects.all()
    serializer_class = SchoolBoardSerializer

class QuestionBoardViewSet(BaseBoardViewSet):
    queryset = QuestionBoard.objects.all()
    serializer_class = QuestionBoardSerializer

class CommentViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        comment = serializer.save()
        
        if comment.writer != comment.board.writer:
            notification = Notification.objects.create(
                user=comment.board.writer,
                message=f"'{comment.board.title}' 게시글에 댓글이 달렸습니다.",
                related_board=comment.board
            )
            send_notification(notification)

class MainCommentViewSet(CommentViewSet):
    queryset = MainComment.objects.all()
    serializer_class = MainCommentSerializer

class SchoolCommentViewSet(CommentViewSet):
    queryset = SchoolComment.objects.all()
    serializer_class = SchoolCommentSerializer

class QuestionCommentViewSet(CommentViewSet):
    queryset = QuestionComment.objects.all()
    serializer_class = QuestionCommentSerializer

class PopularPostViewSet(APIView):
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        term = now - timedelta(days=1)

        popular_posts = MainBoard.objects.filter(time__gte=term).order_by('-like')[:2]
        serializer = MainBoardSerializer(popular_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
