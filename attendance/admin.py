# attendance/admin.py
from django.contrib import admin
from .models import Attendance, AttendanceStatus

class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'date', 
        'time', 
        'created_by', 
        'get_school_name', 
        'track', 
        'auth_code', 
        'late_threshold', 
        'absent_threshold', 
        'get_is_school_verified'
    )
    list_filter = ('date', 'track')
    search_fields = ('title', 'created_by__username', 'created_by__name')

    # school_name 필드 표시
    def get_school_name(self, obj):
        return obj.created_by.school_name
    get_school_name.short_description = "School Name"

    # is_school_verified 필드 표시
    def get_is_school_verified(self, obj):
        return obj.created_by.is_school_verified
    get_is_school_verified.boolean = True
    get_is_school_verified.short_description = "School Verified"

    # ordering 설정
    ordering = ('-date', 'time')

    # school_name을 변경할 수 있는 action 추가
    actions = ['update_school_name']

    def update_school_name(self, request, queryset):
        for attendance in queryset:
            # 작성자의 school_name을 새 값으로 변경
            new_school_name = "Updated School Name"  # 여기에 원하는 새 값을 입력
            attendance.created_by.school_name = new_school_name
            attendance.created_by.save()
        self.message_user(request, "Selected records have been updated with the new school name.")
    update_school_name.short_description = "Update School Name for Selected Records"

admin.site.register(Attendance, AttendanceAdmin)


@admin.register(AttendanceStatus)
class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'user', 'status', 'date', 'get_user_track', 'get_membership_term')
    search_fields = ('user__username', 'user__name', 'attendance__title')
    list_filter = ('status', 'date')

    # 사용자 track 표시
    def get_user_track(self, obj):
        return obj.user.track
    get_user_track.short_description = "User Track"

    # 사용자 membership term 표시
    def get_membership_term(self, obj):
        return obj.user.membership_term
    get_membership_term.short_description = "Membership Term"

    ordering = ('-date', 'status')
