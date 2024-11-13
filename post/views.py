from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils import timezone
from rest_framework.decorators import action, api_view
from .models import *
from .serializers import *
from home.models import Notification
from home.serializers import NotificationSerializer
from rest_framework.permissions import IsAuthenticated
from attendance.permissions import IsStaffOrReadOnly, IsSchoolVerifiedAndSameGroup, IsAdminorReadOnly
from django.db.models import Count, Max
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
                    #related_board=post
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
    permission_classes = [IsAuthenticated]
    queryset = MainBoard.objects.all()
    serializer_class = MainBoardSerializer

class SchoolBoardViewSet(BaseBoardViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    queryset = SchoolBoard.objects.all()
    serializer_class = SchoolBoardSerializer

class QuestionBoardViewSet(BaseBoardViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    queryset = QuestionBoard.objects.all()
    serializer_class = QuestionBoardSerializer

class MainNoticeBoardViewSet(BaseBoardViewSet):
    permission_classes = [IsAuthenticated, IsAdminorReadOnly]
    queryset = MainNoticeBoard.objects.all()
    serializer_class = MainNoticeBoardSerializer

class SchoolNoticeBoardViewSet(BaseBoardViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup, IsStaffOrReadOnly]
    queryset = SchoolNoticeBoard.objects.all()
    serializer_class = SchoolNoticeBoardSerializer

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
    permission_classes = [IsAuthenticated]
    queryset = MainComment.objects.all()
    serializer_class = MainCommentSerializer

class SchoolCommentViewSet(CommentViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    queryset = SchoolComment.objects.all()
    serializer_class = SchoolCommentSerializer

class QuestionCommentViewSet(CommentViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    queryset = QuestionComment.objects.all()
    serializer_class = QuestionCommentSerializer

class MainNoticeCommentViewSet(CommentViewSet):
    permission_classes = [IsAuthenticated]
    queryset = MainNoticeComment.objects.all()
    serializer_class = MainNoticeCommentSerializer

class SchoolNoticeCommentViewSet(CommentViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    queryset = SchoolNoticeComment.objects.all()
    serializer_class = SchoolNoticeCommentSerializer

# 인기글 반환
class PopularPostViewSet(APIView):
    def get(self, request):
        top_posts = []
        
        # 현재 시간으로부터 24시간 전
        time_threshold = timezone.now() - timezone.timedelta(hours=24)
        
        # MainBoard 각 카테고리별로 24시간 내 작성된 게시물 중 like가 가장 많은 게시물 가져오기
        for board_type, _ in MainBoard.BOARD_CHOICES:
            post = (MainBoard.objects.filter(board_title=board_type, time__gte=time_threshold)
                    .annotate(likes_count=Count('like'), scraps_count=Count('scrap'))
                    .order_by('-likes_count', '-time')
                    .first())
            
            if post:
                top_posts.append(post)
        
        # MainNoticeBoard에서 24시간 내 작성된 게시물 중 like가 가장 많은 게시물 가져오기
        for board_type, _ in MainNoticeBoard.BOARD_CHOICES:
            notice_post = (MainNoticeBoard.objects.filter(board_title=board_type, time__gte=time_threshold)
                           .annotate(likes_count=Count('like'), scraps_count=Count('scrap'))
                           .order_by('-likes_count', '-time')
                           .first())
            
            if notice_post:
                top_posts.append(notice_post)
        
        # 직렬화를 통해 응답 데이터 반환
        data = []
        for post in top_posts:
            if isinstance(post, MainBoard):
                serializer = MainBoardSerializer(post)
            else:
                serializer = MainNoticeBoardSerializer(post)
            data.append(serializer.data)
        
        return Response(data)
    
# 가장 최근 공지 반환
@api_view(['GET'])
def latest_main_notice(request):
    try:
        latest_notice = MainNoticeBoard.objects.latest('time')
        serializer = MainNoticeBoardSerializer(latest_notice)
        return Response(serializer.data)
    except MainNoticeBoard.DoesNotExist:
        return Response({'detail': 'No notices available.'}, status=404)
    
@api_view(['GET'])
def latest_school_notice(request):
    try:
        latest_notice = SchoolNoticeBoard.objects.latest('time')
        serializer = SchoolNoticeBoardSerializer(latest_notice)
        return Response(serializer.data)
    except SchoolNoticeBoard.DoesNotExist:
        return Response({'detail': 'No notices available.'}, status=404)