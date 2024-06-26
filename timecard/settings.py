"""
Django プロジェクト timecard の環境定義です。
"""
from django.contrib import messages

# Application information
APP_SITE = 'https://github.com/cottonspace/time-record-system'
APP_NAME = 'T-RECS'
APP_VERSION = '0.9.24'

# Load local settings
try:
    from timecard.local_settings import *
except ImportError:
    pass

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'worktime',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'timecard.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'worktime.context_processors.app_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'timecard.wsgi.application'

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/
LANGUAGE_CODE = 'ja'
TIME_ZONE = 'Asia/Tokyo'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/
STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# メッセージタグの Bootstrap 対応
MESSAGE_TAGS = {
    messages.INFO: 'alert alert-info',
    messages.SUCCESS: 'alert alert-success',
    messages.WARNING: 'alert alert-warning',
    messages.ERROR: 'alert alert-danger',
}

# 曜日文字列
DAY_OF_WEEK = ['月', '火', '水', '木', '金', '土', '日', '祝日']

# 打刻種別
RECORD_ACTIONS = {'begin': '出勤', 'end': '退勤'}

# 祝日 ics データの URL (祝日を自動設定しない場合は None を指定)
HOLIDAY_DOWNLOAD_URL = 'https://calendar.google.com/calendar/ical/ja.japanese%23holiday%40group.v.calendar.google.com/public/basic.ics'

# ログイン用 URL
LOGIN_URL = '/worktime/login/'

# ログイン後ページ URL
LOGIN_REDIRECT_URL = '/worktime/record/'

# ログアウト後ページ URL
LOGOUT_REDIRECT_URL = '/worktime/login/'
