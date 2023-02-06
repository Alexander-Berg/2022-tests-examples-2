# pylint: disable=import-error, wildcard-import
from djangosettings import *  # noqa: F403, F401


BLACKBOX_AUTH = False

MIDDLEWARE_CLASSES = (
    'taxiadmin.middleware.RequestTimeLoggingMiddleware',
    'django.middleware.common.CommonMiddleware',
    'taxiadmin.middleware.BBAuthMiddleware',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s:%(name)s:%(levelname)s: %(message)s',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'default',
            'filename': '/taxi/logs/application-taxi-admin.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'taxi': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'taxi_tasks': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'taxiadmin': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
