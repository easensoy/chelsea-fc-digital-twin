from .base import *
import dj_database_url

DEBUG = False

ALLOWED_HOSTS = [
    '.googleapis.com',
    '.googleusercontent.com',
    'chelsea-fc-digital-twin.ew.r.appspot.com',
    os.environ.get('DOMAIN_NAME', ''),
]

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://chelsea-fc-digital-twin.ew.r.appspot.com',
    os.environ.get('FRONTEND_URL', ''),
]

LOGGING['handlers']['gcp'] = {
    'level': 'INFO',
    'class': 'google.cloud.logging.handlers.CloudLoggingHandler',
}

for logger in LOGGING['loggers'].values():
    if 'handlers' in logger:
        logger['handlers'].append('gcp')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')