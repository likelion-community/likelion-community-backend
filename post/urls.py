from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.conf import settings
from .views import *

router = DefaultRouter()
router.register(r'mainboard', MainBoardViewSet)
router.register(r'schoolboard', SchoolBoardViewSet)
router.register(r'questionboard', QuestionBoardViewSet)
router.register(r'maincomment', MainCommentViewSet)
router.register(r'schoolcomment', SchoolCommentViewSet)
router.register(r'questioncomment', QuestionCommentViewSet)

app_name = 'post'

urlpatterns = [
    path('', include(router.urls)),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)