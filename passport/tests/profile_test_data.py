# -*- coding: utf-8 -*-

from dateutil import rrule
from passport.backend.profile.utils.helpers import (
    from_str_to_date,
    to_date_str,
)
import yenv


# Конфигурация и данные таблиц для тестов расчета профиля.
# original_path используется для того, чтобы считать атрибуты таблицы, а также для построения временного пути
# в тестовом окружении (если не задан target_path)
FRESH_PASSPORT_LOG_DATA = {
    'original_path': '//statbox/passport-log',
    'date': '2016-07-10',
    'rows': [
        {
            'laas_response': '{"is_user_choice": false, "region_id": 236, "suspected_region_city": -1, '
                             '"suspected_longitude": 0.0, "city_id": 236, "probable_regions_reliability": 1.0, '
                             '"precision": 2, "longitude": 52.39582, "suspected_location_accuracy": 0, '
                             '"should_update_cookie": false, "location_unixtime": 1468098440, '
                             '"suspected_region_id": -1, "suspected_precision": 0, '
                             '"latitude": 55.743553, "probable_regions": [], '
                             '"suspected_latitude": 0.0, "location_accuracy": 15000, "suspected_location_unixtime": 0}',
            'retpath': 'https://mail.yandex.ru', 'ip': '178.207.150.130',
            'source_uri': 'prt://passport@passport-na5.yandex.net/var/log/yandex/passport-api/statbox/statbox.log',
            'py': '1',
            '_stbx': 'rt3.fol--passport--passport-log:0:666527073:\xf9l|\xd1U\x01\x00\x00:\xff\xff\xff\xff\xff\xff'
                     '\xff\xff:\x10y\xe5\x08\xc6p{DY\xbc\xb0\xc9\xfe9\x0c\x8f\xaf',
            'track_id': 'b354f08157106ea8ea065f542199593583', 'unixtime': '1468098440',
            'referer': 'https://www.yandex.ru/', 'subkey': '', 'tskv_format': 'passport-log',
            'input_login': 'supersaiyantempy24', 'action': 'submitted', 'iso_eventtime': '2016-07-10 00:07:20',
            'mode': 'any_auth',
            'cookie_yp': '1470690390.ygu.1#1475874397.ww.1#1483866397.szm.1_00:1440x900:1440x775',
            'type': 'password', 'yandexuid': '3696597041468098389',
            'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.103 Safari/537.36',
        },
        {
            '_stbx': 'rt3.fol--passport--passport-log:0:666527073:\xf9l|\xd1U\x01\x00\x00:\xff\xff\xff\xff\xff\xff'
                     '\xff\xff:\x10y\xe5\x08\xc6p{DY\xbc\xb0\xc9\xfe9\x0c\x8f\xaf',
            'action': 'ufo_profile_checked',
            'current': '{"timeuuid": "1fa6e530-4619-11e6-9e88-002590942c30", "os_id": 33, "AS_list": ["AS28840"], '
                       '"city_id": 236, "timestamp": 1468098440, "browser_id": 6, "country_id": 225, '
                       '"yandexuid_timestamp": 1468098389}',
            'input_login': 'supersaiyantempy24',
            'ip': '178.207.150.130',
            'iso_eventtime': '2016-07-10 00:07:20',
            'mode': 'any_auth',
            'py': '1',
            'source_uri': 'prt://passport@passport-na5.yandex.net/var/log/yandex/passport-api/statbox/statbox.log',
            'subkey': '',
            'tensornet_estimate': '0.9807',
            'tensornet_model': 'profile-passp-14054',
            'tensornet_status': '1',
            'track_id': 'b354f08157106ea8ea065f542199593583',
            'tskv_format': 'passport-log',
            'ufo_distance': '100',
            'ufo_status': '1',
            'uid': '390642803',
            'unixtime': '1468098440',
            'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.103 Safari/537.36',
            'yandexuid': '3696597041468098389',
        },
        {
            '_stbx': 'rt3.fol--passport--passport-log:0:666527085:]r|\xd1U\x01\x00\x00:\xff\xff\xff\xff\xff\xff\xff'
                     '\xff:\x10y\xe5\x08\xc6p{DY\xbc\xb0\xc9\xfe9\x0c\x8f\xaf',
            'action': 'profile_threshold_exceeded',
            'decision_source': 'ufo',
            'email_sent': '1',
            'input_login': 'supersaiyantempy24',
            'ip': '178.207.150.130',
            'is_password_change_required': '0',
            'iso_eventtime': '2016-07-10 00:07:20',
            'mode': 'any_auth',
            'py': '1',
            'source_uri': 'prt://passport@passport-na5.yandex.net/var/log/yandex/passport-api/statbox/statbox.log',
            'subkey': '',
            'track_id': 'b354f08157106ea8ea065f542199593583',
            'tskv_format': 'passport-log',
            'uid': '390642803',
            'unixtime': '1468098440',
            'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.103 Safari/537.36',
            'yandexuid': '3696597041468098389',
        },
        {
            '_stbx': 'rt3.fol--passport--passport-log:0:666527085:^r|\xd1U\x01\x00\x00:\xff\xff\xff\xff\xff\xff\xff'
                     '\xff:\x10y\xe5\x08\xc6p{DY\xbc\xb0\xc9\xfe9\x0c\x8f\xaf',
            'action': 'shown',
            'challenges': 'phone',
            'consumer': 'passport',
            'ip': '178.207.150.130',
            'iso_eventtime': '2016-07-10 00:07:20',
            'mode': 'auth_challenge',
            'py': '1',
            'source_uri': 'prt://passport@passport-na5.yandex.net/var/log/yandex/passport-api/statbox/statbox.log',
            'subkey': '',
            'track_id': 'b354f08157106ea8ea065f542199593583',
            'tskv_format': 'passport-log',
            'uid': '390642803',
            'unixtime': '1468098440',
            'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.103 Safari/537.36',
            'yandexuid': '3696597041468098389',
        },
        {
            '_stbx': 'rt3.fol--passport--passport-log:0:666527253:\x91\xa5|\xd1U\x01\x00\x00:\xff\xff\xff\xff\xff'
                     '\xff\xff\xff:\x10y\xe5\x08\xc6p{DY\xbc\xb0\xc9\xfe9\x0c\x8f\xaf',
            'action': 'shown',
            'challenges': 'phone',
            'consumer': 'passport',
            'ip': '178.207.150.130',
            'iso_eventtime': '2016-07-10 00:07:33',
            'mode': 'auth_challenge',
            'py': '1',
            'source_uri': 'prt://passport@passport-na5.yandex.net/var/log/yandex/passport-api/statbox/statbox.log',
            'subkey': '',
            'track_id': 'b354f08157106ea8ea065f542199593583',
            'tskv_format': 'passport-log',
            'uid': '390642803',
            'unixtime': '1468098453',
            'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.103 Safari/537.36',
            'yandexuid': '3696597041468098389',
        },
        {
            '_stbx': 'rt3.fol--passport--passport-log:0:666527253:\x91\xa5|\xd1U\x01\x00\x00:\xff\xff\xff'
                     '\xff\xff\xff\xff\xff:\x10y\xe5\x08\xc6p{DY\xbc\xb0\xc9\xfe9\x0c\x8f\xaf',
            'action': 'passed',
            'challenge': 'phone',
            'consumer': 'passport',
            'ip': '178.207.150.130',
            'iso_eventtime': '2016-07-10 00:07:33',
            'mode': 'auth_challenge',
            'py': '1',
            'source_uri': 'prt://passport@passport-na5.yandex.net/var/log/yandex/passport-api/statbox/statbox.log',
            'subkey': '',
            'track_id': 'b354f08157106ea8ea065f542199593583',
            'tskv_format': 'passport-log',
            'uid': '390642803',
            'unixtime': '1468098453',
            'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.103 Safari/537.36',
            'yandexuid': '3696597041468098389',
        },
        {
            '_stbx': 'rt3.fol--passport--passport-log:0:666527253:\x91\xa5|\xd1U\x01\x00\x00:\xff\xff\xff\xff\xff\xff'
                     '\xff\xff:\x10y\xe5\x08\xc6p{DY\xbc\xb0\xc9\xfe9\x0c\x8f\xaf',
            'action': 'cookie_set',
            'authid': '1468098453000:gpbPsg:83',
            'captcha_passed': '0',
            'cookie_version': '3',
            'input_login': 'supersaiyantempy24',
            'ip': '178.207.150.130',
            'ip_country': 'ru',
            'is_auth_challenge_shown': '1',
            'iso_eventtime': '2016-07-10 00:07:33',
            'mode': 'any_auth',
            'person_country': 'ru',
            'py': '1',
            'retpath': 'https://mail.yandex.ru',
            'session_method': 'create',
            'source_uri': 'prt://passport@passport-na5.yandex.net/var/log/yandex/passport-api/statbox/statbox.log',
            'subkey': '',
            'track_id': 'b354f08157106ea8ea065f542199593583',
            'tskv_format': 'passport-log',
            'ttl': '5',
            'uid': '390642803',
            'uids_count': '1',
            'unixtime': '1468098453',
            'user_agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/51.0.2704.103 Safari/537.36',
            'yandexuid': '3696597041468098389',
        },
    ],
}


