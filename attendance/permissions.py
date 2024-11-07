# permissions.py
from rest_framework import permissions

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
            return False

        # 요청하는 사용자가 운영진일 경우에만 자신의 학교 그룹에 접근 가능
        if request.user.is_staff:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        # 운영진이 자신과 같은 학교 그룹의 데이터만 접근할 수 있도록 제한
        return request.user.school_name == obj.school_name