from django.contrib import admin
from .models import *

# Register your models here.
class SchoolVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submission_date', 'review_date')
    list_filter = ('status')
    search_fields = ('user__username', 'status')

admin.site.register(SchoolVerification)

class ExecutiveVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submission_date', 'review_date')
    list_filter = ('status')
    search_fields = ('user__username', 'status')

admin.site.register(ExecutiveVerification)