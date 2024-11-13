# settings.py
from pathlib import Path
import os, environ
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Initialize environ and load .env file
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Secret Key
SECRET_KEY = env('SECRET_KEY', default='your-default-secret-key')

# Debug
DEBUG = env.bool('DEBUG', default=True)

# Allowed Hosts
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])

# Custom User Model
AUTH_USER_MODEL = 'signup.CustomUser'

# Installed Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'likelion_community',
    'attendance',
    'home',
    'mypage',
    'post',
    'signup',
    'social_django',
    'friend',
    'channels',
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'signup.middlewares.CompleteProfileRequiredMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',
]


CORS_ALLOWED_ORIGINS = [
    "https://localhost:5173",  # HTTPS 로컬 환경
    "https://everion.store",  # HTTPS를 사용하는 도메인 추가
    "http://everion.store"    # HTTP를 사용하는 도메인 추가 
]
CORS_ALLOW_HEADERS = [
    'accept',
    'authorization',
    'content-type',
    'x-requested-with',
]

CORS_ALLOW_CREDENTIALS = True

# URL Configuration
ROOT_URLCONF = 'likelion_community.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        #'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'DIRS' : [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# WSGI Application
WSGI_APPLICATION = 'likelion_community.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',         # MySQL 데이터베이스 엔진
        'NAME': 'everion_db2',                        # 데이터베이스 이름
        'USER': 'root',                               # MySQL 사용자 이름
        'PASSWORD': os.environ.get('DB_PASSWORD'),    # MySQL 사용자 비밀번호
        'HOST': '3.39.168.41',                        # MySQL 서버 IP 주소
        'PORT': '3306',                               # MySQL 포트
    }
}


# Password Validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# Static and Media Files
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_ADD_HEADERS_FUNCTION = None

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# Django Rest Framework (DRF) Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # 기본적으로 인증된 사용자에게만 허용
    ],

}

# Authentication Backends
AUTHENTICATION_BACKENDS = (
    'social_core.backends.kakao.KakaoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

# 환경 변수 설정
# Social Authentication and Kakao Settings
SOCIAL_AUTH_KAKAO_KEY = env('SOCIAL_AUTH_KAKAO_KEY')
SOCIAL_AUTH_KAKAO_SECRET = env('SOCIAL_AUTH_KAKAO_SECRET')
SOCIAL_AUTH_KAKAO_REDIRECT_URI = env('SOCIAL_AUTH_KAKAO_REDIRECT_URI')
SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/'
#SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/signup/complete_profile/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
#SOCIAL_AUTH_LOGIN_REDIRECT_URL = 'https://localhost:5173/kakaoSignup'
LOGIN_URL = '/signup/login/home/'


SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',      # 소셜 정보 가져오기
    'social_core.pipeline.social_auth.social_uid',          # 소셜 UID 가져오기
    'social_core.pipeline.social_auth.auth_allowed',        # 인증 허용 여부 확인
    'social_core.pipeline.social_auth.social_user',         # 기존 사용자 확인
    'signup.pipeline.add_kakao_uid',                        # 사용자 UID 추가
    'social_core.pipeline.user.get_username',               # 사용자 이름 설정
    'social_core.pipeline.user.create_user',                # 새로운 사용자 생성
    'signup.pipeline.require_additional_info',              # 추가 정보 요청
    'signup.pipeline.save_user_details',                    # 사용자 세부 정보 저장
    'social_core.pipeline.social_auth.associate_user',      # 사용자 연동
    'social_core.pipeline.social_auth.load_extra_data',     # 추가 데이터 로드
    'social_core.pipeline.user.user_details',               # 사용자 정보 업데이트
)

SOCIAL_AUTH_KAKAO_SCOPE = ['account_email', 'profile_nickname']
SOCIAL_AUTH_KAKAO_PROFILE_EXTRA_PARAMS = {
    'property_keys': ['kakao_account.email', 'kakao_account.profile.nickname']
}
SOCIAL_AUTH_KAKAO_FORCE_STATE = False
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True

SESSION_COOKIE_AGE = 3600  # 1시간 (초 단위)
SESSION_SAVE_EVERY_REQUEST = True  # 매 요청 시마다 세션 갱신
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = 'None'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = '587'
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1


# Default Primary Key Field Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ASGI Application
ASGI_APPLICATION = 'likelion_community.asgi.application'

# Channels Layer 설정 (Redis 사용)
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                ("127.0.0.1", 6379),  # 로컬 접근용
                ("3.39.168.41", 6379),  # 외부 접근용
                ("everion.store", 6379),
            ],
        },
    },
}

CSRF_COOKIE_NAME = 'csrftoken'  # 쿠키에 저장될 CSRF 토큰의 이름 (기본값: 'csrftoken')
CSRF_COOKIE_HTTPONLY = False    # JavaScript에서 CSRF 토큰에 접근할 수 있게 설정
CSRF_TRUSTED_ORIGINS = [
    "https://localhost:5173", 
    "https://everion.store",
    "http://everion.store",
]
CSRF_COOKIE_SAMESITE = None


import os
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django_log.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],  # 콘솔과 파일에 모두 로그 출력
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file'],  # 요청 상태를 콘솔과 파일로 기록
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# settings.py

import os

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'error.log'),  # 에러 로그 파일 경로
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {  # root logger
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
