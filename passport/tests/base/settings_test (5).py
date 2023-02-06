# -*- coding: utf-8 -*-
from passport.backend.perimeter_api.settings.settings import *  # noqa


DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}
