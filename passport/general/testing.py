from .default import *

from .secrets import (
    DB_USER,
    DB_SLAVE_USER,
    DB_PASSWORD,
    DB_SLAVE_PASSWORD,
)

CONDUCTOR_API_NO_CACHE = {
    'address': 'https://c.test.yandex-team.ru/api/',
    'timeout': 60,
    'retry': 2,
}

CONDUCTOR_API = {
    'address': 'https://c.test.yandex-team.ru/api-cached/',
    'timeout': 60,
    'retry': 2,
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'cnt-dbm-test.passport.yandex.net',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'TEST_CHARSET': 'UTF8',
    },
    'slave': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'cnt-dbm-test.passport.yandex.net',
        'NAME': DB_NAME,
        'USER': DB_SLAVE_USER,
        'PASSWORD': DB_SLAVE_PASSWORD,
        'TEST_CHARSET': 'UTF8',
    },
}

DATABASE_SLAVES = ['slave']

GRANTS_MAIL_ENV_NAME = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EXPORT_GRANTS_URL = 'https://grantushka-test.yandex-team.ru/grants/operations/'
