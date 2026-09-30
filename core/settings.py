from celery.schedules import crontab
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv
import os

# Cargar variables del archivo .env
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ============================
# CONFIGURACIÓN BÁSICA
# ============================
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-sena-default-key-change-in-prod')
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1')

allowed_hosts_raw = os.getenv('ALLOWED_HOSTS', '*')
ALLOWED_HOSTS = [h.strip() for h in allowed_hosts_raw.split(',') if h.strip()] if allowed_hosts_raw else ['*']

EMAILS_FROM_EMAIL = os.getenv('EMAILS_FROM_EMAIL')

# ============================
# ARCHIVOS ESTÁTICOS Y MULTIMEDIA
# ============================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================
# APPS INSTALADAS
# ============================
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Terceros
    'rest_framework',
    'drf_yasg',
    'corsheaders',

    # Apps locales
    'apps.security',
    'apps.general',
    'apps.assign',
]

# ============================
# MIDDLEWARE
# ============================
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
            BASE_DIR / 'apps/security/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'core.wsgi.application'

# ============================
# BASE DE DATOS (MySQL / Dynamic / SQLite in Test)
# ============================
import sys

db_engine = os.getenv('DB_ENGINE', 'django.db.backends.mysql')
db_options = {'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"}
if os.getenv('DB_SSL', 'false').lower() in ('true', '1'):
    db_options['ssl'] = {}

db_name = os.getenv('DB_NAME', 'bdautogestion')
db_user = os.getenv('DB_USER', 'root')
db_password = os.getenv('DB_PASSWORD') or os.getenv('DB_PASS', '')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '3306')

database_url = os.getenv('DATABASE_URL')
if database_url:
    from urllib.parse import urlparse, unquote
    parsed_url = urlparse(database_url)
    if parsed_url.username:
        db_user = unquote(parsed_url.username)
    if parsed_url.password:
        db_password = unquote(parsed_url.password)
    if parsed_url.hostname:
        db_host = parsed_url.hostname
    if parsed_url.port:
        db_port = str(parsed_url.port)
    if parsed_url.path and len(parsed_url.path) > 1:
        db_name = unquote(parsed_url.path.lstrip('/'))
    if 'ssl-mode=REQUIRED' in database_url or 'ssl=true' in database_url.lower():
        db_options['ssl'] = {}

if 'test' in sys.argv and not os.getenv('DATABASE_URL') and not os.getenv('DB_PASSWORD'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': db_engine,
            'NAME': db_name,
            'USER': db_user,
            'PASSWORD': db_password,
            'HOST': db_host,
            'PORT': db_port,
            'OPTIONS': db_options if 'mysql' in db_engine else {},
        }
    }

# ============================
# CELERY CONFIG
# ============================
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
TIME_ZONE = 'America/Bogota'
CELERY_TIMEZONE = TIME_ZONE

CELERY_BEAT_SCHEDULE = {
    'deactivate-expired-instructors-daily': {
        'task': 'apps.general.tasks.deactivate_expired_instructors',
        'schedule': crontab(hour=0, minute=1),
    },
}

# ============================
# MODELO DE USUARIO PERSONALIZADO
# ============================
AUTH_USER_MODEL = 'security.User'

# ============================
# VALIDACIÓN DE CONTRASEÑAS
# ============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ============================
# DRF y JWT
# ============================
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}
X_FRAME_OPTIONS = 'SAMEORIGIN'
# ============================
# SWAGGER / REDOC
# ============================
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {'type': 'apiKey', 'name': 'Authorization', 'in': 'header'}
    },
    'USE_SESSION_AUTH': False,
    'JSON_EDITOR': True,
}

REDOC_SETTINGS = {'LAZY_RENDERING': False}

# ============================
# INTERNACIONALIZACIÓN
# ============================
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Bogota'
USE_I18N = True
USE_TZ = True

# ============================
# ARCHIVOS ESTÁTICOS / MEDIA
# ============================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================
# CORS
# ============================
DEFAULT_CORS_ORIGINS = [
    "http://167.114.98.199",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
]

env_cors = os.getenv('CORS_ALLOWED_ORIGINS')
if env_cors:
    CORS_ALLOWED_ORIGINS = DEFAULT_CORS_ORIGINS + [origin.strip() for origin in env_cors.split(',') if origin.strip()]
else:
    CORS_ALLOWED_ORIGINS = DEFAULT_CORS_ORIGINS

if os.getenv('CORS_ALLOW_ALL_ORIGINS', 'False').lower() in ('true', '1'):
    CORS_ALLOW_ALL_ORIGINS = True

# Allow cookies/credentials from the browser when using `fetch(..., credentials: 'include')`
CORS_ALLOW_CREDENTIALS = True

DEFAULT_CSRF_ORIGINS = [
    "http://167.114.98.199",
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

env_csrf = os.getenv('CSRF_TRUSTED_ORIGINS')
if env_csrf:
    CSRF_TRUSTED_ORIGINS = DEFAULT_CSRF_ORIGINS + [origin.strip() for origin in env_csrf.split(',') if origin.strip()]
else:
    CSRF_TRUSTED_ORIGINS = DEFAULT_CSRF_ORIGINS

# For cross-site cookie usage during development you may need to relax SameSite.
# If you use HTTPS in production, set SESSION_COOKIE_SECURE = True and CSRF_COOKIE_SECURE = True.
SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SAMESITE = None
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


# ============================
# CHANNEL LAYERS (for django-channels)
# ============================
# Configure a channel layer backend. By default use an in-memory layer for
# development. For production use Redis and set the environment variable
# USE_REDIS_CHANNEL=true and REDIS_URL accordingly (e.g. redis://localhost:6379).
USE_REDIS_CHANNEL = os.getenv('USE_REDIS_CHANNEL', 'False').lower() in ('true', '1')
if USE_REDIS_CHANNEL:
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                'hosts': [REDIS_URL],
            },
        },
    }
else:
    # In-memory channel layer is suitable for local development and testing only.
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }


# ============================
# EMAIL CONFIG (desde .env)
# ============================
if os.getenv('EMAIL_HOST_USER') and os.getenv('EMAIL_HOST_PASSWORD'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('EMAIL_HOST_USER', 'no-reply@sena.edu.co')
EMAILS_FROM_NAME = os.getenv('EMAIL_FROM_NAME', 'AutoGestion SENA')

# ============================
# LOGGING
# ============================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'django.log',
        },
    },
    'loggers': {
        'django': {'handlers': ['file'], 'level': 'ERROR', 'propagate': True},
    },
}
