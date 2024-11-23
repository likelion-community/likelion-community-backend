from django.contrib import admin
from .models import Verification

# Verification 모델 관리자 수정
@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'school_status', 'executive_status', 'get_is_school_verified')  # 메서드 이름 사용
    list_filter = ('school_status', 'executive_status')  # DB 필드만 사용
    search_fields = ('user__username',)
    readonly_fields = ('submission_date', 'review_date')

    # is_school_verified 속성을 CustomUser에서 가져와 표시
    def get_is_school_verified(self, obj):
        return obj.user.is_school_verified
    get_is_school_verified.boolean = True  # Boolean 값을 아이콘으로 표시
    get_is_school_verified.short_description = "학교 인증 완료 여부"  # 컬럼 헤더 이름
