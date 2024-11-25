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
    def perform_create(self, serializer):
        post = serializer.save(writer=self.request.user)

        # 이미지 데이터 처리
        images = self.request.FILES.getlist('images')
        for image in images:
            PostImage.objects.create(board=post, image=image) 

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
    queryset = MainBoard.objects.all().order_by('-time')
    serializer_class = MainBoardSerializer

class SchoolBoardViewSet(BaseBoardViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    serializer_class = SchoolBoardSerializer
    queryset = SchoolBoard.objects.all().order_by('-time')

    def get_queryset(self):
        user = self.request.user
        return SchoolBoard.objects.filter(school_name=user.school_name).order_by('-time')

    def perform_create(self, serializer):
        serializer.save(writer=self.request.user, school_name=self.request.user.school_name)


class QuestionBoardViewSet(BaseBoardViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup]
    queryset = QuestionBoard.objects.all().order_by('-time')
    serializer_class = QuestionBoardSerializer

    def get_queryset(self):
        user = self.request.user
        # 사용자의 school_name과 일치하는 게시글만 반환
        return QuestionBoard.objects.filter(writer__school_name=user.school_name).order_by('-time')

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(writer=user, school_name=user.school_name)



class MainNoticeBoardViewSet(BaseBoardViewSet):
    permission_classes = [IsAuthenticated, IsAdminorReadOnly]
    queryset = MainNoticeBoard.objects.all().order_by('-time')
    serializer_class = MainNoticeBoardSerializer


class SchoolNoticeBoardViewSet(BaseBoardViewSet):
    permission_classes = [IsAuthenticated, IsSchoolVerifiedAndSameGroup, IsStaffOrReadOnly]
    serializer_class = SchoolNoticeBoardSerializer

    def get_queryset(self):
        user = self.request.user
        # 사용자의 school_name과 일치하는 게시글만 반환
        return SchoolNoticeBoard.objects.filter(school_name=user.school_name).order_by('-time')

    def perform_create(self, serializer):
        # 게시글 생성 시 작성자의 school_name을 저장
        serializer.save(writer=self.request.user, school_name=self.request.user.school_name)


class CommentViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        writer = self.request.user
        comment = serializer.save(writer=writer)
        
        if comment.writer != comment.board.writer:
            notification = Notification.objects.create(
                user=comment.board.writer,
                message=f"'{comment.board.title}' 게시글에 댓글이 달렸습니다.",
                related_board=comment.board
            )
            send_notification(notification)

    def get_queryset(self):
        board_id = self.request.query_params.get('board_id')
        if board_id:
            return self.queryset.filter(board_id=board_id)
        return self.queryset

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
        # time_threshold = timezone.now() - timezone.timedelta(hours=24)
        
        # MainBoard 각 카테고리별로 24시간 내 작성된 게시물 중 like가 가장 많은 게시물 가져오기
        for board_type, _ in MainBoard.BOARD_CHOICES:
            #post = (MainBoard.objects.filter(board_title=board_type, time__gte=time_threshold)
            post = (MainBoard.objects.filter(board_title=board_type)
                    .annotate(likes_count=Count('like'), scraps_count=Count('scrap'))
                    .order_by('-likes_count', '-time')
                    .first())
                
            if post:
                top_posts.append(post)
        
        # MainNoticeBoard에서 24시간 내 작성된 게시물 중 like가 가장 많은 게시물 가져오기
        for board_type, _ in MainNoticeBoard.BOARD_CHOICES:
            #notice_post = (MainNoticeBoard.objects.filter(board_title=board_type, time__gte=time_threshold)
            notice_post = (MainNoticeBoard.objects.filter(board_title=board_type)
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
    user = request.user
    try:
        # 사용자의 school_name과 일치하는 가장 최신 공지사항 반환
        latest_notice = SchoolNoticeBoard.objects.filter(school_name=user.school_name).latest('time')
        serializer = SchoolNoticeBoardSerializer(latest_notice)
        return Response(serializer.data)
    except SchoolNoticeBoard.DoesNotExist:
        return Response({'detail': 'No notices available.'}, status=404)


# 메인 커뮤니티 가장 최근 글 반환
@api_view(['GET'])
def latest_main_board(request):
    board_choices = [
        '자유게시판',
        '기획/디자인 게시판',
        '프론트엔드 게시판',
        '백엔드 게시판',
        '아기사자게시판',
        '참여게시판'
    ]

    latest_posts = []

    for board_title in board_choices:
        latest_post = MainBoard.objects.filter(board_title=board_title).order_by('-time').first()
        if latest_post:
            latest_posts.append(latest_post)

    # 시리얼라이즈 모든 최신 게시물
    serializer = MainBoardSerializer(latest_posts, many=True)
    return Response(serializer.data)

# 학교 커뮤니티 최근 게시물 3개 반환
@api_view(['GET'])
def latest_school_board(request):
    user = request.user
    latest_posts = SchoolBoard.objects.filter(school_name=user.school_name).order_by('-time')[:3]
    if latest_posts.exists():
        serializer = SchoolBoardSerializer(latest_posts, many=True)
        return Response(serializer.data)
    else:
        return Response({'detail': 'No notices available.'}, status=404)


@api_view(['GET'])
def latest_question_board(request):
    latest_posts = QuestionBoard.objects.order_by('-time')[:3]
    if latest_posts.exists():
        serializer = QuestionBoardSerializer(latest_posts, many=True)
        return Response(serializer.data)
    else:
        return Response({'detail': 'No notices available.'}, status=404)