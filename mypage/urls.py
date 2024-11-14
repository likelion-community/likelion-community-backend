from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from django.conf import settings
from .views import *

app_name = 'mypage'

urlpatterns = [
    path('', MyPageOverviewView.as_view(), name='overview'), 
    path('profileimage/', ProfileImageUpdateView.as_view(), name='profileimage'),
    path('myscraps/', MyScrapView.as_view(), name='myscraps'),
    path('myposts/', MyPostView.as_view(), name='myposts'),
    path('mycomments/', MyCommentView.as_view(), name='mycomments'),
    path('schoolverification/', SchoolVerificationView.as_view(), name='schoolverification'),
    path('executiveverification/', ExecutiveVerificationView.as_view(), name='executiveverification'),
    path('findid/', FindIDEmailView.as_view(), name='findid'),
    path('findpassword/', FindPasswordEmailView.as_view(), name='findpassword'),
    path('verifyid/', VerifyIDView.as_view(), name='verifyid'),
    path('verifypassword/', VerifyPasswordView.as_view(), name='verifypassword'),
    path('resetpassword/', ResetPasswordView.as_view(), name='resetpassword'),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)