from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'chelsea_fc_digital_twin_dev',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CORS_ALLOW_ALL_ORIGINS = True

INTERNAL_IPS = [
    '127.0.0.1',
]

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

LOGGING['handlers']['console'] = {
    'level': 'DEBUG',
    'class': 'logging.StreamHandler',
}

LOGGING['loggers']['django']['handlers'].append('console')
LOGGING['loggers']['core.performance']['handlers'].append('console')
LOGGING['loggers']['core.exports']['handlers'].append('console')