# permissions.py
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

class IsStaffOrReadOnly(permissions.BasePermission):
    #출석 글을 staff만 수정할 수 있도록 제한하는 권한 클래스
    def has_permission(self, request, view):
        # 읽기 요청(GET)은 모두 허용, 쓰기 요청은 staff만 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class IsSchoolVerifiedAndSameGroup(permissions.BasePermission):
    """
    학교 인증을 받고, 같은 학교 그룹에 속한 회원만 접근을 허용
    """
    def has_permission(self, request, view):
        # 학교 인증 여부 확인
        if not request.user.is_school_verified:
            return False  # 학교 인증이 없으면 접근 금지

        # 학교 인증을 받은 운영진이나 일반 사용자 모두 접근 허용
        return True

    def has_object_permission(self, request, view, obj):
        # 같은 학교 그룹인지 확인 (운영진과 일반 사용자 모두 적용)
        if hasattr(obj, 'school_name'):
            return request.user.school_name == obj.school_name
        return False
    
    
class IsAdminorReadOnly(permissions.BasePermission):
    """
    admin만 접근 허용
    """
    def has_permission(self, request, view):
        # SAFE_METHODS에는 GET, HEAD, OPTIONS가 포함됨.
        if request.method in SAFE_METHODS:
            return True
        
        # POST, PUT, DELETE 등의 요청은 슈퍼유저만 가능
        return request.user and request.user.is_superuser