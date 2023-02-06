# -*- coding: utf-8 -*-
# isort:skip_file
import yatest.common as yc

from datetime import datetime

# Фейковые настройки для запуска тестов
from passport.backend.oauth.api.settings.default_settings import *  # noqa

FORBID_NONPUBLIC_GRANT_TYPES = False
PROTECT_YANDEX_CLIENTS_FROM_DESTRUCTION = True

# Тестовые приложения создаются в момент запуска теста, так что на дату их создания смотреть бессмысленно
FORCE_STATELESS_FOR_AM_CLIENTS_CREATED_AFTER = datetime(2099, 1, 1)

OAUTH_PUBLIC_HOST_TEMPLATE = 'oauth.yandex.%(tld)s'
OAUTH_TLDS = ('ru', 'com')

DEPARTMENT_GROUP_PREFIXES = ['staff']

ALLOW_FALLBACK_TO_STATELESS_TOKENS = False

SERVICES_REQUIRING_PAYMENT_AUTH = ['money']
PAYMENT_AUTH_SERVICE_TO_APP_IDS = {
    'money': ['money.app.1', 'money.app.2'],
}

DEFAULT_PHONE_SCOPE_KEYWORD = 'test:default_phone'
CLIENT_DEFAULT_SCOPE_KEYWORD = 'test:basic_scope'

GEOBASE_LOOKUP_FILE = yc.work_path('test_data/geodata4.bin')
IPREG_LOOKUP_FILE = yc.work_path('test_data/layout-passport-ipreg.json')
