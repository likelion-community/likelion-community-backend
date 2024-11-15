from django.contrib import admin
from .models import Verification

@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'school_status', 'executive_status', 'track', 'submission_date', 'review_date')
    list_filter = ('school_status', 'executive_status', 'track')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('submission_date', 'review_date')
