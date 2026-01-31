import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== БАЗОВЫЕ НАСТРОЙКИ ====================

# Ключи и безопасность
SECRET_KEY = os.getenv('SECRET_KEY', os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production'))

# Режим отладки
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Домены
ALLOWED_HOSTS = [
    'helpful-adventure-production-7f22.up.railway.app',
    '.railway.app',
    'localhost',
    '127.0.0.1',
    '*',  # временно для отладки
]

CSRF_TRUSTED_ORIGINS = [
    'https://helpful-adventure-production-7f22.up.railway.app',
    'https://codewithbrainblog-production.up.railway.app',
    'https://*.railway.app',
]

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'taggit',
    'django_ckeditor_5',
    'blog',
    # Cloudinary для изображений
    'cloudinary_storage',
    'cloudinary',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'blog.middleware.AdminAccessLogMiddleware',
]

ROOT_URLCONF = 'config.urls'

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
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ==================== БАЗА ДАННЫХ ====================

import dj_database_url

# Берем DATABASE_URL из переменных окружения Railway
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Используем PostgreSQL на Railway
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print("=" * 50)
    print("✅ Используется PostgreSQL на Railway")
    print("=" * 50)
else:
    # Локальная разработка: SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("=" * 50)
    print("⚠️ ВНИМАНИЕ: Используется SQLite для локальной разработки")
    print("=" * 50)

# ==================== АУТЕНТИФИКАЦИЯ ====================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ==================== СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ ====================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise configuration
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False
WHITENOISE_USE_FINDERS = True

# ==================== CLOUDINARY НАСТРОЙКИ ====================

# Если есть Cloudinary ключи, используем Cloudinary, иначе локальное хранилище
CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')

if all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
    
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET
    )
    
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    
    print("=" * 50)
    print("✅ Используется Cloudinary для хранения изображений")
    print("=" * 50)
else:
    # Локальная разработка: стандартное хранилище файлов
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    
    print("=" * 50)
    print("⚠️ Cloudinary не настроен, используем локальное хранилище файлов")
    print("ℹ️ Для продакшена добавьте переменные CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET")
    print("=" * 50)

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==================== REST FRAMEWORK ====================

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ] + (['rest_framework.renderers.BrowsableAPIRenderer'] if DEBUG else []),
}

# ==================== CKEDITOR 5 ====================

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|', 'bold', 'italic', 'link', 'bulletedList',
            'numberedList', 'blockQuote', 'imageUpload', 'codeBlock'
        ],
    },
}

# ==================== UNFOLD ADMIN ====================

UNFOLD = {
    "SITE_TITLE": "CodeWithBrain Admin",
    "SITE_HEADER": "CodeWithBrain",
    "SITE_SYMBOL": "brain",
}

# ==================== НАСТРОЙКИ БЕЗОПАСНОСТИ ====================

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True

# ==================== ЛОГИРОВАНИЕ ====================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
