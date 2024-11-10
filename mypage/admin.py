from django.contrib import admin
from .models import *

# Register your models here.
class SchoolVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submission_date', 'review_date')
    list_filter = ('status', 'reviewed_by')
    search_fields = ('user__username', 'status')

admin.site.register(SchoolVerification)