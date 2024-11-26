from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.conf import settings
from .views import *
from . import views

router = DefaultRouter()

# 기존 게시판 및 댓글 ViewSet 등록
router.register(r'mainboard', MainBoardViewSet, basename='mainboard')
router.register(r'schoolboard', SchoolBoardViewSet, basename='schoolboard')
router.register(r'questionboard', QuestionBoardViewSet, basename='questionboard')
router.register(r'mainnoticeboard', MainNoticeBoardViewSet, basename='mainnoticeboard')
router.register(r'schoolnoticeboard', SchoolNoticeBoardViewSet, basename='schoolnoticeboard')

router.register(r'maincomment', MainCommentViewSet, basename='maincomment')
router.register(r'schoolcomment', SchoolCommentViewSet, basename='schoolcomment')
router.register(r'questioncomment', QuestionCommentViewSet, basename='questioncomment')
router.register(r'mainnoticecomment', MainNoticeCommentViewSet, basename='mainnoticecomment')
router.register(r'schoolnoticecomment', SchoolNoticeCommentViewSet, basename='schoolnoticecomment')

app_name = 'post'

urlpatterns = [
    path('', include(router.urls)),

    # 댓글 작성 시 게시글 ID를 URL 경로에서 전달받는 엔드포인트 추가
    path('schoolcomment/<int:post_id>/', SchoolCommentViewSet.as_view({'post': 'create'}), name='schoolcomment-create'),
    path('maincomment/<int:post_id>/', MainCommentViewSet.as_view({'post': 'create'}), name='maincomment-create'),
    path('questioncomment/<int:post_id>/', QuestionCommentViewSet.as_view({'post': 'create'}), name='questioncomment-create'),
    path('mainnoticecomment/<int:post_id>/', MainNoticeCommentViewSet.as_view({'post': 'create'}), name='mainnoticecomment-create'),
    path('schoolnoticecomment/<int:post_id>/', SchoolNoticeCommentViewSet.as_view({'post': 'create'}), name='schoolnoticecomment-create'),

    # 기타 엔드포인트
    path('popularposts/', PopularPostViewSet.as_view(), name='popularposts'),
    path('latest-main-notice/', views.latest_main_notice, name='latest-main-notice'),
    path('latest-school-notice/', views.latest_school_notice, name='latest-school-notice'),
    path('latest-main-board/', views.latest_main_board, name='latest-main-board'),
    path('latest-school-board/', views.latest_school_board, name='latest-school-board'),
    path('latest-question-board/', views.latest_question_board, name='latest-question-board'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
