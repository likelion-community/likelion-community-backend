from django.contrib import admin
from .models import Attendance, AttendanceStatus

class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_by', 'get_is_school_verified')  # 메서드 이름 사용
    list_filter = ('date', 'track')  # 실제 필드만 사용 가능

    # `is_school_verified`를 CustomUser에서 가져와 표시
    def get_is_school_verified(self, obj):
        return obj.created_by.is_school_verified
    get_is_school_verified.boolean = True  # 불리언 값으로 표시
    get_is_school_verified.short_description = "School Verified"  # 컬럼 헤더 이름

admin.site.register(Attendance, AttendanceAdmin)


@admin.register(AttendanceStatus)
class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'user', 'status', 'date')  # 관리자 페이지 목록에서 표시할 필드
    search_fields = ('user__username', 'attendance__title')  # 검색 기능 추가
    list_filter = ('status', 'date')  # 필터 추가
