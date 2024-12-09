
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
from . import storage_media
# Build paths inside the project like this: BASE_DIR / 'subdir'.


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'f_)*$6xz#a7k(6ir&u@+tq8h@_t_9%3nr%9g5z4vdp#*a4)a*o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*' ]
CSRF_TRUSTED_ORIGINS = ['http://*']

SITE_URL = "http:127.0.0.1:8000"

# Application definition

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    ##wasabi storage
    'storages',

    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'djoser',

    'product',
    'drf_yasg',
    'order',
    'django_rest_passwordreset',

]

CORS_ALLOWED_ORIGINS = [
    "http://*",
    "https://pay-go-gamma.vercel.app",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
     'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'paygo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR,'templates')
            ],
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

WSGI_APPLICATION = 'paygo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'paygo.sql',
    }
}

# Mysql
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'railway',
#         'USER': 'postgres',
#         'PORT': 27817,
#         'PASSWORD': '4c14b-26c-eeB*Dg-e3-EDAA5EcG3Abd',
#         'HOST': 'viaduct.proxy.rlwy.net',
#     }
# }


## Email settings
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=465
EMAIL_USE_TLS=True
EMAIL_HOST_USER='paygo@gmail.com'
EMAIL_HOST_PASSWORD='R2jSidnt8E3E'
RECIPIENT_ADDRESS='youngtechbro@gmail.com'
DEFAULT_FROM_EMAIL='paygo@gmail.com'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend'


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images, and co)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR,'static'),)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media/'


# AWS S3 settings
# AWS_ACCESS_KEY_ID = ''
# AWS_SECRET_ACCESS_KEY = ''
# AWS_STORAGE_BUCKET_NAME = 'paygo'
# AWS_S3_REGION_NAME = 'us-west-1'  
# AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'


# # Media files setting
# AWS_PUBLIC_MEDIA_LOCATION = 'media'
# DEFAULT_FILE_STORAGE = 'storage_media.PublicMediaStorage'
# MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_PUBLIC_MEDIA_LOCATION}/'


# # Optionally, set AWS querystring auth (False if you want to serve media files publicly)
# AWS_QUERYSTRING_AUTH = False
# media storage
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'



REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'product.authentication.BearerAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


SWAGGER_SETTINGS = {
    "SECURITY_DEFINITIONS": {
        "Auth Token eg [Bearer {JWT}]": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
        }
    }

    
}


AUTHENTICATION_BACKENDS = [
    'product.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',  
]


PAYSTACK_PUBLIC_KEY='pk_test_bdd214c5f09fb577dda652aac05d36d540de78d5'
PAYSTACK_SECRET_KEY='sk_test_c7ca554be91c7e7093e780d169bb4e9cef611682'