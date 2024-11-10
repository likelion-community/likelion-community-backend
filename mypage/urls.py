from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.conf import settings
from .views import *

app_name = 'mypage'

urlpatterns = [
    path('profileimage/', ProfileImageUpdateView.as_view(), name='profileimage'),
    path('myscraps/', MyScrapView.as_view(), name='myscraps'),
    path('schoolverification/', SchoolVerificationView.as_view(), name='schoolverification'),
    path('executiveverification/', ExecutiveVerificationView.as_view(), name='executiveverification'),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)