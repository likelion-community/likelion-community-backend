from django.shortcuts import redirect
from django.urls import reverse
from social_core.pipeline.partial import partial
import logging
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


logger = logging.getLogger(__name__)

def add_kakao_uid(strategy, details, backend, response=None, user=None, *args, **kwargs):
    #uid = backend.get_user_id(details=details, response=response)
    #다른 플랫폼 확장할거면 위에로 쓰기
    uid = str(response.get('id'))

    # response에 kakao_account와 email 정보가 있는지 확인
    email = response.get('kakao_account', {}).get('email')
    logger.info(f"Response from Kakao: {response}")

    User = get_user_model()
    existing_user = User.objects.filter(email=email).first()
    
    if existing_user:
        # 이메일이 존재하지만 추가 정보가 없는 경우
        if not existing_user.name or not existing_user.verification_photo:
            logger.info("Existing email found, but additional information is missing. Redirecting to complete profile.")
            # 로그인한 사용자로 처리
            strategy.session_set('partial_pipeline_user', existing_user.pk)
            return redirect(reverse('signup:complete_profile'))
        else:
            # 기존 사용자라면 로그인으로 진행
            logger.info("Existing user found. Proceeding with login.")
            return {'user': existing_user, 'uid': uid}
    
    # 새로운 사용자인 경우 uid를 반환하여 다음 단계로 진행
    return {'uid': uid, 'username': uid}

@partial
def require_additional_info(strategy, details, backend, response=None, user=None, is_new=False, *args, **kwargs):
    # 새로운 Kakao 사용자인 경우에만 추가 정보 입력을 요구
    if backend.name == 'kakao' and is_new:
        nickname = strategy.request.POST.get('nickname')
        strategy.session_set('nickname', nickname)
        logger.info("Redirecting new Kakao user to complete profile.")
        return strategy.redirect(reverse('signup:complete_profile'))
    
    return None



def save_user_details(strategy, details, response=None, user=None, is_new=False, *args, **kwargs):
    User = get_user_model()
    uid = str(response.get('id'))
    # response에서 직접 가져오도록 수정
    if response is None:
        response = kwargs.get('response')
        
    # 이메일 가져오기
    email = response.get('kakao_account', {}).get('email') if not details.get('email') else details.get('email')
    nickname = strategy.session_get('nickname') if is_new else user.nickname

    if details is None:
        logger.error("Details is None. Unable to fetch user details from Kakao.")
        return redirect(reverse('signup_error'))  # 회원가입 에러 페이지로 리다이렉트

    # details 내용 출력 (추가 확인)
    logger.info(f"User details: {details}")
    

    fields = {
        'username': uid,
        'email': email,
        'nickname': nickname,
    }

    try:
        if not user:
            user = User.objects.create_user(**fields)
            is_new = True
        else:
            user.nickname = nickname  
            user.save()
            is_new = False
    except ValidationError as e:
        logger.error(f"Failed to create user: {e}")
        return redirect(reverse('signup_error'))
    
    return {'is_new': is_new, 'user': user}


