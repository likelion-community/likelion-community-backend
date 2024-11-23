from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.conf import settings
from .views import *
from . import views

router = DefaultRouter()

# `basename` 추가
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
    path('popularposts/', PopularPostViewSet.as_view(), name='popularposts'),
    path('latest-main-notice/', views.latest_main_notice, name='latest-main-notice'),
    path('latest-school-notice/', views.latest_school_notice, name='latest-school-notice'),
    path('latest-main-board/', views.latest_main_board, name='latest-main-board'),
    path('latest-school-board/', views.latest_school_board, name='latest-school-board'),
    path('latest-question-board/', views.latest_question_board, name='latest-question-board'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
