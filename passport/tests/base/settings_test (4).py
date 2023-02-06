# -*- coding: utf-8 -*-
# isort:skip_file
import yatest.common as yc


# Фейковые настройки для запуска тестов
from passport.backend.oauth.tvm_api.settings.default_settings import *  # noqa

DEPARTMENT_GROUP_PREFIXES = ['staff']

ABC_SCOPE_KEYWORD = 'test:abc'
DEFAULT_PHONE_SCOPE_KEYWORD = 'test:default_phone'
CLIENT_DEFAULT_SCOPE_KEYWORD = 'test:basic_scope'

IPREG_LOOKUP_FILE = yc.work_path('test_data/layout-passport-ipreg.json')
