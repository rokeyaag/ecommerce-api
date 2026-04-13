from dotenv import load_dotenv
load_dotenv()
from pathlib import Path
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-(jpsrh@4%g-w@8@)g#b$4dcfdcf%%^#1*8u+5s(s)58x6ks&c+'

DEBUG = True

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'https://ecommerce-api-production-3e99.up.railway.app',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'store',
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

# ── Database ──────────────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL')

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL, conn_max_age=600)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'ecommerce_db',
            'USER': 'postgres',
            'PASSWORD': 'passport123',
            'HOST': 'localhost',
            'PORT': '5432',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Dhaka'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── REST Framework ────────────────────────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}

# ── CORS ──────────────────────────────────────────────────────────
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",  # ← এটা যোগ করুন
    "https://ecommerce-frontend-tawny-two.vercel.app",
]
CORS_ALLOW_CREDENTIALS = True

# ── Media Files ───────────────────────────────────────────────────
MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Site URLs ─────────────────────────────────────────────────────
BASE_URL     = os.environ.get('BACKEND_URL',  'https://ecommerce-api-production-3e99.up.railway.app')
FRONTEND_URL = os.environ.get('FRONTEND_URL', 'https://ecommerce-frontend-tawny-two.vercel.app')

# ── Admin Notification Contact ────────────────────────────────────
ADMIN_PHONE = os.environ.get('ADMIN_PHONE', '01XXXXXXXXX')   # ← আপনার নম্বর
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@shopbd.com')  # ← আপনার email

# ── Gmail SMTP — Email Notification ──────────────────────────────
# Gmail → Google Account → Security → App Passwords → Generate
EMAIL_BACKEND       = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST          = 'smtp.gmail.com'
EMAIL_PORT          = 587
EMAIL_USE_TLS       = True
EMAIL_HOST_USER     = os.environ.get('EMAIL_HOST_USER',     'yourshop@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', 'xxxx xxxx xxxx xxxx')
DEFAULT_FROM_EMAIL  = f'ShopBD <{os.environ.get("EMAIL_HOST_USER", "yourshop@gmail.com")}>'

# ── SSL Wireless — SMS Notification (Bangladesh) ──────────────────
# পাবেন: https://sms.sslwireless.com → API Credentials
SSL_WIRELESS_API_TOKEN = os.environ.get('SSL_WIRELESS_API_TOKEN', 'your_token')
SSL_WIRELESS_SID       = os.environ.get('SSL_WIRELESS_SID',       'your_sid')

# ── bKash Tokenized Payment Gateway ──────────────────────────────
# পাবেন: https://developer.bka.sh
BKASH_USERNAME   = os.environ.get('BKASH_USERNAME',   'your_bkash_username')
BKASH_PASSWORD   = os.environ.get('BKASH_PASSWORD',   'your_bkash_password')
BKASH_APP_KEY    = os.environ.get('BKASH_APP_KEY',    'your_app_key')
BKASH_APP_SECRET = os.environ.get('BKASH_APP_SECRET', 'your_app_secret')

# ── SSL Commerz ───────────────────────────────────────────────────
# পাবেন: https://manage.sslcommerz.com
# (আপনার SSLCOMMERZ_STORE_ID আগে থেকে ছিল, নতুন নামে রাখলাম)
SSL_STORE_ID   = os.environ.get('SSLCOMMERZ_STORE_ID',       'your_store_id')
SSL_STORE_PASS = os.environ.get('SSLCOMMERZ_STORE_PASSWORD',  'your_store_password')

# ── Shurjopay ─────────────────────────────────────────────────────
# পাবেন: https://shurjopay.com.bd
SHURJOPAY_USERNAME = os.environ.get('SHURJOPAY_USERNAME', 'your_username')
SHURJOPAY_PASSWORD = os.environ.get('SHURJOPAY_PASSWORD', 'your_password')

# ── Anthropic AI (Admin panel AI assistant) ───────────────────────
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', 'sk-ant-...')

# ── Logging ───────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}