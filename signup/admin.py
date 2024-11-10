from django.contrib import admin
from .models import CustomUser

# 사용자 모델 등록
admin.site.register(CustomUser)
