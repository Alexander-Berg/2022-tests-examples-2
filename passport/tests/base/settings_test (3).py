# -*- coding: utf-8 -*-
# isort:skip_file
from datetime import datetime

import builtins
import yatest.common as yc


# Фейковые настройки для запуска тестов
SECRET_KEY = 'foo'

builtins.ENV_NAME = 'localhost'
builtins.ENV_TYPE = 'development'

from passport.backend.oauth.settings.api_settings import *  # noqa

# Тестовые приложения создаются в момент запуска теста, так что на дату их создания смотреть бессмысленно
FORCE_STATELESS_FOR_AM_CLIENTS_CREATED_AFTER = datetime(2099, 1, 1)

OAUTH_PUBLIC_HOST_TEMPLATE = 'oauth.yandex.%(tld)s'
OAUTH_TLDS = ('ru', 'com')

DEFAULT_PHONE_SCOPE_KEYWORD = 'test:default_phone'
CLIENT_DEFAULT_SCOPE_KEYWORD = 'test:basic_scope'

SERVICES_REQUIRING_PAYMENT_AUTH = ['money']
PAYMENT_AUTH_SERVICE_TO_APP_IDS = {
    'money': ['money.app.1', 'money.app.2'],
}

GEOBASE_LOOKUP_FILE = yc.work_path('test_data/geodata4.bin')
IPREG_LOOKUP_FILE = yc.work_path('test_data/layout-passport-ipreg.json')
DEVICE_NAMES_MAPPING_CONFIG = yc.work_path('test_data/device-names.json')
