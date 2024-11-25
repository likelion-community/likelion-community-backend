# signup/admin.py
from django.contrib import admin
from .models import CustomUser
from django.contrib.sessions.models import Session

# 사용자 모델 등록
admin.site.register(CustomUser)

# 세션 모델 등록
admin.site.register(Session)
