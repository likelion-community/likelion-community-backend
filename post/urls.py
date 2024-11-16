from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.conf import settings
from .views import *
from . import views

router = DefaultRouter()
router.register(r'mainboard', MainBoardViewSet)
router.register(r'schoolboard', SchoolBoardViewSet)
router.register(r'questionboard', QuestionBoardViewSet)
router.register(r'mainnoticeboard', MainNoticeBoardViewSet)
router.register(r'schoolnoticeboard', SchoolNoticeBoardViewSet)

router.register(r'maincomment', MainCommentViewSet)
router.register(r'schoolcomment', SchoolCommentViewSet)
router.register(r'questioncomment', QuestionCommentViewSet)
router.register(r'mainnoticecomment', MainNoticeCommentViewSet)
router.register(r'schoolnoticecomment', SchoolNoticeCommentViewSet)

app_name = 'post'

urlpatterns = [
    path('', include(router.urls)),
    path('popularposts/', PopularPostViewSet.as_view(), name='popularposts'),
    path('latest-main-notice/', views.latest_main_notice, name='latest-main-notice'),
    path('latest-school-notice/', views.latest_school_notice, name='latest-school-notice'),
    path('latest-main-board/', views.latest_main_board, name='latest-main-board'),
    path('latest-school-board/', views.latest_school_board, name='latest-school-board'),
    path('latest-question-board/', views.latest_question_board, name='latest-question-board'),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)