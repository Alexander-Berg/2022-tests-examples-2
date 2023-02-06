# -*- coding: utf-8 -*-
# isort:skip_file
# flake8: noqa

# Фейковые настройки для запуска тестов
from passport.backend.py_adm.settings.settings import *  # noqa


MIDDLEWARE = [
    cls if cls != 'django_yauth.middleware.YandexAuthMiddleware'
    else 'django_yauth.middleware.YandexAuthTestMiddleware'
    for cls in MIDDLEWARE
]
YAUTH_TEST_USER = {
    'uid': '12345',
    'login': 'login',
}

ALLOWED_HOSTS = ['testserver']
