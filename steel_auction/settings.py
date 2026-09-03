"""
Django settings for the Auction Portal project.

Note: the Python package/folder is still named `steel_auction` internally
(matches ROOT_URLCONF, WSGI_APPLICATION, and any WSGI config already set up
on a hosting service) - only the site's visible name/branding changed.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# For a real deployment, move this into an environment variable too.
SECRET_KEY = 'django-insecure-5hx!6z$kxou9b-l^!q#y-ou1-8-n@y+4_oe$t*u25!rgm2b82!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Our apps (Phase 1)
    'accounts',
    'auctions',
    'bids',
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

ROOT_URLCONF = 'steel_auction.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Project-level templates folder (holds registration/login.html, home.html, etc.)
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

WSGI_APPLICATION = 'steel_auction.wsgi.application'


# Database
# -----------------------------------------------------------------------
# SQLite - a single file on disk, no separate database server needed.
# Django creates/updates this file automatically when you run `migrate`.
# -----------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'  # Company is auctioning in India (₹); adjust if needed
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
# STATIC_ROOT: where `python manage.py collectstatic` copies every static
# file (including Django admin's own CSS/JS) so a real web server can serve
# them. Needed for real hosting (e.g. PythonAnywhere) - `runserver` on your
# own machine doesn't need this, which is why it worked locally without it.
STATIC_ROOT = BASE_DIR / 'staticfiles'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Auth redirects
# -----------------------------------------------------------------------
# After a successful login, Django sends the user to LOGIN_REDIRECT_URL.
# The spec asks for "redirect to homepage" after login and logout, so both
# point at the 'home' named URL (defined in auctions/urls.py, Phase 3).
# -----------------------------------------------------------------------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
