from .development import *

from .secrets import (
    DB_USER,
    DB_PASSWORD,
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': 'cnt-dbm-test.passport.yandex.net',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'TEST_CHARSET': 'UTF8',
    },
}
