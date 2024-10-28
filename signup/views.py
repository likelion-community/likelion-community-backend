# views.py
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, AdditionalInfoForm, CustomLoginForm
from django.contrib.auth.decorators import login_required
from ai_verifier import verify_like_a_lion_member
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.http import JsonResponse
import logging
from django.core.cache import cache
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages 

logger = logging.getLogger(__name__)

def login_home_view(request):
    return render(request, 'signup/login_home.html')

def kakao_login_view(request):
    print("kakao_login_view is called")  # 호출 여부 확인

    if request.user.is_authenticated:
        print(f"Authenticated user: {request.user.username}, Profile Complete: {request.user.is_profile_complete}")
        
        if not request.user.is_profile_complete:
            request.session['partial_pipeline_user'] = request.user.pk
            print("Redirecting to complete_profile")
            return redirect('signup:complete_profile')
        else:
            login(request, request.user)  # 로그인 처리
            print("Redirecting to mainpage with session data:", request.session.items())
            return redirect('home:mainpage')
    
    print("Redirecting to login_home (not authenticated)")
    return redirect('signup:login_home')



def custom_login_view(request):
    if request.user.is_authenticated:
        return redirect('home:mainpage')

    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home:mainpage')
            else:
                form.add_error(None, '아이디 또는 비밀번호가 잘못되었습니다.')
    else:
        form = CustomLoginForm()

    return render(request, 'signup/custom_login.html', {'form': form})

def check_password_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        try:
            validate_password(password)
            return JsonResponse({'is_valid': True, 'message': '유효한 비밀번호입니다.'})
        except ValidationError as e:
            return JsonResponse({'is_valid': False, 'message': e.messages[0]})

def logout_view(request):
    logout(request)
    request.session.flush()  
    cache.clear() 
    return redirect('signup:login_home')

def signup_view(request):
    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            uploaded_image = request.FILES.get('verification_photo')
            is_verified = verify_like_a_lion_member(uploaded_image)
            return JsonResponse({'is_valid': bool(is_verified)})

        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = request.FILES.get('verification_photo')
            is_verified = verify_like_a_lion_member(uploaded_image)
            if bool(is_verified):  
                user = form.save(commit=False)
                user.name = form.cleaned_data.get('name')
                user.verification_photo = uploaded_image
                user.is_profile_complete = True  # 프로필 완료 상태로 설정
                user.save()
                return redirect('signup:login')
            else:
                form.add_error('verification_photo', '이미지 인증에 실패했습니다. 올바른 멋쟁이사자처럼 회원 사진을 업로드해 주세요.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'signup/signup.html', {'form': form})


def complete_profile_view(request):
    User = get_user_model()
    user_id = request.session.get('partial_pipeline_user')
    
    # user_id가 없는 경우, 로그인 페이지로 리디렉션
    if not user_id:
        return redirect('signup:login_home')

    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        # 해당 user_id로 사용자가 없으면 로그인 페이지로 리디렉션
        request.session.pop('partial_pipeline_user', None)
        return redirect('signup:login_home')

    if user.is_profile_complete:
        # 프로필이 완성된 경우 메인 페이지로 리디렉션
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home:mainpage')
    
    if request.method == 'POST':
        # AJAX 요청일 경우 유효성 검사를 처리하고 세션에 플래그 저장
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            uploaded_image = request.FILES.get('verification_photo')
            is_verified = verify_like_a_lion_member(uploaded_image)
            if is_verified:
                request.session['photo_verified'] = True  # 유효성 검사 통과 시 세션에 저장
            return JsonResponse({'is_valid': bool(is_verified)}) 

        # 일반 폼 제출 시 세션의 유효성 검사 결과를 확인
        if request.session.get('photo_verified', False):
            form = AdditionalInfoForm(request.POST, request.FILES, instance=user)
            if form.is_valid():
                user.is_profile_complete = True
                form.save()
                login(request, user, backend='social_core.backends.kakao.KakaoOAuth2')
                request.session.pop('partial_pipeline_user', None)
                request.session.pop('photo_verified', None)  # 검증 후 세션 값 삭제
                return redirect('home:mainpage')
        else:
            messages.error(request, "사진 유효성 검사에 실패했습니다. 다시 시도해 주세요.")
            return redirect('signup:complete_profile')
    
    else:
        # GET 요청 시 폼 초기값 설정
        nickname = request.session.get('nickname')
        initial_data = {'nickname': nickname} if nickname else {}
        form = AdditionalInfoForm(instance=user, initial=initial_data)
        logger.info(f"complete_profile_view 초기값 설정: 초기 닉네임 값 - {nickname}")


    return render(request, 'signup/complete_profile.html', {'form': form})



def delete_incomplete_user(request):
    User = get_user_model()
    user_id = request.session.get('partial_pipeline_user')
    if user_id:
        user = User.objects.get(pk=user_id)
        if not user.is_profile_complete:
            user.delete()
            logger.info(f"Deleted incomplete user: {user.username}")
        request.session.pop('partial_pipeline_user', None)
    return redirect('signup:begin')


        
def delete_user(request):
    user = request.user
    user.delete()
    logout(request)
    request.session.flush()  
    cache.clear() 
    return redirect('signup:login_home')
