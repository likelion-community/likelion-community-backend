from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, AdditionalInfoForm
from django.contrib.auth.decorators import login_required
from ai_verifier import verify_like_a_lion_member
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from django.http import JsonResponse
import logging
from django.core.cache import cache

def login_view(request):
    # 사용자가 이미 로그인된 상태인지 확인
    if request.user.is_authenticated:
        # 추가 정보가 필요한 경우 확인 후 리디렉션
        if not request.user.name or not request.user.verification_photo:
            return redirect('signup:complete_profile')
        else:
            # 메인 페이지로 리디렉션
            return redirect('home:mainpage')
    
    # 로그인 페이지 렌더링
    return render(request, 'signup/login.html')

from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    request.session.flush()  
    cache.clear() 
    return redirect('signup:login')

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            # 이미지 인증 확인
            uploaded_image = request.FILES.get('verification_photo')
            is_verified = verify_like_a_lion_member(uploaded_image)
            if is_verified:
                user = form.save(commit=False)
                user.name = form.cleaned_data.get('name')
                user.verification_photo = uploaded_image
                user.save()
                return redirect('signup:login')
            else:
                form.add_error('verification_photo', '이미지 인증에 실패했습니다. 올바른 멋쟁이사자처럼 회원 사진을 업로드해 주세요.')

    else:
        form = CustomUserCreationForm()
    return render(request, 'signup/signup.html', {'form': form})

logger = logging.getLogger(__name__)


def complete_profile_view(request):
    if request.user.is_authenticated:
        logger.info(f"User is authenticated: {request.user.username}")
        # 추가 정보가 모두 있는 경우 메인 페이지로 리디렉션
        if request.user.name and request.user.verification_photo:
            return redirect('home:mainpage')
        user = request.user
    else:
        user_id = request.session.get('partial_pipeline_user')
        if not user_id:
            return redirect('signup:login')
        
        User = get_user_model()
        user = User.objects.get(pk=user_id)
    
    # AJAX 요청을 통한 유효성 검사
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        uploaded_image = request.FILES.get('verification_photo')
        is_verified = verify_like_a_lion_member(uploaded_image)
        logger.info(f"AJAX request for image verification, result: {is_verified}")
        return JsonResponse({'is_valid': bool(is_verified)})


    elif request.method == 'POST':
        # 실제 회원정보 저장을 위한 POST 요청
        form = AdditionalInfoForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            # 이미지 유효성 검사
            uploaded_image = request.FILES.get('verification_photo')
            is_verified = verify_like_a_lion_member(uploaded_image)
            
            if not is_verified:
                # 유효하지 않으면 오류 메시지를 추가하고 저장하지 않음
                form.add_error('verification_photo', '이미지 인증에 실패했습니다. 올바른 회원 사진을 업로드해 주세요.')
                logger.warning("Image verification failed for user: {}".format(user.username))
                return render(request, 'signup/complete_profile.html', {'form': form})
            
            # 유효성 검사가 통과되었을 때만 저장 및 로그인
            form.save()
            login(request, user, backend='social_core.backends.kakao.KakaoOAuth2')
            logger.info("User profile updated successfully for user: {}".format(user.username))
            
            # 사용되지 않는 세션 데이터 초기화
            request.session.pop('partial_pipeline_user', None)
            return redirect('home:mainpage')

        else:
            logger.warning("Form is not valid: {}".format(form.errors))
    else:
        form = AdditionalInfoForm(instance=user)
    
    return render(request, 'signup/complete_profile.html', {'form': form})


def delete_user(request):
    user = request.user
    user.delete()
    logout(request)
    request.session.flush()  
    cache.clear() 
    return redirect('signup:login')
