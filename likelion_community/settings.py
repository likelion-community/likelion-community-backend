"""
Django settings for likelion_community project.

Generated by 'django-admin startproject' using Django 4.2.14.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
AUTH_USER_MODEL = 'signup.CustomUser'



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-8t1ymn8y*4ta%@txjou(#81hrm^q6du-8c43wd6ey)=ou#b2w8'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

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

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'social_django.middleware.SocialAuthExceptionMiddleware',

]

ROOT_URLCONF = 'likelion_community.urls'

import os

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

WSGI_APPLICATION = 'likelion_community.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# 카카오 인증 백엔드 추가
AUTHENTICATION_BACKENDS = (
    'social_core.backends.kakao.KakaoOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

import os
from dotenv import load_dotenv

load_dotenv()  # .env 파일 로드

# 환경 변수 설정
SOCIAL_AUTH_KAKAO_KEY = os.getenv('SOCIAL_AUTH_KAKAO_KEY')
SOCIAL_AUTH_KAKAO_SECRET = os.getenv('SOCIAL_AUTH_KAKAO_SECRET')
SOCIAL_AUTH_KAKAO_REDIRECT_URI = os.getenv('SOCIAL_AUTH_KAKAO_REDIRECT_URI')


SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGIN_REDIRECT_URL = '/home/' 
LOGOUT_REDIRECT_URL = '/'


SOCIAL_AUTH_PIPELINE = (
    'signup.pipeline.add_kakao_uid',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'signup.pipeline.save_user_details', 
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    'signup.pipeline.require_additional_info',
    'social_core.pipeline.user.user_details',
)





SOCIAL_AUTH_KAKAO_SCOPE = ['account_email']
SOCIAL_AUTH_KAKAO_PROFILE_EXTRA_PARAMS = {'property_keys': ['kakao_account.email']}


LOGIN_URL = '/signup/login/'
# 추가 정보가 필요한 경우 리다이렉트할 URL 설정
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/signup/complete_profile/'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