BUILD_PROFILE_INPUT_TABLES = [
    FRESH_PASSPORT_LOG_DATA,
    {
        'original_path': '//statbox/blackbox-log',
        'date': '2016-07-10',
        'rows': [
            {
                'status': 'ses_update', 'comment': 'aid=1436609877868:H2ujHw:2;ttl=5;host=.yandex.ru;',
                'iso_eventtime': '2016-07-10 04:44:52', 'uid': '45607055', 'unixtime': '1468115092',
                'source_uri': 'prt://blackbox@pass-i82.sezam.yandex.net/opt/sezam-logs/blackbox-auth.log',
                'user_ip': '5.141.235.105', 'version': '1', 'subkey': '', 'host_id': 'A9', 'action': 'auth',
                'tskv_format': 'blackbox-log', 'login': 'l-bayanova', 'type': 'web', 'client_name': 'bb',
                '_stbx': 'rt3.iva--other--other:143:72471675:A\x85z\xd2U\x01\x00\x00:\xff\xff\xff\xff\xff\xff'
                         '\xff\xff:\x10L\xb3e\x91\x7f\x8fC\x8b\x82\xe0\xe7\xcfR\t\xebt',
            },
        ],
    },
    {
        'original_path': '//statbox/oauth-log',
        'date': '2016-07-10',
        'rows': [
            {
                'app_id': None, 'mode': 'issue_token', 'grant_type': 'sessionid', 'am_version': '6.7.1(607010118)', 'user_ip': '89.107.139.118', 'status': 'ok',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 '
                'YaBrowser/19.10.3.281 Yowser/2.5 Safari/537.36', 'action': 'issue', 'unixtime': '1468115092', 'uid': '390642803', 'device_id':
                '0E0ED01C-9B83-43B5-9E87-3FA5E42FA7FD', 'login': 'supersaiyantempy24', 'yandexuid': '3696597041468098389', 'cloud_token': 'cl-xxx', '_stbx':
                'rt3.man--oauth--oauth-log:2@@1013019781@@base64:m4S_LBSmIcmUVYB3RZw8YQ@@1575016698042@@1575016716@@oauth-log@@141647090@@1575016698299'
            },
            # запись без cloud_token - это ок
            {
                'app_id': None, 'mode': 'issue_token', 'grant_type': 'sessionid', 'am_version': '6.7.1(607010118)', 'user_ip': '89.107.139.118', 'status': 'ok',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 '
                'YaBrowser/19.10.3.281 Yowser/2.5 Safari/537.36', 'action': 'issue', 'unixtime': '1468115092', 'uid': '390642803', 'device_id':
                '0E0ED01C-9B83-43B5-9E87-3FA5E42FA7FD', 'login': 'supersaiyantempy24', 'yandexuid': '3696597041468098389', '_stbx':
                'rt3.man--oauth--oauth-log:2@@1013019781@@base64:m4S_LBSmIcmUVYB3RZw8YQ@@1575016698042@@1575016716@@oauth-log@@141647090@@1575016698299'
            },
            {  # запись с непонятным юникодом в полях, будет отсеяна, так как явно не валидна и не должна составлять результирующий профиль
                'app_id': None, 'mode': 'issue_token', 'grant_type': 'sessionid', 'am_version': '7.9.0%28709000329%29§°§', 'user_ip': '89.107.139.118', 'status': 'ok',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 '
                              'YaBrowser/19.10.3.281 Yowser/2.5 Safari/537.36', 'action': 'issue', 'unixtime': '1468115092', 'uid': '390642803', 'device_id':
                'Android+§°§°§+(REL)', 'login': 'supersaiyantempy24', 'yandexuid': '3696597041468098389', '_stbx':
                'rt3.man--oauth--oauth-log:2@@1013019782@@base64:m4S_LBSmIcmUVYB3RZw8YQ@@1575016698042@@1575016716@@oauth-log@@141647090@@1575016698299'
            },
            {  # запись с пустым am_version, будет проигнорирована
                'app_id': None, 'mode': 'issue_token', 'grant_type': 'sessionid', 'am_version': None, 'user_ip': '89.107.139.118', 'status': 'ok',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 '
                              'YaBrowser/19.10.3.281 Yowser/2.5 Safari/537.36', 'action': 'issue', 'unixtime': '1468115092', 'uid': '390642803', 'device_id':
                'Android+§°§°§+(REL)', 'login': 'supersaiyantempy24', 'yandexuid': '3696597041468098389', '_stbx':
                'rt3.man--oauth--oauth-log:2@@1033019782@@base64:m4S_LBSmIcmUVYB3RZw8YQ@@1575016698042@@1575016716@@oauth-log@@141647090@@1575016698299'
            },
        ],
    },
    {
        'original_path': '//home/passport/production/profile/profile',
        'target_path': '//home/passport/%s/profile/profile' % yenv.type,
        'date': '2016-05-11',
        'rows': [],
    },
    {
        'original_path': '//home/passport/production/profile/profile',
        'target_path': '//home/passport/%s/profile/profile' % yenv.type,
        'date': '2016-04-11',
        'rows': [],
    },
    {
        'original_path': '//home/passport/production/profile/profile',
        'target_path': '//home/passport/%s/profile/profile' % yenv.type,
        'date': '2016-03-12',
        'rows': [],
    },
    {
        'original_path': '//home/passport/production/profile/profile',
        'target_path': '//home/passport/%s/profile/profile' % yenv.type,
        'date': '2016-02-11',
        'rows': [],
    },
]

