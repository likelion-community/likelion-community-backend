from django.shortcuts import redirect
from django.urls import reverse
from social_core.pipeline.partial import partial
from django.contrib.auth import get_user_model

def add_kakao_uid(strategy, details, backend, response=None, user=None, *args, **kwargs):
    # `social_user` 단계에서 이미 사용자와 소셜 ID를 연결했으므로,
    # 이 단계에서는 추가 정보가 필요한 경우에만 처리
    uid = str(response.get('id'))
    User = get_user_model()

    # 사용자가 없는 경우, 새로운 사용자 UID를 세션에 저장
    if not user:
        strategy.session_set('partial_pipeline_uid', uid)
        return {'uid': uid}

    # 기존 사용자라면 추가 정보가 필요한지 여부만 확인
    if user and not user.is_profile_complete:
        strategy.session_set('partial_pipeline_user', user.pk)
        return redirect(reverse('signup:complete_profile'))

    return {'user': user}

@partial
def require_additional_info(strategy, details, backend, response=None, user=None, *args, **kwargs):
    # 카카오에서 닉네임을 받아와 세션에 저장하여 추가 정보 입력 시 기본값으로 사용
    nickname = response.get('properties', {}).get('nickname')
    if nickname:
        strategy.session_set('nickname', nickname)

    # 사용자가 존재하지만 프로필이 완성되지 않은 경우 추가 정보 입력 페이지로 이동
    if user and not user.is_profile_complete:
        strategy.session_set('partial_pipeline_user', user.pk)
        print("사용자의 프로필이 완성되지 않았습니다. complete_profile로 이동합니다.")
        return strategy.redirect(reverse('signup:complete_profile'))

def save_user_details(strategy, details, response=None, user=None, is_new=False, *args, **kwargs):
    User = get_user_model()
    uid = str(response.get('id'))
    email = details.get('email') or response.get('kakao_account', {}).get('email')
    nickname = response.get('properties', {}).get('nickname')

    # 새로운 사용자 생성 시
    if is_new and not user:
        user = User.objects.create_user(
            username=uid,
            email=email,
            nickname=nickname,
            is_profile_complete=False  # 기본적으로 미완성 프로필
        )
        print(f"미완성 프로필로 새 사용자 생성됨: {user.username}")

    # 세션에 임시 사용자 ID 저장
    strategy.session_set('partial_pipeline_user', user.pk)
    return {'user': user}
