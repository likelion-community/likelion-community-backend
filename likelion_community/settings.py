from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret Key
SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')

# Debug settings
DEBUG = True
ALLOWED_HOSTS = ['*']

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
    'likelion_community',
    'attendance',
    'home',
    'mypage',
    'post',
    'signup',
    'social_django',
    'rest_framework',
    'corsheaders',
]

# Middleware
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
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
    "http://localhost:5173",
    "http://3.39.168.41:8000",
]


# URL Configuration
ROOT_URLCONF = 'likelion_community.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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
        'ENGINE': 'django.db.backends.mysql',  # MySQL 데이터베이스 엔진
        'NAME': 'everion',                     # 데이터베이스 이름
        'USER': 'root',                         # MySQL 사용자 이름
        'PASSWORD': os.environ.get('DB_PASSWORD'),    # MySQL 사용자 비밀번호
        'HOST': '3.39.168.41',                 # MySQL 서버의 퍼블릭 IP 주소
        'PORT': '3306',                        # MySQL 포트 (기본 포트)
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
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',  # JSON 포맷을 기본으로 사용
    ],
}

# Authentication Backends
AUTHENTICATION_BACKENDS = (
    'social_core.backends.kakao.KakaoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

# Social Authentication and Kakao Settings
SOCIAL_AUTH_KAKAO_KEY = os.getenv('SOCIAL_AUTH_KAKAO_KEY')
SOCIAL_AUTH_KAKAO_SECRET = os.getenv('SOCIAL_AUTH_KAKAO_SECRET')
SOCIAL_AUTH_KAKAO_REDIRECT_URI = os.getenv('SOCIAL_AUTH_KAKAO_REDIRECT_URI')
SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGIN_REDIRECT_URL = '/home/'
LOGOUT_REDIRECT_URL = '/'
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/signup/complete_profile/'
LOGIN_URL = '/signup/login/'

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

# Default Primary Key Field Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
