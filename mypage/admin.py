from django.contrib import admin
from .models import Verification

# Verification 모델 관리자 수정
@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'school_status', 'executive_status', 'is_school_verified')  # is_school_verified 추가
    list_filter = ('school_status', 'executive_status', 'is_school_verified')
    search_fields = ('user__username',)
    readonly_fields = ('submission_date', 'review_date')

    # 인증 완료 시, is_school_verified 업데이트하는 옵션 추가
    def save_model(self, request, obj, form, change):
        if obj.school_status == 'approved':
            obj.is_school_verified = True
        else:
            obj.is_school_verified = False
        super().save_model(request, obj, form, change)
