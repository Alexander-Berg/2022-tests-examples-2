from .passport_admin_roles_production import *

from .secrets import (
    DB_USER,
    DB_PASSWORD,
    DB_SLAVE_USER,
    DB_SLAVE_PASSWORD,
)


DB_HOST = 'cnt-dbm-test.passport.yandex.net'
DB_NAME = 'passport_grants_configurator_passportadm'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': DB_HOST,
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'TEST_CHARSET': 'UTF8',
    },
    'slave': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': DB_HOST,
        'NAME': DB_NAME,
        'USER': DB_SLAVE_USER,
        'PASSWORD': DB_SLAVE_PASSWORD,
        'TEST_CHARSET': 'UTF8',
    },
}

DATABASE_SLAVES = ['slave']
