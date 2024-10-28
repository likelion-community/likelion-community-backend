from django.urls import path
from . import views
from social_django import views as social_views 


app_name = 'signup'

urlpatterns = [
    path('login/', views.login_home_view, name='login_home'),  # 로그인 홈 (카카오, 일반 선택 화면)
    path('login/custom/', views.custom_login_view, name='login'), 
    path('signup/', views.signup_view, name='signup'),
    path('complete_profile/', views.complete_profile_view, name='complete_profile'), 
    path('delete_user/', views.delete_user, name='delete_user'),
    path('logout/', views.logout_view, name='logout'), 
     # 카카오 소셜 로그인
    path('login/kakao/', social_views.auth, name='begin', kwargs={'backend': 'kakao'}),  
    path('complete/kakao/', social_views.complete, name='complete'), 
    path('check-password/', views.check_password_view, name='check_password'),
    

]