# -*- coding: utf-8 -*-

from passport.backend.core.builders.frodo.faker import EmptyFrodoParams
from passport.backend.core.test.time_utils.time_utils import TimeNow

from .base_test_data import *


def create_frodo_params(**kwargs):
    params = {
        'login': TEST_LOGIN,
        'iname': 'Some',
        'fname': 'User',
        'from': 'dev',
        'consumer': 'dev',
        'hintqid': '',
        'passwd': '0.0.0.0.0.0.0.0',
        'passwdex': '0.0.0.0.0.0.0.0',
        'hintq': '0.0.0.0.0.0',
        'hintqex': '0.0.0.0.0.0',
        'hinta': '0.0.0.0.0.0',
        'hintaex': '0.0.0.0.0.0',
        'yandexuid': TEST_YANDEXUID_COOKIE,
        'fuid': TEST_FUID01_COOKIE,
        'useragent': TEST_USER_AGENT,
        'host': TEST_HOST,
        'xcountry': 'en',
        'lang': 'en',
        'ip_from': TEST_USER_IP,
        'v2_ip': TEST_USER_IP,
        'valkey': '0000000000',
        'action': 'admsocialreg',
        'v2_track_created': TimeNow(),
        'v2_is_ssl': '1',
        'v2_has_cookie_l': '1',
        'v2_cookie_l_timestamp': str(TEST_COOKIE_TIMESTAMP),
        'v2_cookie_l_uid': str(TEST_UID),
        'v2_cookie_l_login': TEST_LOGIN,
        'v2_has_cookie_yandex_login': '0',
        'v2_has_cookie_my': '1',
        'v2_has_cookie_ys': '0',
        'v2_has_cookie_yp': '0',
        'v2_cookie_my_language': 'tt',
        'v2_cookie_my_block_count': '1',
        'v2_yandex_gid': 'yandex_gid',
        'social_provider': TEST_PROVIDER['code'],
        'v2_account_timezone': 'Europe/Moscow',
        'v2_account_country': 'ru',
        'v2_account_language': 'ru',
        'v2_account_karma': '',
        'v2_accept_language': 'ru',
    }
    params.update(**kwargs)
    return EmptyFrodoParams(**params)
