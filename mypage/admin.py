from django.contrib import admin
from .models import Verification

# Verification 모델 관리자 수정
@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'school_status', 'executive_status', 'is_school_verified')  # is_school_verified 추가
    list_filter = ('school_status', 'executive_status')  # DB 필드만 사용
    search_fields = ('user__username',)
    readonly_fields = ('submission_date', 'review_date')

    # is_school_verified 속성을 어드민에 표시
    def is_school_verified(self, obj):
        return obj.is_school_verified
    is_school_verified.boolean = True  # Boolean 값을 아이콘으로 표시
    is_school_verified.short_description = "학교 인증 완료 여부"  # 컬럼 헤더 이름
