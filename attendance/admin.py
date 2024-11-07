from django.contrib import admin
from .models import Attendance, AttendanceStatus

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_by', 'auth_code')  # 관리자 페이지 목록에서 표시할 필드
    search_fields = ('title', 'description', 'created_by__username')  # 검색 기능 추가
    list_filter = ('date', 'created_by')  # 필터 추가

@admin.register(AttendanceStatus)
class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'user', 'status', 'date')  # 관리자 페이지 목록에서 표시할 필드
    search_fields = ('user__username', 'attendance__title')  # 검색 기능 추가
    list_filter = ('status', 'date')  # 필터 추가
