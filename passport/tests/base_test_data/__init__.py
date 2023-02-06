# -*- coding: utf-8 -*-
import uuid

from passport.backend.utils.time import timeuuid_to_timestamp


TEST_ENVIRONMENT_VERSION = 1
TEST_ENVIRONMENT_TIMEUUID = uuid.UUID('cb78b616-7f0b-11e5-b8cc-fc7bfc3c8e01')
TEST_ENVIRONMENT_TIMEUUID_V2 = uuid.UUID('00000000-5633-7351-0000-00000000002a')
TEST_ENVIRONMENT_TIMESTAMP = timeuuid_to_timestamp(TEST_ENVIRONMENT_TIMEUUID)
TEST_AS_LIST = ['AS13238']
TEST_COUNTRY_ID = 225
TEST_CITY_ID = 213
TEST_BROWSER_ID = 1
TEST_OS_ID = 55
TEST_YANDEXUID_TIMESTAMP = 99

TEST_ENV_PROFILE_KWARGS = {
    'timeuuid': TEST_ENVIRONMENT_TIMEUUID.bytes,
    'timestamp': TEST_ENVIRONMENT_TIMESTAMP,
    'AS_list': TEST_AS_LIST,
    'country_id': TEST_COUNTRY_ID,
    'city_id': TEST_CITY_ID,
    'browser_id': TEST_BROWSER_ID,
    'os_id': TEST_OS_ID,
    'yandexuid_timestamp': TEST_YANDEXUID_TIMESTAMP,
}

TEST_ENV_PROFILE_KWARGS_V2 = {
    'timeuuid': TEST_ENVIRONMENT_TIMEUUID_V2.bytes,
    'timestamp': TEST_ENVIRONMENT_TIMESTAMP,
    'AS_list': TEST_AS_LIST,
    'country_id': TEST_COUNTRY_ID,
    'city_id': TEST_CITY_ID,
    'browser_id': TEST_BROWSER_ID,
    'os_id': TEST_OS_ID,
    'yandexuid_timestamp': TEST_YANDEXUID_TIMESTAMP,
}

UATRAITS_SETTINGS = {
    'BROWSER_ENCODE': {None: 0, 'OperaMini': 1},
    'BROWSER_DECODE': {0: None, 1: 'OperaMini'},
    'OS_ENCODE': {(None, None): 0, ('Java', None): 55, ('Android KitKat', '4.4.2'): 201, ('Android KitKat', '4.4.3'): 212},
    'OS_DUMB_ENCODE': {None: 0, 'Java': 55, 'Android KitKat': 107},
    'OS_DECODE': {0: (None, None), 55: ('Java', None), 201: ('Android KitKat', '4.4.2'), 212: ('Android KitKat', '4.4.3')},
}
