# -*- coding: utf-8 -*-

from core_djangosettings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BILLING_HOST = 'http://mbi1ft.yandex.ru:34861'
YANDEX_BLACKBOX_URL = 'http://blackbox-mimino.yandex.net/blackbox'
YANDEX_TEAM_BLACKBOX_URL = 'http://blackbox-ipv6.yandex-team.ru/blackbox/'
YANDEX_BLACKBOX_URL_TEST_ON_TESTING = 'http://blackbox-test.yandex.net/blackbox/'
EXTERNAL_SESSION_REFRESH_URL = 'https://passport.yandex.ru/auth/update/?retpath='
INTERNAL_SESSION_REFRESH_URL = 'https://passport.yandex-team.ru/auth/update/?retpath='
INTERNAL_SESSION_CREATE_URL = 'https://passport.yandex-team.ru/auth?retpath='

# For CORS
SURGE_API_EXTERNAL_HOST = (
    'http://tariff-editor.frgt.taxi-front01h.taxi.dev.yandex.ru'
)
GEOAREAS_API_EXTERNAL_HOST = (
    'http://tariff-editor.frgt.taxi-front01h.taxi.dev.yandex.ru'
)
QUEUES_API_EXTERNAL_HOST = GEOAREAS_API_EXTERNAL_HOST
TARIFFEDITOR_API_EXTERNAL_HOST = GEOAREAS_API_EXTERNAL_HOST
PROMOTIONS_API_EXTERNAL_HOST = GEOAREAS_API_EXTERNAL_HOST
SUBVENTIONS_API_EXTERNAL_HOST = GEOAREAS_API_EXTERNAL_HOST
APP_VERSION_INFO_EXTERNAL_HOST = GEOAREAS_API_EXTERNAL_HOST
EXPERIMENTS_API_EXTERNAL_HOST = GEOAREAS_API_EXTERNAL_HOST
# FIXME: I don't know this should be this way
# no one gave me clarifications so I just copy-n-paste this strange staff
CLASSIFIER_API_EXTERNAL_HOST = GEOAREAS_API_EXTERNAL_HOST
PERMITS_WHITELIST_EXTERNAL_HOST = GEOAREAS_API_EXTERNAL_HOST
