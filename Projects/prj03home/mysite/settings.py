"""
Django settings for mysite project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# .env 환경변수 로드
load_dotenv()

# 기본 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent

# 보안 설정
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-dev-key")  # .env 없으면 기본값
DEBUG = True
ALLOWED_HOSTS = []

# 앱 등록
INSTALLED_APPS = [
    # Django 기본 앱
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # 사용자 정의 앱
    'accounts.apps.AccountsConfig',
    'travel_input.apps.TravelInputConfig',
    'map.apps.MapConfig',
    'image_enhance',
]

# 미들웨어 설정
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

# URL 설정
ROOT_URLCONF = 'mysite.urls'

# 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'travel_input.context_processors.cities',
            ],
        },
    },
]

# WSGI
WSGI_APPLICATION = 'mysite.wsgi.application'

# 데이터베이스
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 비밀번호 검증
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 지역화
LANGUAGE_CODE = 'ko-kr'
LANGUAGES = [
    ('ko', 'Korean'),
    ('en', 'English'),
]
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# 정적 파일
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# 사용자 모델
AUTH_USER_MODEL = 'accounts.CustomUser'

# 로그인 리디렉션
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# 기본 PK 필드 타입
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# OpenAI API 키 환경변수 로드
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("OPENAI_API_KEY 환경변수가 설정되어 있지 않습니다.")
