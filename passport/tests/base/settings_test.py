# -*- coding: utf-8 -*-
# isort:skip_file
import yatest.common as yc

from passport.backend.oauth.core.test.base_test_data import (
    TEST_LOGIN,
    TEST_UID,
)

# Фейковые настройки для запуска тестов
from passport.backend.oauth.admin.settings.default_settings_production import *  # noqa
from passport.backend.oauth.admin.settings.default_settings_production import MIDDLEWARE

REQUIRE_HTTPS = False

MIDDLEWARE = [
    cls if cls != 'django_yauth.middleware.YandexAuthMiddleware'
    else 'django_yauth.middleware.YandexAuthTestMiddleware'
    for cls in MIDDLEWARE
]
YAUTH_TEST_USER = {
    'uid': TEST_UID,
    'login': TEST_LOGIN,
}

DEFAULT_PHONE_SCOPE_KEYWORD = 'test:default_phone'
CLIENT_DEFAULT_SCOPE_KEYWORD = 'test:basic_scope'

GEOBASE_LOOKUP_FILE = yc.work_path('test_data/geodata4.bin')
IPREG_LOOKUP_FILE = yc.work_path('test_data/layout-passport-ipreg.json')
