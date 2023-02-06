# -*- coding: utf-8 -*-

from core_djangosettings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BILLING_HOST = 'http://mbi1ft.yandex.ru:34861'
EXTERNAL_SESSION_REFRESH_URL = 'https://passport.yandex.ru/auth/update/?retpath='
INTERNAL_SESSION_REFRESH_URL = 'https://passport.yandex-team.ru/auth/update/?retpath='

YANDEX_BLACKBOX_URL = 'http://blackbox-mimino.yandex.net/blackbox'
