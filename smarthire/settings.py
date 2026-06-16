import importlib.util
import os
import sys
from pathlib import Path
import dj_database_url

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional in local environments
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production')
DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get('ALLOWED_HOSTS', '*').split(',')
    if host.strip()
]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.users',
    'apps.resumes',
    'apps.scoring',
    'apps.dashboard',
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

if importlib.util.find_spec('whitenoise') is not None:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

ROOT_URLCONF = 'smarthire.urls'

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

WSGI_APPLICATION = 'smarthire.wsgi.application'

# Database configuration: support PostgreSQL (via DATABASE_URL) with SQLite fallback
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        ssl_require=False if os.environ.get('DATABASE_URL', '').startswith('http') else (not DEBUG if os.environ.get('DATABASE_URL') else False)
    )
}

# MongoDB Atlas - optional; app works without it (data stored in memory/SQLite fallback)
MONGODB_URI = os.environ.get('MONGODB_URI', '')

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
if importlib.util.find_spec('whitenoise') is not None:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/uploads/'
MEDIA_ROOT = BASE_DIR / 'uploads'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/users/login/'

# Job API keys (optional)
JSEARCH_API_KEY = os.environ.get('JSEARCH_API_KEY', '')
ADZUNA_APP_ID = os.environ.get('ADZUNA_APP_ID', '')
ADZUNA_APP_KEY = os.environ.get('ADZUNA_APP_KEY', '')

default_csrf_trusted_origins = [
    'https://smarthire-bxte.onrender.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]
render_hostname = os.environ.get('RENDER_EXTERNAL_HOSTNAME', '').strip()
if render_hostname:
    default_csrf_trusted_origins.append(f'https://{render_hostname}')

extra_csrf_trusted_origins = [
    origin.strip()
    for origin in os.environ.get('CSRF_TRUSTED_ORIGINS', '').split(',')
    if origin.strip()
]
CSRF_TRUSTED_ORIGINS = sorted(set(default_csrf_trusted_origins + extra_csrf_trusted_origins))

SESSION_COOKIE_AGE = 86400  # 1 day
SESSION_SAVE_EVERY_REQUEST = False
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
