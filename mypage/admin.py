from django.contrib import admin
from django.utils.html import format_html
from .models import Verification, VerificationPhoto

# VerificationPhoto 인라인
class VerificationPhotoInline(admin.TabularInline):
    model = Verification.verification_photos.through
    extra = 0
    readonly_fields = ('photo_preview',)

    # 사진 미리보기 메서드 정의
    def photo_preview(self, obj):
        if obj.verificationphoto.photo:
            # 이미지를 클릭하면 원본 이미지 링크를 새 창에서 열도록 설정
            return format_html(
                f'<a href="{obj.verificationphoto.photo.url}" target="_blank">'
                f'<img src="{obj.verificationphoto.photo.url}" style="width: 100px; height: auto;" />'
                f'</a>'
            )
        return "미리보기 없음"
    photo_preview.short_description = "사진 미리보기"

# Verification 모델 관리자
@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'school_status', 'executive_status', 'get_is_school_verified')
    list_filter = ('school_status', 'executive_status')
    search_fields = ('user__username',)
    readonly_fields = ('submission_date', 'review_date', 'photo_previews')
    inlines = [VerificationPhotoInline]

    # 학교 인증 완료 여부 표시
    def get_is_school_verified(self, obj):
        return obj.user.is_school_verified
    get_is_school_verified.boolean = True
    get_is_school_verified.short_description = "학교 인증 완료 여부"

    # 여러 사진 미리보기를 위한 커스텀 필드
    def photo_previews(self, obj):
        photos = obj.verification_photos.all()
        if photos:
            # 각 이미지를 클릭 가능하도록 HTML 생성
            return format_html(
                "".join(
                    [
                        f'<a href="{photo.photo.url}" target="_blank">'
                        f'<img src="{photo.photo.url}" style="width: 100px; height: auto; margin-right: 10px;" />'
                        f'</a>'
                        for photo in photos
                    ]
                )
            )
        return "미리보기 없음"
    photo_previews.short_description = "업로드된 사진들"
