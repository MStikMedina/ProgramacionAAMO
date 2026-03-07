"""
Django settings for core project.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

# Cargar variables del .env (una sola vez)
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / '.env')

# ─────────────────────────────────────────────────────────────
# SEGURIDAD
# ─────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get('SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = []
PASSWORD_ENCRYPT_KEY = os.environ.get('PASSWORD_ENCRYPT_KEY')

# ─────────────────────────────────────────────────────────────
# APLICACIONES
# ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'configuracion',
    'colegios',
    'profesores',
    'general',
    'usuarios',
    'informes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'usuarios.middleware.ControlAccesoMiddleware',
]

LOGIN_URL = '/usuarios/login/'

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# ─────────────────────────────────────────────────────────────
# BASE DE DATOS
# ─────────────────────────────────────────────────────────────
DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        ssl_require=True,
    )
}

# ─────────────────────────────────────────────────────────────
# VALIDACIÓN DE CONTRASEÑAS
# ─────────────────────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─────────────────────────────────────────────────────────────
# INTERNACIONALIZACIÓN
# ─────────────────────────────────────────────────────────────
LANGUAGE_CODE = 'es-co'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# ─────────────────────────────────────────────────────────────
# CACHÉ
# ─────────────────────────────────────────────────────────────
# LocMemCache para desarrollo — sin dependencias extra.
# Para producción con Redis, instalar django-redis y cambiar por:
#
#   CACHES = {
#       'default': {
#           'BACKEND': 'django_redis.cache.RedisCache',
#           'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
#           'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
#           'TIMEOUT': 300,
#       }
#   }
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'aamo-cache',
        'TIMEOUT': 300,  # 5 minutos
    }
}

# ─────────────────────────────────────────────────────────────
# ARCHIVOS ESTÁTICOS
# ─────────────────────────────────────────────────────────────
STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'