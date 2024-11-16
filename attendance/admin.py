from django.contrib import admin
from .models import Attendance, AttendanceStatus

class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'date', 
        'time', 
        'created_by', 
        'track', 
        'auth_code', 
        'late_threshold', 
        'absent_threshold', 
        'get_is_school_verified'
    )
    list_filter = ('date', 'track')
    search_fields = ('title', 'created_by__username', 'created_by__name')

    def get_is_school_verified(self, obj):
        return obj.created_by.is_school_verified
    get_is_school_verified.boolean = True
    get_is_school_verified.short_description = "School Verified"

    ordering = ('-date', 'time')

admin.site.register(Attendance, AttendanceAdmin)


@admin.register(AttendanceStatus)
class AttendanceStatusAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'user', 'status', 'date', 'get_user_track', 'get_membership_term')
    search_fields = ('user__username', 'user__name', 'attendance__title')
    list_filter = ('status', 'date')

    def get_user_track(self, obj):
        return obj.user.track
    get_user_track.short_description = "User Track"

    def get_membership_term(self, obj):
        return obj.user.membership_term
    get_membership_term.short_description = "Membership Term"

    ordering = ('-date', 'status')
