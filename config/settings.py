import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ==================== БАЗОВЫЕ НАСТРОЙКИ ====================

# Ключи и безопасность
SECRET_KEY = os.getenv('SECRET_KEY', os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production'))

# Режим отладки
DEBUG = os.getenv('DEBUG', 'False') == 'True'

# Домены
if DEBUG:
    ALLOWED_HOSTS = ['*']  # В разработке разрешаем всё
    CSRF_TRUSTED_ORIGINS = []
else:
    # В продакшене явно указываем домены Railway
    ALLOWED_HOSTS = [
        'codewithbrainblog-production.up.railway.app',
        'localhost',
        '127.0.0.1',
    ]
    CSRF_TRUSTED_ORIGINS = [
        'https://codewithbrainblog-production.up.railway.app',
    ]

# ==================== ПРИЛОЖЕНИЯ ====================

INSTALLED_APPS = [
    # Unfold admin (должен быть перед django.contrib.admin)
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third party
    'rest_framework',
    'taggit',
    'django_ckeditor_5',

    # Apps
    'blog',
]

# ==================== MIDDLEWARE ====================

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

# ==================== НАСТРОЙКИ URL И ШАБЛОНОВ ====================

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
# КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Правильная настройка для Railway

DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    # Используем PostgreSQL от Railway
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
    
    # Обязательно добавляем SSL для Railway PostgreSQL
    if 'railway' in DATABASE_URL.lower() or 'postgres.railway.app' in DATABASE_URL.lower():
        DATABASES['default']['OPTIONS'] = {
            'sslmode': 'require',
        }
else:
    # На Railway всегда должен быть DATABASE_URL
    # Если его нет, значит мы в локальной разработке
    # Используем SQLite для локальной разработки как fallback
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ==================== АУТЕНТИФИКАЦИЯ ====================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==================== ЯЗЫК И ВРЕМЯ ====================

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ==================== СТАТИЧЕСКИЕ И МЕДИА ФАЙЛЫ ====================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# WhiteNoise configuration для Railway
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MANIFEST_STRICT = False  # Игнорировать отсутствующие файлы
WHITENOISE_USE_FINDERS = True  # Искать статические файлы в приложениях
WHITENOISE_KEEP_ONLY_HASHED_FILES = True  # Удалять старые файлы

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

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
        'image': {
            'toolbar': [
                'imageTextAlternative', '|',
                'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight', '|',
                'resizeImage'
            ],
            'styles': [
                'alignLeft', 'alignCenter', 'alignRight'
            ]
        },
        'table': {
            'contentToolbar': ['tableColumn', 'tableRow', 'mergeTableCells']
        }
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
    # Включить все настройки безопасности для продакшена
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 год
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# ==================== ЛОГИРОВАНИЕ ====================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'admin': {
            'format': '{asctime} | ADMIN | User: {user} | Action: {action} | Model: {model} | Object: {object_id} | Details: {details}',
            'style': '{',
        },
        'access': {
            'format': '{asctime} | ACCESS | Method: {method} | Path: {path} | Status: {status_code} | Duration: {duration:.2f}s | User: {user} | IP: {ip}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/debug.log'),
            'formatter': 'verbose',
            'maxBytes': 10485760,
            'backupCount': 5,
            'encoding': 'utf-8',
        } if DEBUG else {
            'class': 'logging.NullHandler',  # В продакшене логи только в stdout
        },
        'admin_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/admin.log'),
            'formatter': 'admin',
            'maxBytes': 10485760,
            'backupCount': 5,
            'encoding': 'utf-8',
        } if DEBUG else {
            'class': 'logging.NullHandler',
        },
        'access_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/access.log'),
            'formatter': 'access',
            'maxBytes': 10485760,
            'backupCount': 5,
            'encoding': 'utf-8',
        } if DEBUG else {
            'class': 'logging.NullHandler',
        },
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs/security.log'),
            'formatter': 'verbose',
            'maxBytes': 10485760,
            'backupCount': 5,
            'encoding': 'utf-8',
        } if DEBUG else {
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'blog': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'admin_logger': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'access_logger': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Создаем папку logs только в разработке
if DEBUG:
    logs_dir = os.path.join(BASE_DIR, 'logs')
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"Создана папка для логов: {logs_dir}")

# ==================== ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА ДЛЯ RAILWAY ====================

# Для отладки: вывести информацию о подключении к базе данных
if not DEBUG:
    print("=" * 50)
    print("PRODUCTION ENVIRONMENT")
    print(f"DATABASE_URL exists: {bool(DATABASE_URL)}")
    print(f"Database engine: {DATABASES['default']['ENGINE']}")
    print(f"ALLOWED_HOSTS: {ALLOWED_HOSTS}")
    print("=" * 50)