for date in rrule.rrule(rrule.DAILY, dtstart=from_str_to_date('2016-06-10'), until=from_str_to_date('2016-07-09')):
    BUILD_PROFILE_INPUT_TABLES.append(
        {
            'original_path': '//home/passport/production/profile/auth',
            'target_path': '//home/passport/%s/profile/auth' % yenv.type,
            'date': to_date_str(date),
            'rows': [],
        },
    )

for date in rrule.rrule(rrule.DAILY, dtstart=from_str_to_date('2016-06-10'), until=from_str_to_date('2016-07-09')):
    BUILD_PROFILE_INPUT_TABLES.append(
        {
            'original_path': '//home/passport/production/profile/bb',
            'target_path': '//home/passport/%s/profile/bb' % yenv.type,
            'date': to_date_str(date),
            'rows': [],
        },
    )

for date in rrule.rrule(rrule.DAILY, dtstart=from_str_to_date('2016-06-10'), until=from_str_to_date('2016-07-09')):
    BUILD_PROFILE_INPUT_TABLES.append(
        {
            'original_path': '//home/passport/production/profile/profile',
            'target_path': '//home/passport/%s/profile/profile' % yenv.type,
            'date': to_date_str(date),
            'rows': [],
        },
    )

for date in rrule.rrule(rrule.DAILY, dtstart=from_str_to_date('2016-06-10'), until=from_str_to_date('2016-07-09')):
    BUILD_PROFILE_INPUT_TABLES.append(
        {
            'original_path': '//home/passport/production/profile/oauth',
            'target_path': '//home/passport/%s/profile/oauth' % yenv.type,
            'date': to_date_str(date),
            'rows': [],
        },
    )


