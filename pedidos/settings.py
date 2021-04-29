"""
Django settings for djp project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'u70#f+20!y)aua@!wg1w6sinmz+*b46&s4ikib)a^fi(9%pa4d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['www.esshoesmultimarcas.com']

#FORCE_SCRIPT_NAME = '/app'

ADMINS = [('jose', 'jggalvan@prodigy.net.mx'),]



# Application definition

INSTALLED_APPS = (
    # django app
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'rest_framework'
    # 3ed party app
    'crispy_forms',
    #'django_tables2',
    # My app
    #'reportes',
    'pedidos',

    )

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'djp.urls'

STATIC_ROOT = '/home/jggalvan/webapps/esshoes_static_produccion/'



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
                'django.core.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = 'djp.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'lafe_prueba',
        'USER': 'lafe',
        'PASSWORD': 'malher',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Monterrey'

USE_I18N = True

USE_L10N = True

USE_TZ = False

DATE_INPUT_FORMATS = ['%d/%m/%Y',]


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = 'http://www.esshoesmultimarcas.com/static/'

LOGIN_URL = '/pedidos/acceso/'

CRISPY_TEMPLATE_PACK = 'bootstrap3'





# ----------- configuracion de correo 

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

SERVER_EMAIL = 'smtp.webfaction.com'

EMAIL_HOST = 'smtp.webfaction.com'

EMAIL_PORT = '465'

EMAIL_HOST_USER ='pedidos_multimarcas'

EMAIL_HOST_PASSWORD ='pedidos1'

EMAIL_USE_TLS = False

EMAIL_USE_SSL = True

DEFAULT_FROM_EMAIL = 'soporte@esshoesmultimarcas.com'







# Email Settings

#EMAIL_HOST = 'smtp.webfaction.com'

#EMAIL_PORT = '587'

#EMAIL_HOST_USER ='atencion_clientes'

#EMAIL_HOST_PASSWORD ='ciajcm1218'

#EMAIL_USE_TLS = True

#EMAIL_USE_SSL = False
