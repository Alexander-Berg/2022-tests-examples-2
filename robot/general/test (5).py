import os

YANDEX_AUTH_HOST = ".yandex-team.ru"

os.environ.setdefault('SMELTER_DEBUG', 'true')
os.environ.setdefault('PRIMARY_YT_PROXY', 'test')

SEND_MAIL_ENABLED = False

# should be in the end
from .base import *  # noqa

STARTER_SYNC_PROBABLITY = 1.0
TEST_RETURN_TEMPORARY_CODE_IN_REQUEST = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}
