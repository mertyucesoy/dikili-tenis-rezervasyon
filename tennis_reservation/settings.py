from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-5af(hnr^^+nl+2g4((^ha1z1#6#q84-k2@y)pd5%^%4$92^e14'

DEBUG = True

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'dikili-tenis-rezervasyon.onrender.com',
    'dikili-tenis-rezervasyon.pythonanywhere.com',
]

# Uygulamalar
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'court',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # static files için önemli
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'tennis_reservation.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Gerekirse özel template klasörü yolu verilir
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

WSGI_APPLICATION = 'tennis_reservation.wsgi.application'

# Veritabanı
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Şifre doğrulama
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Uluslararası ayarlar
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# Statik dosyalar (Render için doğru yapı)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # collectstatic buraya kopyalar

# STATICFILES_DIRS sadece localde özel dosyaların varsa gereklidir.
# Eğer kullanmıyorsan tamamen kaldır:
# STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Varsayılan AutoField
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Giriş yönlendirmeleri
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Özel kullanıcı modeli
AUTH_USER_MODEL = 'court.CustomUser'

# E-posta ayarları
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'dikilitenis@gmail.com'
EMAIL_HOST_PASSWORD = 'zyqrwinycmmvyxkb'  # Google uygulama şifresi

# E-posta veya kullanıcı adı ile giriş desteği
AUTHENTICATION_BACKENDS = [
    'tennis_reservation.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]