PROFILE_ROWS = [
    {
        'uid': 45607055,

        'su_ip_freq_1d': [[u'5.141.235.105', 1]],
        'su_ip_freq_1w': [[u'5.141.235.105', 1]],
        'su_ip_freq_1m': [[u'5.141.235.105', 1]],
        'su_ip_freq_3m': [[u'5.141.235.105', 1]],
        'su_ip_freq_6m': [[u'5.141.235.105', 1]],

        'su_as_list_freq_1d': [[u'AS12389', 1]],
        'su_as_list_freq_1w': [[u'AS12389', 1]],
        'su_as_list_freq_1m': [[u'AS12389', 1]],
        'su_as_list_freq_3m': [[u'AS12389', 1]],
        'su_as_list_freq_6m': [[u'AS12389', 1]],

        'su_city_freq_1d': [[55, 1]],
        'su_city_freq_1w': [[55, 1]],
        'su_city_freq_1m': [[55, 1]],
        'su_city_freq_3m': [[55, 1]],
        'su_city_freq_6m': [[55, 1]],

        'su_country_freq_1d': [[225, 1]],
        'su_country_freq_1w': [[225, 1]],
        'su_country_freq_1m': [[225, 1]],
        'su_country_freq_3m': [[225, 1]],
        'su_country_freq_6m': [[225, 1]],

        'su_day_part_freq_1d': [[0, 1]],
        'su_day_part_freq_1w': [[0, 1]],
        'su_day_part_freq_1m': [[0, 1]],
        'su_day_part_freq_3m': [[0, 1]],
        'su_day_part_freq_6m': [[0, 1]],

        'su_weekday_freq_1d': [[7, 1]],
        'su_weekday_freq_1w': [[7, 1]],
        'su_weekday_freq_1m': [[7, 1]],
        'su_weekday_freq_3m': [[7, 1]],
        'su_weekday_freq_6m': [[7, 1]],
    },
    {
        'uid': 390642803,

        'it_am_version_freq_1d': [[u'6.7.1', 2]],
        'it_am_version_freq_1w': [[u'6.7.1', 2]],
        'it_am_version_freq_1m': [[u'6.7.1', 2]],
        'it_am_version_freq_3m': [[u'6.7.1', 2]],
        'it_am_version_freq_6m': [[u'6.7.1', 2]],

        'ip_freq_1d': [[u'178.207.150.130', 1]],
        'ip_freq_1w': [[u'178.207.150.130', 1]],
        'ip_freq_1m': [[u'178.207.150.130', 1]],
        'ip_freq_3m': [[u'178.207.150.130', 1]],
        'ip_freq_6m': [[u'178.207.150.130', 1]],

        'browser_os_freq_1d': [[u'Chrome 51.0.2704.103 - Windows 7', 1]],
        'browser_os_freq_1w': [[u'Chrome 51.0.2704.103 - Windows 7', 1]],
        'browser_os_freq_1m': [[u'Chrome 51.0.2704.103 - Windows 7', 1]],
        'browser_os_freq_3m': [[u'Chrome 51.0.2704.103 - Windows 7', 1]],
        'browser_os_freq_6m': [[u'Chrome 51.0.2704.103 - Windows 7', 1]],

        'is_mobile_freq_1d': [[0, 1]],
        'is_mobile_freq_1w': [[0, 1]],
        'is_mobile_freq_1m': [[0, 1]],
        'is_mobile_freq_3m': [[0, 1]],
        'is_mobile_freq_6m': [[0, 1]],

        'it_weekday_freq_1d': [[7, 2]],
        'it_weekday_freq_1w': [[7, 2]],
        'it_weekday_freq_1m': [[7, 2]],
        'it_weekday_freq_3m': [[7, 2]],
        'it_weekday_freq_6m': [[7, 2]],

        'succ_auth_count_1d': 1,
        'succ_auth_count_1w': 1,
        'succ_auth_count_1m': 1,

        'captcha_passed_1d': 0,
        'captcha_passed_1w': 0,
        'captcha_passed_1m': 0,

        'yandexuid_freq_1d': [[u'3696597041468098389', 1]],
        'yandexuid_freq_1w': [[u'3696597041468098389', 1]],
        'yandexuid_freq_1m': [[u'3696597041468098389', 1]],
        'yandexuid_freq_3m': [[u'3696597041468098389', 1]],
        'yandexuid_freq_6m': [[u'3696597041468098389', 1]],

        'os_name_freq_1d': [[u'Windows 7', 1]],
        'os_name_freq_1w': [[u'Windows 7', 1]],
        'os_name_freq_1m': [[u'Windows 7', 1]],
        'os_name_freq_3m': [[u'Windows 7', 1]],
        'os_name_freq_6m': [[u'Windows 7', 1]],

        'os_family_freq_1d': [[u'Windows', 1]],
        'os_family_freq_1w': [[u'Windows', 1]],
        'os_family_freq_1m': [[u'Windows', 1]],
        'os_family_freq_3m': [[u'Windows', 1]],
        'os_family_freq_6m': [[u'Windows', 1]],

        'browser_freq_1d': [[u'Chrome 51.0.2704.103', 1]],
        'browser_freq_1w': [[u'Chrome 51.0.2704.103', 1]],
        'browser_freq_1m': [[u'Chrome 51.0.2704.103', 1]],
        'browser_freq_3m': [[u'Chrome 51.0.2704.103', 1]],
        'browser_freq_6m': [[u'Chrome 51.0.2704.103', 1]],

        'browser_name_freq_1d': [[u'Chrome', 1]],
        'browser_name_freq_1w': [[u'Chrome', 1]],
        'browser_name_freq_1m': [[u'Chrome', 1]],
        'browser_name_freq_3m': [[u'Chrome', 1]],
        'browser_name_freq_6m': [[u'Chrome', 1]],

        'day_part_freq_1d': [[0, 1]],
        'day_part_freq_1w': [[0, 1]],
        'day_part_freq_1m': [[0, 1]],
        'day_part_freq_3m': [[0, 1]],
        'day_part_freq_6m': [[0, 1]],

        'weekday_freq_1d': [[7, 1]],
        'weekday_freq_1w': [[7, 1]],
        'weekday_freq_1m': [[7, 1]],
        'weekday_freq_3m': [[7, 1]],
        'weekday_freq_6m': [[7, 1]],

        'it_day_part_freq_1d': [[0, 2]],
        'it_day_part_freq_1w': [[0, 2]],
        'it_day_part_freq_1m': [[0, 2]],
        'it_day_part_freq_3m': [[0, 2]],
        'it_day_part_freq_6m': [[0, 2]],

        'it_country_freq_1d': [[225, 2]],
        'it_country_freq_1w': [[225, 2]],
        'it_country_freq_1m': [[225, 2]],
        'it_country_freq_3m': [[225, 2]],
        'it_country_freq_6m': [[225, 2]],

        'country_freq_1d': [[225, 1]],
        'country_freq_1w': [[225, 1]],
        'country_freq_1m': [[225, 1]],
        'country_freq_3m': [[225, 1]],
        'country_freq_6m': [[225, 1]],

        'city_freq_1d': [[11127, 1]],
        'city_freq_1w': [[11127, 1]],
        'city_freq_1m': [[11127, 1]],
        'city_freq_3m': [[11127, 1]],
        'city_freq_6m': [[11127, 1]],

        'it_city_freq_1d': [[146, 2]],
        'it_city_freq_1w': [[146, 2]],
        'it_city_freq_1m': [[146, 2]],
        'it_city_freq_3m': [[146, 2]],
        'it_city_freq_6m': [[146, 2]],

        'it_device_id_freq_1d': [[u'0E0ED01C-9B83-43B5-9E87-3FA5E42FA7FD', 2]],
        'it_device_id_freq_1w': [[u'0E0ED01C-9B83-43B5-9E87-3FA5E42FA7FD', 2]],
        'it_device_id_freq_1m': [[u'0E0ED01C-9B83-43B5-9E87-3FA5E42FA7FD', 2]],
        'it_device_id_freq_3m': [[u'0E0ED01C-9B83-43B5-9E87-3FA5E42FA7FD', 2]],
        'it_device_id_freq_6m': [[u'0E0ED01C-9B83-43B5-9E87-3FA5E42FA7FD', 2]],

        'it_cloud_token_freq_1d': [[u'cl-xxx', 1]],
        'it_cloud_token_freq_1w': [[u'cl-xxx', 1]],
        'it_cloud_token_freq_1m': [[u'cl-xxx', 1]],
        'it_cloud_token_freq_3m': [[u'cl-xxx', 1]],
        'it_cloud_token_freq_6m': [[u'cl-xxx', 1]],

        'referer_host_2_freq_1d': [[u'yandex.ru', 1]],
        'referer_host_2_freq_1w': [[u'yandex.ru', 1]],
        'referer_host_2_freq_1m': [[u'yandex.ru', 1]],
        'referer_host_2_freq_3m': [[u'yandex.ru', 1]],
        'referer_host_2_freq_6m': [[u'yandex.ru', 1]],

        'retpath_host_2_freq_1d': [[u'yandex.ru', 1]],
        'retpath_host_2_freq_1w': [[u'yandex.ru', 1]],
        'retpath_host_2_freq_1m': [[u'yandex.ru', 1]],
        'retpath_host_2_freq_3m': [[u'yandex.ru', 1]],
        'retpath_host_2_freq_6m': [[u'yandex.ru', 1]],

        'referer_host_3_freq_1d': [[u'www.yandex.ru', 1]],
        'referer_host_3_freq_1w': [[u'www.yandex.ru', 1]],
        'referer_host_3_freq_1m': [[u'www.yandex.ru', 1]],
        'referer_host_3_freq_3m': [[u'www.yandex.ru', 1]],
        'referer_host_3_freq_6m': [[u'www.yandex.ru', 1]],

        'retpath_host_3_freq_1d': [[u'mail.yandex.ru', 1]],
        'retpath_host_3_freq_1w': [[u'mail.yandex.ru', 1]],
        'retpath_host_3_freq_1m': [[u'mail.yandex.ru', 1]],
        'retpath_host_3_freq_3m': [[u'mail.yandex.ru', 1]],
        'retpath_host_3_freq_6m': [[u'mail.yandex.ru', 1]],

        'as_list_freq_1d': [[u'AS28840', 1]],
        'as_list_freq_1w': [[u'AS28840', 1]],
        'as_list_freq_1m': [[u'AS28840', 1]],
        'as_list_freq_3m': [[u'AS28840', 1]],
        'as_list_freq_6m': [[u'AS28840', 1]],

        'it_as_list_freq_1d': [[u'AS201776', 2]],
        'it_as_list_freq_1w': [[u'AS201776', 2]],
        'it_as_list_freq_1m': [[u'AS201776', 2]],
        'it_as_list_freq_3m': [[u'AS201776', 2]],
        'it_as_list_freq_6m': [[u'AS201776', 2]],
    },
]


