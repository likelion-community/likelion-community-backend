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
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status

# Create your views here.
class MainBoardViewSet(viewsets.ModelViewSet):
    queryset = MainBoard.objects.all()
    serializer_class = MainBoardSerializer

    @action(detail=True, methods=['post'])
    def likes(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.like.all():
                post.like.remove(user)
                liked = False
            else:
                post.like.add(user)
                liked = True

            post.save()

            # 알림 생성
            notification = Notification.objects.create(
            user=post.writer,
            message=f"'{post.title}' 게시글에 좋아요가 달렸습니다.",
            related_board=post
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
            return Response({'liked': liked, 'like_count': post.like.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
    @action(detail=True, methods=['post'])
    def scraps(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.scrap.all():
                post.scrap.remove(user)
                scraped = False
            else:
                post.scrap.add(user)
                scraped = True

            post.save()
            return Response({'scraped': scraped, 'scrap_count': post.scrap.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

class SchoolBoardViewSet(viewsets.ModelViewSet):
    queryset = SchoolBoard.objects.all()
    serializer_class = SchoolBoardSerializer

    @action(detail=True, methods=['post'])
    def likes(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.like.all():
                post.like.remove(user)
                liked = False
            else:
                post.like.add(user)
                liked = True

            post.save()

            # 알림 생성
            notification = Notification.objects.create(
            user=post.writer,
            message=f"'{post.title}' 게시글에 좋아요가 달렸습니다.",
            related_board=post
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
            return Response({'liked': liked, 'like_count': post.like.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['post'])
    def scraps(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.scrap.all():
                post.scrap.remove(user)
                scraped = False
            else:
                post.scrap.add(user)
                scraped = True

            post.save()
            return Response({'scraped': scraped, 'scrap_count': post.scrap.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

class QuestionBoardViewSet(viewsets.ModelViewSet):
    queryset = QuestionBoard.objects.all()
    serializer_class = QuestionBoardSerializer

    @action(detail=True, methods=['post'])
    def likes(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.like.all():
                post.like.remove(user)
                liked = False
            else:
                post.like.add(user)
                liked = True

            post.save()

            # 알림 생성
            notification = Notification.objects.create(
            user=post.writer,
            message=f"'{post.title}' 게시글에 좋아요가 달렸습니다.",
            related_board=post
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
            return Response({'liked': liked, 'like_count': post.like.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=['post'])
    def scraps(self, request, pk=None):
        try:
            post = self.get_object()
            user = request.user

            if user in post.scrap.all():
                post.scrap.remove(user)
                scraped = False
            else:
                post.scrap.add(user)
                scraped = True

            post.save()
            return Response({'scraped': scraped, 'scrap_count': post.scrap.count()}, status=status.HTTP_200_OK)
        except MainBoard.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

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

class QuestionCommentViewSet(viewsets.ModelViewSet):
    queryset = QuestionComment.objects.all()
    serializer_class = QuestionCommentSerializer

    def perform_create(self, serializer):
        question_comment = serializer.save()
        
        # 알림 생성 (댓글 작성자와 게시글 작성자가 다를 때만)
        if question_comment.writer != question_comment.board.writer:
            notification = Notification.objects.create(
                user=question_comment.board.writer,
                message=f"'{question_comment.board.title}' 게시글에 댓글이 달렸습니다.",
                related_school_board=question_comment.board
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

class PopularPostViewSet(APIView):
    def get(self, request, *args, **kwargs):
        now = timezone.now()
        term = now - timedelta(days=1)

        popular_posts = MainBoard.objects.filter(time__gte=term).order_by('-like')[:2]
        serializer = MainBoardSerializer(popular_posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)