from django.urls import path
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
    path('verification/', VerificationStatusView.as_view(), name='verification'),  # 올바른 뷰 이름 반영
    path('findid/', FindIDEmailView.as_view(), name='findid'),
    path('findpassword/', FindPasswordEmailView.as_view(), name='findpassword'),
    path('verifyid/', VerifyIDView.as_view(), name='verifyid'),
    path('verifypassword/', VerifyPasswordView.as_view(), name='verifypassword'),
    path('resetpassword/', ResetPasswordView.as_view(), name='resetpassword'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