UPLOADED_PROFILES = [
    {
        'su_as_list_freq_1d': [['AS31094', 1L]],
        'su_city_freq_1d': [[55L, 1L]],
        'su_country_freq_1d': [[225L, 1L]],
        'su_day_part_freq_1d': [[0L, 1L]],
        'su_ip_freq_1d': [['5.141.235.105', 1L]],
        'su_weekday_freq_1d': [[7L, 1L]],
        'uid': 45607055L,
    },
    {
        'as_list_freq_1d': [['AS28840', 1L]],
        'browser_freq_1d': [['Chrome 51.0.2704', 1L]],
        'browser_name_freq_1d': [['Chrome', 1L]],
        'browser_os_freq_1d': [['Chrome 51.0.2704 - Windows 7', 1L]],
        'captcha_passed_1d': 0L,
        'city_freq_1d': [[236L, 1L]],
        'country_freq_1d': [[225L, 1L]],
        'day_part_freq_1d': [[0L, 1L]],
        'ip_freq_1d': [['178.207.150.130', 1L]],
        'is_mobile_freq_1d': [[0L, 1L]],
        'os_family_freq_1d': [['Windows', 1L]],
        'os_name_freq_1d': [['Windows 7', 1L]],
        'referer_host_2_freq_1d': [['yandex.ru', 1L]],
        'referer_host_3_freq_1d': [['www.yandex.ru', 1L]],
        'retpath_host_2_freq_1d': [['yandex.ru', 1L]],
        'retpath_host_3_freq_1d': [['mail.yandex.ru', 1L]],
        'succ_auth_count_1d': 1L,
        'uid': 390642803L,
        'weekday_freq_1d': [[7L, 1L]],
        'yandexuid_freq_1d': [['3696597041468098389', 1L]],
    },
]


UPLOAD_PROFILE_INPUT_TABLES = [FRESH_PASSPORT_LOG_DATA] + [
    {
        'original_path': '//home/passport/production/profile/profile',
        'target_path': '//home/passport/%s/profile/profile' % yenv.type,
        'date': '2016-07-10',
        'rows': PROFILE_ROWS,
        'attributes': {
            'profile_daily_job_status': {
                'job_finished_source_row_count': 7,
                'job_finished_timestamp': 1468213664,
                'job_started_source_row_count': 7,
                'job_started_timestamp': 1468202404,
                'need_rerun': 'false',
            },
        }
    },
]
