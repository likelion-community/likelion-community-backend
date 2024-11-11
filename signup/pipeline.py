from django.shortcuts import redirect
from django.urls import reverse
from social_core.pipeline.partial import partial
import logging
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth import logout

logger = logging.getLogger(__name__)

def add_kakao_uid(strategy, details, backend, response=None, user=None, *args, **kwargs):
    uid = str(response.get('id'))
    email = response.get('kakao_account', {}).get('email')
    logger.info(f"add_kakao_uid 호출, Kakao 응답: {response}")

    User = get_user_model()
    existing_user = User.objects.filter(email=email).first()

    # 기존 사용자이지만 추가 정보가 없는 경우
    if existing_user:
        if not existing_user.name or not existing_user.verification_photo:
            logger.info("기존 사용자이지만 추가 정보가 부족합니다. 프로필 완성 페이지로 이동합니다.")
            strategy.session_set('partial_pipeline_user', existing_user.pk)
            return {'user': existing_user, 'uid': uid}
        else:
            logger.info("기존 사용자입니다. 로그인 진행 중.")
            return {'user': existing_user, 'uid': uid}

    # 새로운 사용자: 세션에 uid 저장
    strategy.session_set('partial_pipeline_uid', uid)
    return {'uid': uid, 'username': uid}


@partial
def require_additional_info(strategy, details, backend, response=None, user=None, *args, **kwargs):
    nickname = response.get('properties', {}).get('nickname')
    if nickname:
        strategy.session_set('nickname', nickname)
        strategy.session_set('partial_pipeline_user', user.pk if user else None)
        strategy.request.session.save()
    if user:
        strategy.session_set('partial_pipeline_user', user.pk)

    return strategy.redirect(reverse('https://localhost:5173/kakaoSignup'))


def save_user_details(strategy, details, response=None, user=None, is_new=False, *args, **kwargs):
    User = get_user_model()
    uid = str(response.get('id'))
    
    # 이메일과 닉네임 가져오기
    email = details.get('email') if details.get('email') else response.get('kakao_account', {}).get('email')
    nickname = strategy.session_get('nickname') if is_new else user.nickname

    # 임시 계정이므로 is_profile_complete를 False로 설정
    if not user:
        fields = {
            'username': uid,
            'email': email,
            'nickname': nickname,
            'is_profile_complete': False,  # 프로필 미완성 상태로 저장
        }
        user = User.objects.create_user(**fields)
        logger.info(f"Created temporary user: {user.username}")
    else:
        user.email = email
        user.nickname = nickname
        user.is_profile_complete = True  # 기존 사용자 업데이트
        user.save()
        logger.info(f"Updated temporary user: {user.username}")

    # 세션에 임시 사용자 ID를 저장
    strategy.session_set('partial_pipeline_user', user.pk)
    return {'is_new': is_new, 'user': user}




