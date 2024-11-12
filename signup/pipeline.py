from django.shortcuts import redirect
from django.urls import reverse
from social_core.pipeline.partial import partial
from django.contrib.auth import get_user_model

def add_kakao_uid(strategy, details, backend, response=None, user=None, *args, **kwargs):
    uid = str(response.get('id'))
    email = response.get('kakao_account', {}).get('email')
    User = get_user_model()

    # 기존 사용자 확인
    existing_user = User.objects.filter(email=email).first()

    if existing_user:
        # 프로필이 미완성일 경우
        if not existing_user.is_profile_complete:
            print("기존 사용자이며 프로필이 미완성입니다. complete_profile로 이동합니다.")
            strategy.session_set('partial_pipeline_user', existing_user.pk)
            return redirect(reverse('signup:complete_profile'))
        # 프로필이 완성된 사용자 - 로그인 진행
        return {'user': existing_user, 'uid': uid}

    # 새로운 사용자 - UID를 세션에 저장
    strategy.session_set('partial_pipeline_uid', uid)
    return {'uid': uid}

@partial
def require_additional_info(strategy, details, backend, response=None, user=None, *args, **kwargs):
    # 카카오에서 닉네임을 받아와 세션에 저장
    nickname = response.get('properties', {}).get('nickname')
    if nickname:
        strategy.session_set('nickname', nickname)

    # 프로필이 완성되지 않은 경우 추가 정보 입력 페이지로 이동
    if user and not user.is_profile_complete:
        strategy.session_set('partial_pipeline_user', user.pk)
        print("사용자의 프로필이 완성되지 않았습니다. complete_profile로 이동합니다.")
        return strategy.redirect(reverse('signup:complete_profile'))

def save_user_details(strategy, details, response=None, user=None, is_new=False, *args, **kwargs):
    User = get_user_model()
    uid = str(response.get('id'))
    email = details.get('email') or response.get('kakao_account', {}).get('email')
    nickname = response.get('properties', {}).get('nickname')

    if is_new:
        # 임시 계정 생성, 프로필 미완성 상태
        user = User.objects.create_user(
            username=uid,
            email=email,
            nickname=nickname,
            is_profile_complete=False
        )
        print(f"미완성 프로필로 새 사용자 생성됨: {user.username}")

    # 세션에 임시 사용자 ID 저장
    strategy.session_set('partial_pipeline_user', user.pk)
    return {'user': user}
