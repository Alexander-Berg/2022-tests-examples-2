# -*- coding: utf-8 -*-

from copy import deepcopy


TEST_UID = 1
TEST_RESTORE_ID = '7E,13079,1408955588.53,1,6e777e67590d34c8365a6990090b49157e'
TEST_RESTORE_ID_2 = '7E,13079,1408955588.53,1,1234'
TEST_RESTORE_ID_3 = '7F,13079,1408955588.53,2,1234'
TEST_PDD_UID = 1130000000011111
TEST_LOGIN = 'test-login'
TEST_GALATASARAY_ALIAS = 'test-login@galatasaray.net'
TEST_LOGIN_NOT_NORMALIZED = 'Test.Login'
TEST_SUPPORT_UID = 183
TEST_USER_LOGIN = 'user-login'
TEST_COOKIE = 'Session_id=3:1408711252.5.0.1408710928000:vGUJJQ:7e.0|1.0.2|66585.705413.3SNybpx2D_aCv5wrBHfJs48odcY'
TEST_HOST = 'yandex-team.ru'
TEST_IP = '127.0.0.1'
TEST_AUTHORIZATION = 'OAuth 1234'
TEST_REQUEST_SOURCE = 'restore'

TEST_SOCIAL_ALIAS = 'uid-12345678'
TEST_PHONISH_ALIAS = 'phne-12345678'
TEST_PHONE_ALIAS = '79151234567'
TEST_YANDEXOID_ALIAS = 'test_yastaff_login'
TEST_LITE_ALIAS = 'login@lite.ru'
TEST_PDD_ALIAS = u'login@окна.рф'
TEST_PDD_LOGIN = u'login@окна.рф'
TEST_PDD_DOMAIN_ENCODED = u'xn--80atjc.xn--p1ai'
TEST_PDD_ALIAS_2 = u'login_2@окна.рф'
# Специальная кодировка алиасов для таблицы removed_aliases
TEST_PDD_ALIAS_ENCODED = u'xn--80atjc.xn--p1ai/login'
TEST_PDD_ALIAS_ENCODED_AS_LITE = u'login@xn--80atjc.xn--p1ai'
TEST_PDD_ALIAS_2_ENCODED = u'xn--80atjc.xn--p1ai/login_2'

TEST_CRYPT_PASSWORD = '1:$1$LRVl.MiL$/B.GhedFTs9nHORnw5DvH0'

DATETIME_FOR_TS_1 = u'1970-01-01 03:00:01 MSK+0300'
DATETIME_FOR_TS_2 = u'1970-01-01 03:00:02 MSK+0300'
DATETIME_FOR_TS_4 = u'1970-01-01 03:00:04 MSK+0300'

TEST_RESTORATION_LINK = u'https://rest.orat.ion/lin/k/'

TEST_STRING_FACTOR_NO_MATCH = [['initial_equal', -1], ['symbol_shrink', -1], ['distance', -1], ['xlit_used', -1]]

TEST_SOCIAL_TASK_ID = '0123456789abcdef'

TEST_FACTORS_DATA_VERSION_2 = {
    'version': 2,
    'delivery_addresses': {
        'matches': [],
        'entered': None,
        'account': [],
        'factor': [['entered_count', 0], ['account_count', 0], ['matches_count', 0], ['absence', 0]],
    },
    'restore_status': 'pending',
    'social_accounts': {
        'entered': None,
        'api_status': True,
        'profiles': [],
        'factor_absence': 0,
    },
    'outbound_emails': {
        'matches': [],
        'entered': None,
        'factor': [['entered_count', 0], ['actual_count', 0], ['matches_count', 0], ['absence', 0]],
        'actual': [],
        'api_status': True,
    },
    'registration_country': {
        'factor_id': 1,
        'entered_id': 225,
        'factor': TEST_STRING_FACTOR_NO_MATCH,
        'entered': 'u0420u043eu0441u0456u044f',
        'history_id': 225,
        'history': 'u0420u043eu0441u0441u0438u044f',
    },
    'names': {
        'account': ['test', 'test'],
        'account_factor': {
            'lastname': [['initial_equal', 1], ['symbol_shrink', -1], ['distance', -1], ['xlit_used', -1], ['aggressive_shrink', -1], ['aggressive_equal', -1]],
            'firstname': [['initial_equal', -1], ['symbol_shrink', -1], ['distance', -1], ['xlit_used', -1], ['aggressive_shrink', -1], ['aggressive_equal', -1]]
        },
        'account_status': True,
        'entered': ['test', 'test'],
        'history_status': True,
        'history_factor': {
            'lastname': [['initial_equal', 1], ['symbol_shrink', -1], ['distance', -1], ['xlit_used', -1], ['aggressive_shrink', -1], ['aggressive_equal', -1]],
            'firstname': [['initial_equal', -1], ['symbol_shrink', -1], ['distance', -1], ['xlit_used', -1], ['aggressive_shrink', -1], ['aggressive_equal', -1]]
        },
        'history': ['test', 'test'],
    },
    'phone_numbers': {
        'matches': [],
        'entered': None,
        'factor': [['entered_count', 0], ['history_count', 1], ['matches_count', 0], ['absence', 0]],
        'history': ['79264607453'],
    },
    'request_source': 'changepass',
    'email_blacklist': {
        'matches': [],
        'entered': None,
        'factor': [['entered_count', 0], ['actual_count', 0], ['matches_count', 0], ['absence', 0]],
        'actual': [],
        'api_status': False,
    },
    'user_ip': {'auths_contain_ip_api_status': True, 'actual': '84.201.167.219', 'factor': 1},
    'historydb_api_events_status': True,
    'registration_ip': '77.88.0.85',
    'answer': {
        'history_best_match': None,
        'question': '-1:None',
        'factor_absence': 0,
        'factor': TEST_STRING_FACTOR_NO_MATCH,
        'entered': None,
        'history': [],
    },
    'registration_date': {'entered': '2001-09-03 msd+0400', 'account': '2014-10-21 15:41:59', 'factor': 0.0},
    'registration_city': {
        'factor_id': 1,
        'entered_id': 213,
        'factor': TEST_STRING_FACTOR_NO_MATCH,
        'entered': 'u041cu043eu0441u043au0432u0430',
        'history_id': 213,
        'history': 'u041cu043eu0441u043au0432u0430',
    },
    'birthday': {
        'entered': '1987-11-11',
        'account_factor': 1,
        'history_factor': 1,
        'account': '1987-11-11',
        'history': '1987-11-11',
    },
    'services': {
        'matches': [],
        'entered': [],
        'account': ['mail'],
        'factor': [['entered_count', 0], ['account_count', 1], ['matches_count', 0]],
    },
    'password': {
        'used_until': None,
        'used_since': None,
        'api_status': True,
        'auth_date_entered': None,
        'factor': [['auth_found', -1], ['auth_date', -1]],
    },
    'emails': {
        'matches': [],
        'history_confirmed': [],
        'factor': [
            ['entered_count', 0],
            ['history_count', 0],
            ['matches_count', 0],
            ['history_collected_count', 0],
            ['history_confirmed_count', 0],
            ['matches_collected_count', 0],
            ['matches_confirmed_count', 0],
            ['absence', 0],
        ],
        'history_collected': [],
        'entered': None,
        'history': [],
    },
    'oauth_api_status': True,
    'email_collectors': {
        'matches': [],
        'entered': None,
        'factor': [['entered_count', 0], ['actual_count', 0], ['matches_count', 0], ['absence', 0]],
        'actual': [],
        'api_status': False,
    },
    'ip_stats': {
        'statistics': {
            'status': 'ok',
            'uid': 1130000000051873,
            'different_ips_count': 2,
            'total_auths_count': 4,
            'first_user_ip_auth_timestamp': 1413961019.344068,
            'last_user_ip_auth_timestamp': 1413965789.979167,
            'auths_by_user_ip': 3,
        },
        'auths_ip_statistics_api_status': True,
    },
    'email_folders': {
        'matches': [],
        'entered': None,
        'factor': [['entered_count', 0], ['actual_count', 0], ['matches_count', 0], ['absence', 0]],
        'actual': [],
        'api_status': False,
    },
    'email_whitelist': {
        'matches': [],
        'entered': None,
        'factor': [['entered_count', 0], ['actual_count', 0], ['matches_count', 0], ['absence', 0]],
        'actual': [],
        'api_status': False,
    },
    'user_ip_subnet': {
        'actual': '2a02:6b8::/32',
        'history_ips': ['2a02:6b8:0:2307:613d:988d:911a:16bc'],
        'actual_as_list': ['as13238'],
        'factor': 1,
    },
    'user_env': {
        'history': [
            {'os.name': None, 'yandexuid': '5633677591395745464', 'browser.name': None},
            {'os.name': None, 'yandexuid': '2430869941395667304', 'browser.name': None},
            {'os.name': None, 'yandexuid': '2163529481395842212', 'browser.name': None},
        ],
        'actual': {'os.name': 'Mac OS X Mavericks', 'yandexuid': '7329570481414843658', 'browser.name': 'Safari'},
        'factor': 0,
    },
    'auths_successful_envs_api_status': True,
}

TEST_FACTORS_OUTPUT_VERSION_2 = {
    u'datetime': u'1970-01-01 03:20:34',
    u'restore_id': TEST_RESTORE_ID,
    u'action': u'restore_semi_auto_request',
    u'ip_info': {
        u'errors': {
            u'auths_contain_ip_api_status': True,
            u'auths_successful_envs_api_status': True,
            u'auths_ip_statistics_api_status': True,
        },
        u'factors': {
            u'user_ip_in_history': u'match',
            u'user_subnet_in_history': u'match',
            u'user_ip_eq_registration_ip': u'no_match',
            u'user_ua_in_history': u'no_match',
        },
        u'user_ip_last_auth_datetime': u'2014-10-22 12:16:29 MSK+0400',
        u'user_ip_auths_count': 3,
        u'max_auths_ip': u'-',
        u'different_ips_count': 2,
        u'user_ip': u'84.201.167.219',
        u'user_ip_auths_percent': u'75.00',
        u'max_auths_ip_auths_count': u'-',
        u'registration_ip': u'77.88.0.85',
        u'total_auths_count': 4,
        u'user_ip_first_auth_datetime': u'2014-10-22 10:56:59 MSK+0400',
    },
    u'groups': [
        {
            u'basic_fields': [
                u'names',
                u'birthday',
            ],
        },
        {
            u'other_fields': [
                u'registration_date',
                u'registration_country',
                u'registration_city',
                u'phone_numbers',
                u'emails',
                u'password',
                u'answer',
                u'email_blacklist',
                u'email_collectors',
                u'email_whitelist',
                u'outbound_emails',
                u'email_folders',
                u'delivery_addresses',
                u'social_accounts',
            ],
        },
    ],
    u'data': {
        u'social_accounts': {
            u'errors': {u'api_status': True},
            u'incoming': [],
            u'trusted': [],
            u'factors_summary': u'',
            u'factors': {},
        },
        u'birthday': {
            u'errors': {u'historydb_api_events_status': True},
            u'incoming': [u'1987-11-11'],
            u'trusted': {u'account': [u'1987-11-11'], u'history': [u'1987-11-11']},
            u'factors_summary': u'match',
            u'factors': {u'account': u'match', u'history': u'match'},
        },
        u'email_blacklist': {
            u'errors': {u'oauth_api_status': True, u'api_status': False},
            u'incoming': [],
            u'trusted': [],
            u'factors_summary': u'no_match',
            u'factors': u'no_match',
        },
        u'email_collectors': {
            u'errors': {u'oauth_api_status': True, u'api_status': False},
            u'incoming': [],
            u'trusted': [],
            u'factors_summary': u'no_match',
            u'factors': u'no_match',
        },
        u'registration_date': {
            u'errors': {},
            u'incoming': [u'2001-09-03 msd+0400'],
            u'trusted': [u'2014-10-21 15:41:59 MSK+0400'],
            u'factors_summary': u'no_match',
            u'factors': u'no_match',
        },
        u'registration_city': {
            u'errors': {},
            u'incoming': [u'u041cu043eu0441u043au0432u0430 (213)'],
            u'trusted': [u'u041cu043eu0441u043au0432u0430 (213)'],
            u'factors_summary': u'match',
            u'factors': u'match',
        },
        u'outbound_emails': {
            u'errors': {u'oauth_api_status': True, u'api_status': True},
            u'incoming': [],
            u'trusted': [],
            u'factors_summary': u'no_match',
            u'factors': u'no_match',
        },
        u'delivery_addresses': {
            u'errors': {},
            u'incoming': [],
            u'trusted': [],
            u'factors_summary': u'no_match',
            u'factors': u'no_match',
        },
        u'registration_country': {
            u'errors': {},
            u'incoming': [u'u0420u043eu0441u0456u044f (225)'],
            u'trusted': [u'u0420u043eu0441u0441u0438u044f (225)'],
            u'factors_summary': u'match',
            u'factors': u'match',
        },
        u'email_folders': {
            u'errors': {u'oauth_api_status': True, u'api_status': False},
            u'incoming': [],
            u'trusted': [],
            u'factors_summary': u'no_match',
            u'factors': u'no_match',
        },
        u'answer': {
            u'errors': {},
            u'incoming': None,
            u'trusted': [],
            u'factors_summary': u'no_match',
            u'factors': u'no_match',
        },
        u'email_whitelist': {
            u'errors': {u'oauth_api_status': True, u'api_status': False},
            u'incoming': [],
            u'trusted': [],
            u'factors_summary': u'no_match',
            u'factors': u'no_match',
        },
        u'phone_numbers': {
            u'errors': {},
            u'incoming': [],
            u'trusted': [u'79264607453'],
            u'factors_summary': u'no_match',
            u'factors': u'no_match',
        },
        u'password': {
            u'errors': {u'api_status': True},
            u'incoming': None,
            u'trusted': None,
            u'factors_summary': u'no_match',
            u'factors': {u'auth_date': u'not_calculated', u'auth_found': u'not_calculated'},
        },
        u'emails': {
            u'errors': {},
            u'incoming': [],
            u'trusted': [],
            u'factors_summary': u'no_match',
            u'factors': u'no_match',
        },
        u'names': {
            u'errors': {u'historydb_api_events_status': True},
            u'incoming': [u'test test'],
            u'trusted': {u'account': [u'test test'], u'history': [u'test test']},
            u'factors_summary': u'match',
            u'factors': {u'account': u'match', u'history': u'match'},
        },
    },
    u'extra_info': {
        u'request_source': u'changepass',
        u'version': 2,
        u'is_current_version': False,
        u'restore_status': u'pending',
        u'is_for_learning': False,
    },
}


TEST_FACTORS_DATA_VERSION_MULTISTEP_3 = {
    u'version': u'multistep.3',
    u'restore_status': u'pending',
    u'is_for_learning': False,
    u'request_info': {
        u'contact_email': u'ivan-normal@yandex.ru',
        u'contact_reason': u'dsalkdsadsalk',
        u'language': u'ru',
        u'last_step': u'final_info',
        u'request_source': u'changepass',
        u'user_enabled': False,
    },
    u'historydb_api_events_status': True,
    u'answer': {
        u'entered': {
            u'answer': u'answerr',
            u'question': u'99:question',
        },
        u'factor': {
            u'best': 2,
            u'current': 2,
        },
        u'history': [
            {
                u'answers': [
                    {
                        u'intervals': [
                            {
                                u'end': {u'timestamp': 1425565652.685456, u'user_ip': u'37.9.101.188'},
                                u'start': {u'timestamp': 1425565624.911279, u'user_ip': u'37.9.101.188'},
                            },
                        ],
                        u'value': u'answer',
                    },
                    {
                        u'intervals': [
                            {
                                u'end': None,
                                u'start': {u'timestamp': 1425566871.750641, u'user_ip': u'37.9.101.188'},
                            },
                        ],
                        u'value': u'answerr',
                    },
                ],
                u'question': u'99:question',
            },
            {
                u'answers': [
                    {
                        u'intervals': [
                            {
                                u'end': {u'timestamp': 1425566871.750641, u'user_ip': u'37.9.101.188'},
                                u'start': {u'timestamp': 1425565652.685456, u'user_ip': u'37.9.101.188'},
                            },
                        ],
                        u'value': u'answer',
                    },
                ],
                u'question': u'12:Фамилия вашего любимого музыканта',
            },
        ],
        u'indices': {u'best': [0, 1]},
    },
    u'auths_successful_envs_api_status': True,
    u'birthday': {
        u'account': [
            {
                u'interval': {
                    u'end': {u'timestamp': 1396886905.815272, u'user_ip': u'37.9.101.188'},
                    u'start': {u'timestamp': 1396886815.616372, u'user_ip': u'37.9.101.188'},
                },
                u'value': u'1988-04-21',
            },
            {
                u'interval': {
                    u'end': {u'timestamp': 1396887135.94596, u'user_ip': u'37.9.101.188'},
                    u'start': {u'timestamp': 1396886905.815272, u'user_ip': u'37.9.101.188'},
                },
                u'value': u'1988-04-23',
            },
            {
                u'interval': {
                    u'end': {u'timestamp': 1405078459.189554, u'user_ip': u'37.9.101.188'},
                    u'start': {u'timestamp': 1396887135.94596, u'user_ip': u'37.9.101.188'},
                },
                u'value': u'1988-04-22',
            },
            {
                u'interval': {
                    u'end': None,
                    u'start': {u'timestamp': 1408019396.217614, u'user_ip': u'37.9.101.188'},
                },
                u'value': u'1988-04-21',
            },
        ],
        u'entered': u'1988-04-21',
        u'factor': {
            u'current': 1,
            u'intermediate': 1,
            u'registration': -1,
        },
        u'indices': {
            u'current': 3,
            u'intermediate': 0,
            u'registration': None,
        },
    },
    u'delivery_addresses': {
        u'account': [
            {
                u'building': u'moscow', u'cargolift': u'', u'city': u'moscow`', u'comment': u'',
                u'country': u'Россия', u'email': u'', u'entrance': u'',
                u'fathersname': u'', u'firstname': u'', u'flat': u'', u'floor': u'', u'intercom': u'',
                u'lastname': u'', u'metro': u'', u'phone': u'', u'phone_extra': u'', u'street': u'moscow',
                u'suite': u'', u'zip': u'',
            },
            {
                u'building': u'dsadsa', u'cargolift': u'', u'city': u'moscow', u'comment': u'',
                u'country': u'Россия', u'email': u'', u'entrance': u'',
                u'fathersname': u'', u'firstname': u'', u'flat': u'', u'floor': u'', u'intercom': u'',
                u'lastname': u'', u'metro': u'', u'phone': u'', u'phone_extra': u'', u'street': u'dsadsa',
                u'suite': u'', u'zip': u'',
            },
        ],
        u'entered': [{u'building': u'10', u'city': u'moscow', u'country': u'russia', u'street': u'le'}],
        u'factor': [
            [u'entered_count', 1],
            [u'account_count', 2],
            [u'matches_count', 0],
            [u'absence', 0],
        ],
        u'matches': [],
    },
    u'email_blacklist': {
        u'actual': [],
        u'api_status': False,
        u'entered': [u'black@black.ru'],
        u'factor': [
            [u'entered_count', 1],
            [u'actual_count', 0],
            [u'matches_count', 0],
            [u'absence', 0],
        ],
        u'matches': [],
    },
    u'email_collectors': {
        u'actual': [],
        u'api_status': False,
        u'entered': [u'zzz@фыфв.фыфв'],
        u'factor': [
            [u'entered_count', 1],
            [u'actual_count', 0],
            [u'matches_count', 0],
            [u'absence', 0],
        ],
        u'matches': [],
    },
    u'email_folders': {
        u'actual': [u'папка пка', u'папка 1'],
        u'api_status': True,
        u'entered': [u'omg', u'olol'],
        u'factor': [
            [u'entered_count', 2],
            [u'actual_count', 2],
            [u'matches_count', 0],
            [u'absence', 0],
        ],
        u'matches': [],
    },
    u'email_whitelist': {
        u'actual': [],
        u'api_status': False,
        u'entered': [u'white@white.ru'],
        u'factor': [
            [u'entered_count', 1],
            [u'actual_count', 0],
            [u'matches_count', 0],
            [u'absence', 0],
        ],
        u'matches': [],
    },
    u'emails': {
        u'entered': [u'em@em.ru'],
        u'factor': {
            u'entered_count': 1,
            u'history_count': 2,
            u'matches_count': 0,
        },
        u'history': [
            {
                u'intervals': [
                    {
                        u'end': {u'timestamp': 1425562468.009999, u'user_ip': None},
                        u'start': {u'timestamp': 1425562388.052999, u'user_ip': None},
                    },
                    {
                        u'end': None,
                        u'start': {u'timestamp': 1425562523.801, u'user_ip': None},
                    },
                ],
                u'value': u'a.o.kudryavtsev@gmail.com',
            },
            {
                u'intervals': [
                    {
                        u'end': None,
                        u'start': {u'timestamp': 1425562599.753, u'user_ip': None},
                    },
                ],
                u'value': u'ivan-normal@mail.ru',
            },
        ],
        u'match_indices': [],
        u'matches': [],
    },
    u'names': {
        u'account': [
            {
                u'firstname': u'Ivan',
                u'interval': {
                    u'end': {u'timestamp': 1425559143.221163, u'user_ip': u'37.9.101.188'},
                    u'start': {u'timestamp': 1396886745.699594, u'user_ip': u'37.9.101.188'},
                },
                u'lastname': u'Ivanov',
            },
            {
                u'firstname': u'\u0412\u0430\u0441\u0438\u043b\u0438\u0439',
                u'interval': {
                    u'end': {u'timestamp': 1425559439.142621, u'user_ip': u'37.9.101.188'},
                    u'start': {u'timestamp': 1425559143.221163, u'user_ip': u'37.9.101.188'},
                },
                u'lastname': u'Ivanov',
            },
            {
                u'firstname': u'\u041e\u043b\u043e\u043b\u043e\u0448',
                u'interval': {
                    u'end': {u'timestamp': 1425559507.877384, u'user_ip': u'37.9.101.188'},
                    u'start': {u'timestamp': 1425559439.142621, u'user_ip': u'37.9.101.188'},
                },
                u'lastname': u'\u041e\u043b\u043e\u043b\u043e\u0448\u0435\u0432\u0438\u0447',
            },
            {
                u'firstname': u'ivan',
                u'interval': {
                    u'end': None,
                    u'start': {u'timestamp': 1425559507.877384, u'user_ip': u'37.9.101.188'},
                },
                u'lastname': u'ivanonv',
            },
        ],
        u'entered': {
            u'firstnames': [u'ivan', u'иванн'],
            u'lastnames': [u'ivanonv', u'иваноф'],
        },
        u'factor': {
            u'current': 2,
            u'intermediate': 1,
            u'registration': -1,
        },
        u'indices': {
            u'current': [0, 3],
            u'intermediate': [0, 0],
            u'registration': None,
        },
    },
    u'oauth_api_status': True,
    u'outbound_emails': {
        u'actual': [u'vasia@pupkin.ru'],
        u'api_status': True,
        u'entered': [u'a@b.c'],
        u'factor': [
            [u'entered_count', 1],
            [u'actual_count', 1],
            [u'matches_count', 0],
            [u'absence', 0],
        ],
        u'matches': [],
    },
    u'passwords': {
        u'api_statuses': [True, True, True],
        u'auth_date_entered': u'2014-12-12 EST-0500',
        u'factor': {
            u'auth_date': [0.4564794215795328, 1.0, -1],
            u'auth_found': [1, 1, 0],
            u'entered_count': 3,
        },
        u'indices': [2, 2, None],
        u'intervals': [
            [
                {
                    u'end': {u'timestamp': 1408711178.295746, u'user_ip': None},
                    u'start': {u'timestamp': 1396886745.699594, u'user_ip': None},
                },
                {
                    u'end': {u'timestamp': 1410866243.777811, u'user_ip': None},
                    u'start': {u'timestamp': 1408711252.96859, u'user_ip': None},
                },
                {
                    u'end': {u'timestamp': 1411635065.595066, u'user_ip': None},
                    u'start': {u'timestamp': 1410866281.81494, u'user_ip': None},
                },
                {
                    u'end': None,
                    u'start': {u'timestamp': 1422381737.819005, u'user_ip': None},
                },
            ],
            [
                {
                    u'end': {u'timestamp': 1408711252.96859, u'user_ip': None},
                    u'start': {u'timestamp': 1408711178.295746, u'user_ip': None},
                },
                {
                    u'end': {u'timestamp': 1410866281.81494, u'user_ip': None},
                    u'start': {u'timestamp': 1410866243.777811, u'user_ip': None},
                },
                {
                    u'end': {u'timestamp': 1422381737.819005, u'user_ip': None},
                    u'start': {u'timestamp': 1411635065.595066, u'user_ip': None},
                },
            ],
            [],
        ],
    },
    u'phone_numbers': {
        u'entered': [u'12345'],
        u'factor': {
            u'entered_count': 1,
            u'history_count': 1,
            u'matches_count': 0,
        },
        u'history': [
            {
                u'intervals': [
                    {
                        u'end': {u'timestamp': 1408711221.535799, u'user_ip': u'37.9.101.188'},
                        u'start': {u'timestamp': 1408711178.229276, u'user_ip': u'87.250.235.20'},
                    },
                    {
                        u'end': {u'timestamp': 1409906010.814816, u'user_ip': u'37.9.101.188'},
                        u'start': {u'timestamp': 1409905847.890153, u'user_ip': u'37.9.101.188'},
                    },
                    {
                        u'end': None,
                        u'start': {u'timestamp': 1417539384.749069, u'user_ip': u'37.9.101.188'},
                    },
                ],
                u'value': u'79151711300',
            },
        ],
        u'match_indices': [],
        u'matches': [],
    },
    u'registration_city': {
        u'entered': u'moscow',
        u'entered_id': 1,
        u'factor': [
            [u'initial_equal', 0],
            [u'symbol_shrink', 1.0],
            [u'distance', 1.0],
            [u'xlit_used', -1],
        ],
        u'factor_id': 0,
        u'history': u'Москва',
        u'history_id': 213,
    },
    u'registration_country': {
        u'entered': u'russia',
        u'entered_id': 100500,
        u'factor': [
            [u'initial_equal', 0],
            [u'symbol_shrink', 1.0],
            [u'distance', 1.0],
            [u'xlit_used', -1],
        ],
        u'factor_id': 0,
        u'history': u'Россия',
        u'history_id': 225,
    },
    u'registration_date': {
        u'account': u'2014-04-07 20:05:45',
        u'entered': u'2000-01-01 EST-0500',
        u'factor': 0.0,
    },
    u'registration_ip': u'37.9.101.188',
    u'services': {
        u'account': [u'mail'],
        u'entered': [u'mail'],
        u'factor': [
            [u'entered_count', 1],
            [u'account_count', 1],
            [u'matches_count', 1],
        ],
        u'matches': [u'mail'],
    },
    u'social_accounts': {
        u'account_profiles': [
            {
                u'addresses': [u'https://plus.google.com/118320684667584130204'],
                u'allow_auth': False,
                u'person': {
                    u'birthday': None,
                    u'email': u'a.o.kudryavtsev@gmail.com',
                    u'firstname': u'Alexander',
                    u'gender': u'm',
                    u'lastname': u'Kudryavtsev',
                    u'nickname': u'',
                    u'profile_id': 101796,
                },
                u'profile_id': 101796,
                u'provider': u'google',
                u'uid': 3000453634,
                u'userid': u'118320684667584130204',
                u'username': u'a.o.kudryavtsev',
            },
        ],
        u'api_status': False,
        u'entered_profiles': [],
        u'factor': {
            u'account_profiles_count': 1,
            u'entered_accounts_count': 1,
            u'entered_profiles_count': 0,
            u'matches_count': 0,
        },
    },
    u'user_env': {
        u'actual': {u'browser.name': None, u'os.name': None, u'yandexuid': None},
        u'factor': 0,
        u'history': [
            {u'browser.name': u'Firefox', u'os.name': u'Ubuntu', u'yandexuid': u'1046714081386936400'},
        ],
    },
    u'user_ip': {
        u'actual': u'8.8.8.8',
        u'auths_contain_ip_api_status': True,
        u'factor': 0,
    },
    u'user_ip_subnet': {
        u'actual': None,
        u'actual_as_list': [],
        u'factor': -1,
        u'history_ips': [u'37.9.101.188', u'5.255.233.113'],
    },
}


TEST_FACTORS_OUTPUT_VERSION_MULTISTEP_3 = {
    u'action': u'restore_semi_auto_request',
    u'extra_info': {
        u'is_for_learning': False,
        u'request_source': u'changepass',
        u'restore_status': u'pending',
        u'version': u'multistep.3',
        u'is_current_version': False,
        u'contact_email': u'ivan-normal@yandex.ru',
    },
    u'data': {
        u'answer': {
            u'changes_info': {},
            u'errors': {},
            u'factors': {
                u'best': u'match',
                u'current': u'match',
            },
            u'factors_summary': u'match',
            u'incoming': [
                {
                    u'answer': u'answerr',
                    u'question': u'99:question',
                },
            ],
            u'indices': {
                u'best': 1,
            },
            u'trusted': [
                u'answer',
                u'answerr',
            ],
            u'trusted_intervals': [
                [
                    {
                        u'end': {
                            u'datetime': u'2015-03-05 17:27:32 MSK+0300',
                            u'user_ip': u'37.9.101.188',
                        },
                        u'start': {
                            u'datetime': u'2015-03-05 17:27:04 MSK+0300',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
                [
                    {
                        u'end': None,
                        u'start': {
                            u'datetime': u'2015-03-05 17:47:51 MSK+0300',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
            ],
        },
        u'birthday': {
            u'errors': {
                u'historydb_api_events_status': True,
            },
            u'factors': {
                u'current': u'match',
                u'intermediate': u'match',
                u'registration': u'not_calculated',
            },
            u'factors_summary': u'match',
            u'incoming': [
                u'1988-04-21',
            ],
            u'indices': {
                u'current': 3,
                u'intermediate': 0,
                u'registration': None,
            },
            u'trusted': [
                u'1988-04-21',
                u'1988-04-23',
                u'1988-04-22',
                u'1988-04-21',
            ],
            u'trusted_intervals': [
                [
                    {
                        u'end': {
                            u'datetime': u'2014-04-07 20:08:25 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                        u'start': {
                            u'datetime': u'2014-04-07 20:06:55 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
                [
                    {
                        u'end': {
                            u'datetime': u'2014-04-07 20:12:15 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                        u'start': {
                            u'datetime': u'2014-04-07 20:08:25 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
                [
                    {
                        u'end': {
                            u'datetime': u'2014-07-11 15:34:19 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                        u'start': {
                            u'datetime': u'2014-04-07 20:12:15 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
                [
                    {
                        u'end': None,
                        u'start': {
                            u'datetime': u'2014-08-14 16:29:56 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
            ],
        },
        u'delivery_addresses': {
            u'errors': {},
            u'factors': u'no_match',
            u'factors_summary': u'no_match',
            u'incoming': [
                {
                    u'building': u'10',
                    u'city': u'moscow',
                    u'country': u'russia',
                    u'street': u'le',
                },
            ],
            u'trusted': [
                {
                    u'building': u'moscow',
                    u'city': u'moscow`',
                    u'country': u'Россия',
                    u'street': u'moscow',
                    u'suite': u'',
                },
                {
                    u'building': u'dsadsa',
                    u'city': u'moscow',
                    u'country': u'Россия',
                    u'street': u'dsadsa',
                    u'suite': u'',
                },
            ],
        },
        u'email_blacklist': {
            u'errors': {
                u'api_status': False,
                u'oauth_api_status': True,
            },
            u'factors': u'no_match',
            u'factors_summary': u'no_match',
            u'incoming': [
                u'black@black.ru'
            ],
            u'trusted': [],
        },
        u'email_collectors': {
            u'errors': {
                u'api_status': False,
                u'oauth_api_status': True,
            },
            u'factors': u'no_match',
            u'factors_summary': u'no_match',
            u'incoming': [
                u'zzz@фыфв.фыфв',
            ],
            u'trusted': [],
        },
        u'email_folders': {
            u'errors': {
                u'api_status': True,
                u'oauth_api_status': True,
            },
            u'factors': u'no_match',
            u'factors_summary': u'no_match',
            u'incoming': [
                u'omg',
                u'olol',
            ],
            u'trusted': [
                u'папка пка',
                u'папка 1',
            ],
        },
        u'email_whitelist': {
            u'errors': {
                u'api_status': False,
                u'oauth_api_status': True,
            },
            u'factors': u'no_match',
            u'factors_summary': u'no_match',
            u'incoming': [
                u'white@white.ru',
            ],
            u'trusted': [],
        },
        u'emails': {
            u'errors': {},
            u'factors': u'no_match',
            u'factors_summary': u'no_match',
            u'incoming': [
                u'em@em.ru',
            ],
            u'indices': [],
            u'trusted': [
                u'a.o.kudryavtsev@gmail.com',
                u'ivan-normal@mail.ru',
            ],
            u'trusted_intervals': [
                [
                    {
                        u'end': {
                            u'datetime': u'2015-03-05 16:34:28 MSK+0300',
                            u'user_ip': None,
                        },
                        u'start': {
                            u'datetime': u'2015-03-05 16:33:08 MSK+0300',
                            u'user_ip': None,
                        },
                    },
                    {
                        u'end': None,
                        u'start': {
                            u'datetime': u'2015-03-05 16:35:23 MSK+0300',
                            u'user_ip': None,
                        },
                    },
                ],
                [
                    {
                        u'end': None,
                        u'start': {
                            u'datetime': u'2015-03-05 16:36:39 MSK+0300',
                            u'user_ip': None,
                        },
                    },
                ],
            ],
        },
        u'names': {
            u'errors': {
                u'historydb_api_events_status': True,
            },
            u'factors': {
                u'current': u'match',
                u'intermediate': u'inexact_match',
                u'registration': u'not_calculated',
            },
            u'factors_summary': u'match',
            u'incoming': [
                u'ivan ivanonv',
                u'иванн иваноф',
            ],
            u'indices': {
                u'current': [
                    0,
                    3,
                ],
                u'intermediate': [
                    0,
                    0,
                ],
                u'registration': None,
            },
            u'trusted': [
                u'Ivan Ivanov',
                u'Василий Ivanov',
                u'Ололош Ололошевич',
                u'ivan ivanonv',
            ],
            u'trusted_intervals': [
                [
                    {
                        u'end': {
                            u'datetime': u'2015-03-05 15:39:03 MSK+0300',
                            u'user_ip': u'37.9.101.188',
                        },
                        u'start': {
                            u'datetime': u'2014-04-07 20:05:45 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
                [
                    {
                        u'end': {
                            u'datetime': u'2015-03-05 15:43:59 MSK+0300',
                            u'user_ip': u'37.9.101.188',
                        },
                        u'start': {
                            u'datetime': u'2015-03-05 15:39:03 MSK+0300',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
                [
                    {
                        u'end': {
                            u'datetime': u'2015-03-05 15:45:07 MSK+0300',
                            u'user_ip': u'37.9.101.188',
                        },
                        u'start': {
                            u'datetime': u'2015-03-05 15:43:59 MSK+0300',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
                [
                    {
                        u'end': None,
                        u'start': {
                            u'datetime': u'2015-03-05 15:45:07 MSK+0300',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
            ],
        },
        u'outbound_emails': {
            u'errors': {
                u'api_status': True,
                u'oauth_api_status': True,
            },
            u'factors': u'no_match',
            u'factors_summary': u'no_match',
            u'incoming': [
                u'a@b.c',
            ],
            u'trusted': [
                u'vasia@pupkin.ru',
            ],
        },
        u'passwords': {
            u'errors': {
                u'api_statuses': True,
            },
            u'factors': {
                u'auth_date_0': u'no_match',
                u'auth_date_1': u'match',
                u'auth_date_2': u'not_calculated',
                u'auth_found_0': u'match',
                u'auth_found_1': u'match',
                u'auth_found_2': u'no_match',
            },
            u'factors_summary': u'match',
            u'incoming': [
                {
                    u'auth_date': u'2014-12-12 EST-0500',
                    u'passwords_count': 3
                },
            ],
            u'trusted': [],
            u'trusted_intervals': [
                [
                    {
                        u'end': {
                            u'datetime': u'2014-08-22 16:39:38 MSK+0400',
                            u'user_ip': None,
                        },
                        u'start': {
                            u'datetime': u'2014-04-07 20:05:45 MSK+0400',
                            u'user_ip': None,
                        },
                    },
                    {
                        u'end': {
                            u'datetime': u'2014-09-16 15:17:23 MSK+0400',
                            u'user_ip': None,
                        },
                        u'start': {
                            u'datetime': u'2014-08-22 16:40:52 MSK+0400',
                            u'user_ip': None,
                        },
                    },
                    {
                        u'end': {
                            u'datetime': u'2014-09-25 12:51:05 MSK+0400',
                            u'user_ip': None,
                        },
                        u'start': {
                            u'datetime': u'2014-09-16 15:18:01 MSK+0400',
                            u'user_ip': None,
                        },
                    },
                    {
                        u'end': None,
                        u'start': {
                            u'datetime': u'2015-01-27 21:02:17 MSK+0300',
                            u'user_ip': None,
                        },
                    },
                ],
                [
                    {
                        u'end': {
                            u'datetime': u'2014-08-22 16:40:52 MSK+0400',
                            u'user_ip': None,
                        },
                        u'start': {
                            u'datetime': u'2014-08-22 16:39:38 MSK+0400',
                            u'user_ip': None,
                        },
                    },
                    {
                        u'end': {
                            u'datetime': u'2014-09-16 15:18:01 MSK+0400',
                            u'user_ip': None,
                        },
                        u'start': {
                            u'datetime': u'2014-09-16 15:17:23 MSK+0400',
                            u'user_ip': None,
                        },
                    },
                    {
                        u'end': {
                            u'datetime': u'2015-01-27 21:02:17 MSK+0300',
                            u'user_ip': None,
                        },
                        u'start': {
                            u'datetime': u'2014-09-25 12:51:05 MSK+0400',
                            u'user_ip': None,
                        },
                    },
                ],
                [],
            ],
        },
        u'phone_numbers': {
            u'changes_info': {},
            u'errors': {},
            u'factors': u'no_match',
            u'factors_summary': u'no_match',
            u'incoming': [
                u'12345',
            ],
            u'indices': [],
            u'trusted': [
                u'79151711300',
            ],
            u'trusted_intervals': [
                [
                    {
                        u'end': {
                            u'datetime': u'2014-08-22 16:40:21 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                        u'start': {
                            u'datetime': u'2014-08-22 16:39:38 MSK+0400',
                            u'user_ip': u'87.250.235.20',
                        },
                    },
                    {
                        u'end': {
                            u'datetime': u'2014-09-05 12:33:30 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                        u'start': {
                            u'datetime': u'2014-09-05 12:30:47 MSK+0400',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                    {
                        u'end': None,
                        u'start': {
                            u'datetime': u'2014-12-02 19:56:24 MSK+0300',
                            u'user_ip': u'37.9.101.188',
                        },
                    },
                ],
            ],
        },
        u'registration_city': {
            u'errors': {},
            u'factors': u'match',
            u'factors_summary': u'match',
            u'incoming': [
                u'moscow (1)',
            ],
            u'trusted': [
                u'Москва (213)',
            ],
        },
        u'registration_country': {
            u'errors': {},
            u'factors': u'match',
            u'factors_summary': u'match',
            u'incoming': [
                u'russia (100500)',
            ],
            u'trusted': [
                u'Россия (225)',
            ],
        },
        u'registration_date': {
            u'errors': {},
            u'factors': u'no_match',
            u'factors_summary': u'no_match',
            u'incoming': [
                u'2000-01-01 EST-0500',
            ],
            u'trusted': [
                u'2014-04-07 20:05:45 MSK+0400',
            ],
        },
        u'services': {
            u'errors': {},
            u'factors': u'match',
            u'factors_summary': u'match',
            u'incoming': [
                u'mail',
            ],
            u'trusted': [
                u'mail',
            ],
        },
        u'social_accounts': {
            u'errors': {
                u'api_status': False,
            },
            u'factors': u'no_match',
            u'factors_summary': u'no_match',
            u'incoming': [],
            u'trusted': [
                {
                    u'belongs_to_account': True,
                    u'is_matched': False,
                    u'addresses': [
                        u'https://plus.google.com/118320684667584130204',
                    ],
                    u'birthday': None,
                    u'firstname': u'Alexander',
                    u'lastname': u'Kudryavtsev',
                },
            ],
        },
    },
    u'groups': [
        {
            u'basic_fields': [
                u'names',
                u'birthday',
            ],
        },
        {
            u'other_fields': [
                u'passwords',
                u'phone_numbers',
                u'emails',
                u'answer',
                u'registration_date',
                u'registration_country',
                u'registration_city',
                u'social_accounts',
                u'services',
                u'delivery_addresses',
                u'email_folders',
                u'email_blacklist',
                u'email_whitelist',
                u'email_collectors',
                u'outbound_emails',
            ],
        },
    ],
    u'ip_info': {
        u'different_ips_count': u'-',
        u'errors': {
            u'auths_contain_ip_api_status': True,
            u'auths_ip_statistics_api_status': None,
            u'auths_successful_envs_api_status': True,
        },
        u'factors': {
            u'user_ip_eq_registration_ip': u'no_match',
            u'user_ip_in_history': u'no_match',
            u'user_subnet_in_history': u'not_calculated',
            u'user_ua_in_history': u'no_match',
        },
        u'max_auths_ip': u'-',
        u'max_auths_ip_auths_count': u'-',
        u'registration_ip': u'37.9.101.188',
        u'total_auths_count': u'-',
        u'user_ip': u'8.8.8.8',
        u'user_ip_auths_count': u'-',
        u'user_ip_auths_percent': u'-',
        u'user_ip_first_auth_datetime': None,
        u'user_ip_last_auth_datetime': None,
    },
    u'restore_id': TEST_RESTORE_ID,
    u'support_decision': None,
    u'datetime': u'1970-01-01 03:20:34',
}


TEST_FACTORS_DATA_VERSION_MULTISTEP_4 = {
    # Общая информация об анкете
    'is_for_learning': False,  # Признак того, что анкета используется для обучения
    'restore_status': 'pending',
    'request_info': {
        'language': 'ru',
        'last_step': 'final_info',
        'contact_email': u'vasia@пупкин.рф',
        'contact_reason': u'Забыл пароль',
        'request_source': 'restore',
        'is_unconditional_pass': False,  # Признак безусловной проверки
        'user_enabled': True,  # Признак требования заблокированности
    },
    'version': 'multistep.4',  # Версия анкеты

    # Признаки успешности выполнения вызовов API
    'auths_aggregated_runtime_api_status': True,
    'historydb_api_events_status': True,
    'oauth_api_status': True,

    # Шаг 1
    'names': {
        'account': [
            {
                'firstname': u'Петр',
                'lastname': u'Петров',
                'interval': {
                    'end': {
                        'timestamp': 2,
                        'user_ip': '5.45.207.1',
                        'yandexuid': '123',
                    },
                    'start': {
                        'timestamp': 1,
                        'user_ip': '5.45.207.254',
                        'yandexuid': '123',
                    },
                },
            },
            {
                'firstname': u'Петр',
                'lastname': 'Petroff',
                'interval': {
                    'end': None,
                    'start': {
                        'timestamp': 2,
                        'user_ip': '5.45.207.1',
                        'yandexuid': '123',
                    },
                },
            },
        ],
        'indices': {
            'current': (
                1,
                1,
            ),
            'registration': (
                1,
                0,
            ),
            'intermediate': None,
        },
        'entered': {
            'lastnames': [  # Варианты фамилии
                'B',
                'P',
            ],
            'firstnames': [  # Варианты имени
                'A',
            ],
        },
        'factor': {
            'current': 0,  # Совпадение с текущими ФИ
            'intermediate': -1,  # Лучшее совпадение с промежуточными ФИ
            'registration': 0,  # Совпадение с регистрационными ФИ
            'change_count': 1,  # Число смен ФИ в истории (первичное задание не считается)
            'change_depth': [  # Глубина для первой и двух последних смен
                1.0,
                -1,
                1.0,
            ],
            'change_ip_eq_reg': [  # Совпадение IP смен с IP регистрации
                0,
                -1,
                0,
            ],
            'change_subnet_eq_reg': [  # Совпадение subnet смен с subnet регистрации
                1,
                -1,
                1,
            ],
            'change_ua_eq_reg': [  # Совпадение UA смен с UA регистрации
                1,
                -1,
                1,
            ],
            'change_ip_eq_user': [  # Совпадение IP смен с IP пользователя
                0,
                -1,
                0,
            ],
            'change_subnet_eq_user': [  # Совпадение subnet смен с subnet пользователя
                1,
                -1,
                1,
            ],
            'change_ua_eq_user': [  # Совпадение UA смен с UA пользователя
                0,
                -1,
                0,
            ],
        },
    },
    'birthday': {
        'account': [
            {
                'value': '2011-11-11',
                'interval': {
                    'end': {
                        'timestamp': None,
                    },
                    'start': {
                        'timestamp': 1,
                        'user_ip': '5.45.207.254',
                        'yandexuid': '123',
                    },
                },
            },
            {
                'value': '2000-10-01',
                'interval': {
                    'end': None,
                    'start': {
                        'timestamp': None,
                    },
                },
            },
        ],
        'indices': {
            'current': 1,
            'registration': 0,
            'intermediate': None,
        },
        'entered': '2012-01-01',
        'factor': {  # Описание факторов аналогично факторам names
            'intermediate': -1,
            'registration': 0,
            'current': 0,
            'change_count': 1,
            'change_depth': [
                -1,
                -1,
                -1,
            ],
            'change_ip_eq_user': [
                -1,
                -1,
                -1,
            ],
            'change_subnet_eq_user': [
                -1,
                -1,
                -1,
            ],
            'change_ua_eq_user': [
                0,
                -1,
                0,
            ],
            'change_ip_eq_reg': [
                -1,
                -1,
                -1,
            ],
            'change_subnet_eq_reg': [
                -1,
                -1,
                -1,
            ],
            'change_ua_eq_reg': [
                0,
                -1,
                0,
            ],
        },
    },
    'passwords': {
        'actual': {
            'last_change_request': {  # Информация о последнем принуждении к смене пароля
                'admin': 'alexco',
                'comment': 'broken',
                'change_required': True,  # Признак, было ли принуждение выставлено или снято
                'origin_info': {
                    'timestamp': 1,
                    'user_ip': '5.45.207.254',
                    'yandexuid': '123',
                },
            },
            'last_change': {  # Информация о последней смене пароля, выполненной пользователем
                'origin_info': {
                    'user_ip': '5.45.207.254',
                    'timestamp': 1000,
                    'yandexuid': 'yandexuid',
                },
                'change_type': 'forced',  # Тип смены; другие значения - voluntary, restore
            },
            'last_change_ip_first_auth': {  # Информация о первой авторизации с IP последней смены
                'timestamp': 500,
                'status': 'successful',
                'authtype': 'imap',
            },
            'last_change_subnet_first_auth': {  # Информация о первой авторизации с subnet последней смены
                'timestamp': 10,
                'status': 'successful',
                'authtype': 'imap',
            },
            'last_change_ua_first_auth': {  # Информация о первой авторизации с UA последней смены
                'timestamp': 10,
                'status': 'successful',
                'authtype': 'imap',
            },
        },
        'auth_date_entered': '2010-10-10 MSD+0400',  # Формат даты '%Y-%m-%d %Z%z'. Часовой пояс определяется по IP пользователя.
        'api_statuses': [  # Список признаков успешности вызова API поиска паролей в HistoryDB.
            True,
        ],
        'indices': [  # Номера лучших подходящих интервалов актуальности для найденных в истории паролей
            None,
        ],
        'intervals': [  # Список интервалов актуальности для введенных вариантов пароля. Содержит пары Unix timestamp;
                        # если вариант пароля актуален, второе значение в паре None.
            [],
        ],
        'factor': {
            'entered_count': 1,  # Число введенных вариантов пароля
            'auth_found': [  # Список факторов-признаков того, найдена ли авторизация паролем в истории.
                             # Если поиск не выполнялся, значение -1. Всегда 3 элемента.
                0,
                -1,
                -1,
            ],
            'auth_date': [  # Список факторов нечеткого сравнения дат (по одному для каждого варианта пароля), значение от 0.0 до 1.0,
                            # либо -1, если не было сравнения. Всегда 3 элемента.
                -1,
                -1,
                -1,
            ],
            'first_auth_depth': [  # Глубина заведения пароля, если он был найден, для каждого из введенных вариантов
                -1,
                -1,
                -1,
            ],
            'change_count': 0,  # Число смен пароля
            'forced_change_pending': 1,  # Признак того, требуется ли принудительная смена
            'last_change_is_forced_change': -1,  # Признак того, что последняя смена - принудительная
            'last_change_depth': -1,  # Глубина последней смены
            'last_change_ip_first_auth_depth': -1,  # Глубина первой авторизации с IP последней смены
            'last_change_subnet_first_auth_depth': 0.0,  # Глубина первой авторизации с subnet последней смены
            'last_change_ua_first_auth_depth': 0.0,  # Глубина первой авторизации с UA последней смены
            'last_change_ip_eq_user': -1,  # Фактор совпадения IP последней смены с пользовательским
            'last_change_subnet_eq_user': -1,  # Фактор совпадения subnet последней смены с пользовательским
            'last_change_ua_eq_user': -1,  # Фактор совпадения UA последней смены с пользовательским
        },
    },

    # Шаг 2
    'emails': {
        'history': [  # Значения отсортированы в порядке первого появления email в истории
            {
                'value': 'email_2@ya.ru',
                'intervals': [
                    {
                        'end': None,
                        'start': {
                            'timestamp': 1,
                            'user_ip': '5.45.207.254',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
            {
                'value': 'email_3@ya.ru',
                'intervals': [
                    {
                        'end': {
                            'timestamp': 5,
                            'user_ip': '5.45.207.254',
                            'yandexuid': '123',
                        },
                        'start': {
                            'timestamp': 2,
                            'user_ip': '5.45.207.254',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
            {
                'value': u'ва@силий@xn--80atjc.xn--p1ai',
                'intervals': [
                    {
                        'end': None,
                        'start': {
                            'timestamp': 3,
                            'user_ip': '5.45.207.254',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
            {
                'value': u'email_5@.рф',
                'intervals': [
                    {
                        'end': None,
                        'start': {
                            'timestamp': 4,
                            'user_ip': '5.45.207.254',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
        ],
        'matches': [
            'email_3@ya.ru',
            'email_2@ya.ru',
            u'ва@силий@xn--80atjc.xn--p1ai',
            u'email_5@.рф',
        ],
        'entered': [
            'email_2@ya.ru',
            'email_3@ya.ru',
            u'ва@силий@xn--80atjc.xn--p1ai',
            u'email_5@.рф',
        ],
        'factor': {
            'matches_count': 4,
            'history_count': 4,
            'entered_count': 4,
        },
        'match_indices': [
            (
                0,
                1,
            ),
            (
                1,
                0,
            ),
            (
                2,
                2,
            ),
            (
                3,
                3,
            ),
        ],
    },
    'answer': {
        'history': [  # Список КВ/КО из истории - упорядочен по времени появления КВ
            {
                'question': '1:qqq',
                'answers': [  # Список КО для КВ - упорядочен по времени появления КО
                    {
                        'value': u'КО',
                        'intervals': [
                            {
                                'end': {
                                    'timestamp': 3,
                                    'user_ip': '5.45.207.254',
                                    'yandexuid': '123',
                                },
                                'start': {
                                    'timestamp': 2,
                                    'user_ip': '5.45.207.254',
                                    'yandexuid': '123',
                                },
                            },
                        ],
                    },
                ],
            },
            {
                'question': '99:my question',
                'answers': [
                    {
                        'value': u'КО',
                        'intervals': [
                            {
                                'end': {
                                    'timestamp': 4,
                                    'user_ip': '5.45.207.254',
                                    'yandexuid': '123',
                                },
                                'start': {
                                    'timestamp': 3,
                                    'user_ip': '5.45.207.254',
                                    'yandexuid': '123',
                                },
                            },
                        ],
                    },
                    {
                        'value': u'ответ',
                        'intervals': [
                            {
                                'end': {
                                    'timestamp': 6,
                                    'user_ip': '5.45.207.254',
                                    'yandexuid': '123',
                                },
                                'start': {
                                    'timestamp': 4,
                                    'user_ip': '5.45.207.254',
                                    'yandexuid': '123',
                                },
                            },
                        ],
                    },
                    {
                        'value': 'answer',
                        'intervals': [
                            {
                                'end': None,
                                'start': {
                                    'timestamp': 6,
                                    'user_ip': '5.45.207.254',
                                    'yandexuid': '123',
                                },
                            },
                        ],
                    },
                ],
            },
        ],
        'indices': {
            'best': (
                1,
                1,
            ),
        },
        'entered': {
            'question': '99:my question',
            'answer': u'ответ',
        },
        'factor': {
            'current': 0,  # Простой строковый фактор для совпадения с текущими КВ/КО на аккаунте
            'best': 2,  # Простой строковый фактор для лучшего совпадения. Если КО не введен, либо ничего не найдено, значение -1.
            'change_count': 3,  # Число смен в истории
            'change_depth': [  # Фактор глубины времени для последних трех смен
                -1,
                -1,
                -1,
            ],
            'change_ip_eq_user': [  # Признак совпадения IP смен с пользовательским
                1,
                1,
                1,
            ],
            'change_subnet_eq_user': [  # Признак совпадения subnet смен с пользовательским
                1,
                1,
                1,
            ],
            'change_ua_eq_user': [  # Признак совпадения UA смен с пользовательским
                0,
                0,
                0,
            ],

        },
    },
    'phone_numbers': {
        'history': [
            {
                'value': '79117654321',
                'intervals': [
                    {
                        'end': None,
                        'start': {
                            'timestamp': 1,
                            'user_ip': '5.45.207.254',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
            {
                'value': '79111234567',
                'intervals': [
                    {
                        'end': {
                            'timestamp': 3,
                            'user_ip': '5.45.207.254',
                            'yandexuid': '123',
                        },
                        'start': {
                            'timestamp': 2,
                            'user_ip': '5.45.207.254',
                            'yandexuid': '123',
                        },
                    },
                    {
                        'end': None,
                        'start': {
                            'timestamp': 4,
                            'user_ip': '5.45.207.254',
                            'yandexuid': '123',
                        },
                    },
                ],
            },
        ],
        'matches': [
            '79111234567',
        ],
        'entered': [
            '89111234567',
            '79111234567',
            '79111234568',
        ],
        'factor': {
            'matches_count': 1,
            'history_count': 2,
            'entered_count': 3,
            # Факторы смены - аналогично КВ/КО
            'change_count': 2,
            'change_depth': [
                -1,
                1,
                1,
            ],
            'change_ip_eq_user': [
                -1,
                1,
                1,
            ],
            'change_subnet_eq_user': [
                -1,
                1,
                1,
            ],
            'change_ua_eq_user': [
                -1,
                0,
                0,
            ],
        },
        'match_indices': [
            (
                0,
                1,
            ),
        ],
    },

    # Шаг 3
    'registration_date': {
        'account': '2010-10-10 10:20:30',
        'entered': '2010-10-10 MSD+0400',
        'factor': 1,  # Фактор неточного сравнения дат. Значение от 0.0 до 1.0.
    },
    'registration_city': {
        'history_id': 213,
        'history': u'Москва',
        'entered_id': None,
        'entered': None,
        'factor': {
            'text': 0,  # Простой строковый фактор
            'id': 0,  # Признак совпадения ID Геобазы
        },
    },
    'registration_country': {
        'history_id': 225,
        'history': u'Россия',
        'entered_id': None,
        'entered': 'RU',
        'factor': {
            'text': 2,  # Простой строковый фактор
            'id': 0,  # Признак совпадения ID Геобазы
        },
    },
    'registration_ip': '5.45.207.254',

    # Шаг 4
    'social_accounts': {
        'entered_accounts': [  # Информация о введенных в форму соц. аккаунтах (без привязки к Яндексу)
            {
                'provider': {
                    'name': 'google',
                    'id': 5,
                    'code': 'gg',
                },
                'firstname': 'Firstname',
                'userid': '57575757575',
                'avatar': {
                    '0x0': 'https://lh3.googleusercontent.com/-XdUIqdskCWA/AAAAAAAAAAI/AAAAAAAAAAA/2252rscbv5M/photo.jpg',
                },
                'lastname': 'Lastname',
                'username': 'some.user',
                'email': 'some-mail@example.com',
                'links': [
                    'https://plus.google.com/118320684662584130204',
                ],
                'gender': 'm',
            },
        ],
        'entered_profiles': [  # Информация о соответствующих введенным соц. аккаунтам соц. профилям в Яндексе
            {
                'provider': 'facebook',
                'addresses': [
                    'http://www.facebook.com/profile.php?id=%(userid)s',
                    'http://www.facebook.com/some.user',
                ],
                'uid': 1130000000000001,
                'userid': '57575757575',
                'profile_id': 123,
                'allow_auth': True,
                'username': 'some.user',
            },
        ],
        'account_profiles': [],  # Информация о соц. профилях аккаунта, к которому восстанавливаем доступ
        'api_status': True,  # Успешность вызова соц. апи
        'factor': {
            'matches_count': 0,
            'entered_accounts_count': 1,
            'entered_profiles_count': 1,
            'account_profiles_count': 0,
        },
    },
    'services': {
        'matches': [
            'mail',
            'metrika',
            'disk',
        ],
        'account': [
            'mail',
            'metrika',
            'disk',
        ],
        'entered': [
            'mail',
            'metrika',
            'disk',
            'yandsearch',
        ],
        'factor': {
            'matches_count': 4,
            'account_count': 4,
            'entered_count': 5,
        },
    },


    # Шаг 5
    'email_collectors': {
        'actual': [
            'mail1@mail.com',
            'mail2@mail.ru',
        ],
        'matches': [
            'mail1@mail.com',
        ],
        'api_status': 1,
        'entered': [
            'mail2@mail.com',
        ],
        'factor': {
            'matches_count': 1,
            'actual_count': 2,
            'entered_count': 1,
        },
    },
    'email_folders': {
        'actual': [
            u'Папка',
        ],
        'matches': [
            u'Папка',
        ],
        'api_status': True,
        'entered': [
            u'Папка1',
            u'Папка2',
            'Papka',
        ],
        'factor': {
            'matches_count': 1,
            'actual_count': 1,
            'entered_count': 3,
        },
    },
    'email_blacklist': {
        'actual': [
            'vasia@xn--80a1acny.xn--p1ai',
            u'вася@xn--80a1acny.xn--p1ai',
        ],
        'matches': [
            'vasia@xn--80a1acny.xn--p1ai',
        ],
        'api_status': 1,
        'entered': [
            u'вася@почта.рф',
        ],
        'factor': {
            'matches_count': 1,
            'actual_count': 2,
            'entered_count': 1,
        },
    },
    'delivery_addresses': {
        'matches': [
            {
                'firstname': '',
                'street': 'tolstoy',
                'suite': '10c4',
                'floor': '',
                'lastname': '',
                'email': '',
                'fathersname': '',
                'city': u'Иваново',
                'metro': '',
                'intercom': '',
                'phone_extra': '',
                'country': 'rf',
                'cargolift': '',
                'entrance': '',
                'phone': '',
                'zip': '',
                'comment': '',
                'building': '16',
                'flat': '',
            },
        ],
        'account': [
            {
                'firstname': '',
                'street': 'tolstoy',
                'suite': '10c4',
                'floor': '',
                'lastname': '',
                'email': '',
                'fathersname': '',
                'city': u'Иваново',
                'metro': '',
                'intercom': '',
                'phone_extra': '',
                'country': 'rf',
                'cargolift': '',
                'entrance': '',
                'phone': '',
                'zip': '',
                'comment': '',
                'building': '16',
                'flat': '',
            },
        ],
        'entered': [
            {
                'firstname': '',
                'street': 'tolstoy',
                'suite': '10c4',
                'floor': '',
                'lastname': '',
                'email': '',
                'fathersname': '',
                'city': u'Иваново',
                'metro': '',
                'intercom': '',
                'phone_extra': '',
                'country': 'rf',
                'cargolift': '',
                'entrance': '',
                'phone': '',
                'zip': '',
                'comment': '',
                'building': '16',
                'flat': '',
            },
        ],
        'factor': {
            'matches_count': 1,
            'account_count': 1,
            'entered_count': 1,
        },
    },
    'email_whitelist': {
        'actual': [
            'mail1@mail.ru',
            'mail2@mail.ru',
        ],
        'matches': [
            'mail1@mail.ru',
            'mail2@mail.ru',
        ],
        'api_status': 1,
        'entered': [
            'mail1@mail.com',
            'mail1@mail.ru',
        ],
        'factor': {
            'matches_count': 2,
            'actual_count': 2,
            'entered_count': 2,
        },
    },
    'outbound_emails': {
        'actual': [
            'vasia@xn--80a1acny.xn--p1ai',
            u'вася@xn--80a1acny.xn--p1ai',
        ],
        'matches': [
            'vasia@xn--80a1acny.xn--p1ai',
        ],
        'api_status': 1,
        'entered': [
            u'вася@почта.рф',
        ],
        'factor': {
            'matches_count': 1,
            'actual_count': 2,
            'entered_count': 1,
        },
    },
    # Шаг 6
    'user_env_auths': {  # Данные о поиске окружения пользователя в истории авторизаций и не только
        'actual': {
            'gathered_auths_count': 3,  # Сколько авторизаций было вынуто из истории за год
            'ip_first_auth': None,  # Информация о первой авторизации с IP пользователя
            'ip_last_auth': None,  # Информация о последней авторизации с IP пользователя
            'subnet_first_auth': None,  # Информация о первой авторизации с subnet пользователя
            'subnet_last_auth': None,  # Информация о последней авторизации с subnet пользователя
            'ua_first_auth': {  # Информация о первой авторизации с UA пользователя
                'timestamp': 10,
                'status': 'ses_create',
                'authtype': 'web',
            },
            'ua_last_auth': {  # Информация о последней авторизации с UA пользователя
                'timestamp': 1000,
                'status': 'successful',
                'authtype': 'imap',
            },
            'ip': '5.45.207.254',  # IP пользователя
            'subnet': '5.45.192.0/18',  # subnet пользователя
            'ua': {  # UA пользователя
                'os.name': 'windows xp',
                'yandexuid': 'yandexuid',
                'browser.name': 'firefox',
            },
        },
        'registration': {  # Информация об окружении при регистрации аккаунта
            'ip': None,
            'subnet': None,
            'ua': {
                'os.name': None,
                'yandexuid': None,
                'browser.name': None,
            },
        },
        'factor': {
            'auths_limit_reached': 0,  # Признак того, что был достигнут лимит по числу авторизаций при запросе истории
            'ip_eq_reg': -1,  # Признак совпадения IP пользователя с регистрационным
            'subnet_eq_reg': -1,  # Признак совпадения subnet пользователя с регистрационным
            'ua_eq_reg': 0,  # Признак совпадения UA пользователя с регистрационным
            'ip_auth_interval': -1,  # Фактор для временного интервала IP
            'subnet_auth_interval': -1,  # Фактор для временного интервала subnet
            'ua_auth_interval': 0.5,  # Фактор для временного интервала UA
            'ip_first_auth_depth': -1,  # Фактор глубины для первой авторизации с IP пользователя
            'subnet_first_auth_depth': -1,  # Фактор глубины для первой авторизации с subnet пользователя
            'ua_first_auth_depth': 1,  # Фактор глубины для первой авторизации с UA пользователя
        },
    },
    'aggregated': {  # Данные по аггрегированным факторам
        'actual': {
            # Найденные авторизации для окружения смены в один день
            # пароля и персональных данных (до трех различных значений)
            'password_and_personal_change_one_day': {
                'ua_first_auth': [
                    None,
                    None,
                    None,
                ],
                'subnet_first_auth': [
                    None,
                    None,
                    None,
                ],
                'ip_first_auth': [
                    None,
                    None,
                    None,
                ],
            },
            # Найденные авторизации для окружения смены в один день
            # персональных данных и средств восстановления (до четырех различных значений)
            'personal_and_recovery_change_one_day': {
                'ua_first_auth': [
                    {
                        'timestamp': 10,
                        'status': 'successful',
                        'authtype': 'imap',
                    },
                    None,
                    None,
                    None,
                ],
                'subnet_first_auth': [
                    {
                        'timestamp': 10,
                        'status': 'successful',
                        'authtype': 'imap',
                    },
                    None,
                    None,
                    None,
                ],
                'ip_first_auth': [
                    {
                        'timestamp': 10,
                        'status': 'successful',
                        'authtype': 'imap',
                    },
                    {
                        'timestamp': 500,
                        'status': 'successful',
                        'authtype': 'imap',
                    },
                    None,
                    None,
                ],
            },
            # Найденные авторизации для окружения смены в один день
            # средств восстановления и пароля (до трех различных значений)
            'password_and_recovery_change_one_day': {
                'ua_first_auth': [
                    None,
                    None,
                    None,
                ],
                'subnet_first_auth': [
                    None,
                    None,
                    None,
                ],
                'ip_first_auth': [
                    None,
                    None,
                    None,
                ],
            },
        },
        'factor': {
            # Факторы для окружения смены в один день
            # пароля и персональных данных
            'password_and_personal_change_one_day': {
                'ip_match': 0,  # Выявлено совпадение по IP для смен в один день
                'ua_match': 0,  # Выявлено совпадение по UA для смен в один день
                'subnet_match': 0,  # Выявлено совпадение по subnet для смен в один день
                # Факторы сравнения найденного окружения смен в один день и регистрационного окружения
                'ip_eq_reg': -1,
                'subnet_eq_reg': -1,
                'ua_eq_reg': -1,
                # Факторы сравнения найденного окружения смен в один день и пользовательского окружения
                'ip_eq_user': -1,
                'subnet_eq_user': -1,
                'ua_eq_user': -1,
                'ip_first_auth_depth': [  # Глубина IP окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'subnet_first_auth_depth': [  # Глубина subnet окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'ua_first_auth_depth': [  # Глубина UA окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],

            },
            # Факторы для окружения смены в один день
            # персональных данных и средств восстановления
            'personal_and_recovery_change_one_day': {
                'ip_match': 0,  # Выявлено совпадение по IP для смен в один день
                'subnet_match': 1,  # Выявлено совпадение по subnet для смен в один день
                'ua_match': 1,  # Выявлено совпадение по UA для смен в один день
                # Факторы сравнения найденного окружения смен в один день и регистрационного окружения
                'ip_eq_reg': -1,
                'subnet_eq_reg': -1,
                'ua_eq_reg': 0,
                # Факторы сравнения найденного окружения смен в один день и пользовательского окружения
                'ip_eq_user': 1,
                'subnet_eq_user': 0,
                'ua_eq_user': 1,
                'ip_first_auth_depth': [  # Глубина IP окружения найденной смены в один день
                    1.0,
                    0.8,
                    -1,
                    -1,
                ],
                'subnet_first_auth_depth': [  # Глубина subnet окружения найденной смены в один день
                    1.0,
                    -1,
                    -1,
                    -1,
                ],
                'ua_first_auth_depth': [  # Глубина UA окружения найденной смены в один день
                    1.0,
                    -1,
                    -1,
                    -1,
                ],
            },
            # Факторы для окружения смены в один день
            # пароля и средств восстановления
            'password_and_recovery_change_one_day': {
                'ip_match': 0,  # Выявлено совпадение по IP для смен в один день
                'ua_match': 0,  # Выявлено совпадение по UA для смен в один день
                'subnet_match': 0,  # Выявлено совпадение по subnet для смен в один день
                # Факторы сравнения найденного окружения смен в один день и регистрационного окружения
                'ip_eq_reg': -1,
                'subnet_eq_reg': -1,
                'ua_eq_reg': -1,
                # Факторы сравнения найденного окружения смен в один день и пользовательского окружения
                'ip_eq_user': -1,
                'subnet_eq_user': -1,
                'ua_eq_user': -1,
                'ip_first_auth_depth': [  # Глубина IP окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'subnet_first_auth_depth': [  # Глубина subnet окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'ua_first_auth_depth': [  # Глубина UA окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
            },
        },
    },
}


def _build_version_multistep_41():
    data = dict(
        TEST_FACTORS_DATA_VERSION_MULTISTEP_4,
        version='multistep.4.1',
    )
    data['aggregated'] = {
        'matches': {
            # Найденные совпадения для смены в один день
            # персональных данных и средств восстановления, сгруппированные попарно по сменам данных
            'personal_and_recovery_change_one_day': [
                # Найденные смены сравниваются каждая с каждой, поэтому максимальное число элементов - 4
                # (две последние смены для ФИО и ДР, и две смены для КО и телефона)
                {
                    'envs': [  # Всегда пара смен, в пределах одного дня
                        {
                            'timestamp': 1000,
                            'entity': 'names',  # Название персональных данных, которые были изменены.
                            'ip': '5.45.207.254',
                            'subnet': '5.45.192.0/18',
                            'ua': {'os.name': None, 'yandexuid': '123', 'browser.name': None},
                            # Информация о найденной первой авторизации с IP/подсети/UA смены
                            'ip_first_auth_info': {'status': 'successful', 'timestamp': 500, 'authtype': 'imap'},
                            'subnet_first_auth_info': {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'},
                            'ua_first_auth_info': None,
                        },
                        {
                            'timestamp': 1000,
                            'entity': 'phone_numbers',
                            'ip': '5.45.207.254',
                            'subnet': '5.45.192.0/18',
                            'ua': {'os.name': None, 'yandexuid': '123', 'browser.name': None},
                            'ip_first_auth_info': {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'},
                            'subnet_first_auth_info': {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'},
                            'ua_first_auth_info': None,
                        },
                    ],
                    'fields': ['ip', 'subnet'],  # Совпавшие компоненты окружений, всегда как минимум одно значение
                },
                {
                    'envs': [
                        {
                            'timestamp': 1000,
                            'entity': 'birthday',
                            'ip': '192.168.0.1',
                            'subnet': None,
                            'ua': {'os.name': 'windows xp', 'yandexuid': 'yandexuid', 'browser.name': 'firefox'},
                            'ip_first_auth_info': None,
                            'subnet_first_auth_info': None,
                            'ua_first_auth_info': {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'},
                        },
                        {
                            'timestamp': 1000,
                            'entity': 'answer',
                            'ip': '10.10.10.10',
                            'subnet': None,
                            'ua': {'os.name': 'windows xp', 'yandexuid': 'yandexuid', 'browser.name': 'firefox'},
                            'ip_first_auth_info': None,
                            'subnet_first_auth_info': None,
                            'ua_first_auth_info': {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'},
                        },
                    ],
                    'fields': ['ua'],
                },
            ],
            # Найденные совпадения для смены в один день
            # пароля и персональных данных, сгруппированные попарно по сменам данных
            'password_and_personal_change_one_day': [],
            # Найденные совпадения для смены в один день
            # средств восстановления и пароля, сгруппированные попарно по сменам данных
            'password_and_recovery_change_one_day': [],
        },
        'factor': {
            # Факторы для окружения смены в один день
            # пароля и персональных данных
            'password_and_personal_change_one_day': {
                'ip_match': 0,  # Выявлено совпадение по IP для смен в один день
                'ua_match': 0,  # Выявлено совпадение по UA для смен в один день
                'subnet_match': 0,  # Выявлено совпадение по subnet для смен в один день
                # Факторы сравнения найденного окружения смен в один день и регистрационного окружения
                'ip_eq_reg': -1,
                'subnet_eq_reg': -1,
                'ua_eq_reg': -1,
                # Факторы сравнения найденного окружения смен в один день и пользовательского окружения
                'ip_eq_user': -1,
                'subnet_eq_user': -1,
                'ua_eq_user': -1,
                'ip_first_auth_depth': [  # Глубина IP окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'subnet_first_auth_depth': [  # Глубина subnet окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'ua_first_auth_depth': [  # Глубина UA окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],

            },
            # Факторы для окружения смены в один день
            # персональных данных и средств восстановления
            'personal_and_recovery_change_one_day': {
                'ip_match': 0,  # Выявлено совпадение по IP для смен в один день
                'subnet_match': 1,  # Выявлено совпадение по subnet для смен в один день
                'ua_match': 1,  # Выявлено совпадение по UA для смен в один день
                # Факторы сравнения найденного окружения смен в один день и регистрационного окружения
                'ip_eq_reg': -1,
                'subnet_eq_reg': -1,
                'ua_eq_reg': 0,
                # Факторы сравнения найденного окружения смен в один день и пользовательского окружения
                'ip_eq_user': 1,
                'subnet_eq_user': 0,
                'ua_eq_user': 1,
                'ip_first_auth_depth': [  # Глубина IP окружения найденной смены в один день
                    1.0,
                    0.8,
                    -1,
                    -1,
                ],
                'subnet_first_auth_depth': [  # Глубина subnet окружения найденной смены в один день
                    1.0,
                    -1,
                    -1,
                    -1,
                ],
                'ua_first_auth_depth': [  # Глубина UA окружения найденной смены в один день
                    1.0,
                    -1,
                    -1,
                    -1,
                ],
            },
            # Факторы для окружения смены в один день
            # пароля и средств восстановления
            'password_and_recovery_change_one_day': {
                'ip_match': 0,  # Выявлено совпадение по IP для смен в один день
                'ua_match': 0,  # Выявлено совпадение по UA для смен в один день
                'subnet_match': 0,  # Выявлено совпадение по subnet для смен в один день
                # Факторы сравнения найденного окружения смен в один день и регистрационного окружения
                'ip_eq_reg': -1,
                'subnet_eq_reg': -1,
                'ua_eq_reg': -1,
                # Факторы сравнения найденного окружения смен в один день и пользовательского окружения
                'ip_eq_user': -1,
                'subnet_eq_user': -1,
                'ua_eq_user': -1,
                'ip_first_auth_depth': [  # Глубина IP окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'subnet_first_auth_depth': [  # Глубина subnet окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
                'ua_first_auth_depth': [  # Глубина UA окружения найденной смены в один день
                    -1,
                    -1,
                    -1,
                ],
            },
        },
    }
    return data


TEST_FACTORS_DATA_VERSION_MULTISTEP_41 = _build_version_multistep_41()


def _build_version_multistep_42():
    data = dict(
        deepcopy(TEST_FACTORS_DATA_VERSION_MULTISTEP_41),
        version='multistep.4.2',
    )
    data['names']['indices'] = {
        'current': (
            (0, 1),  # Индексы лучших имени и фамилии из введенных вариантов
            1,  # Индекс в истории (указывает на самое последнее значение)
        ),
        'registration': (
            (0, 1),
            0,
        ),
        'intermediate': None,
    }
    data['names']['factor'] = {
        'current': [0, 0],  # Совпадение с текущими ФИ - пара факторов для введенных имени и фамилии
        'intermediate': [-1, -1],  # Лучшее совпадение с промежуточными ФИ - пара факторов для введенных имени и фамилии
        'intermediate_depth': -1,  # Фактор глубины для лучшего промежуточного совпадения - если совпадение найдено
        'registration': [0, 0],  # Совпадение с регистрационными ФИ - пара факторов для введенных имени и фамилии
        'change_count': 1,  # Число смен ФИ в истории (первичное задание не считается)
        'change_depth': [  # Глубина для первой и двух последних смен
            1.0,
            -1,
            1.0,
        ],
        'change_ip_eq_reg': [  # Совпадение IP смен с IP регистрации
            0,
            -1,
            0,
        ],
        'change_subnet_eq_reg': [  # Совпадение subnet смен с subnet регистрации
            1,
            -1,
            1,
        ],
        'change_ua_eq_reg': [  # Совпадение UA смен с UA регистрации
            3,
            -1,
            3,
        ],
        'change_ip_eq_user': [  # Совпадение IP смен с IP пользователя
            0,
            -1,
            0,
        ],
        'change_subnet_eq_user': [  # Совпадение subnet смен с subnet пользователя
            1,
            -1,
            1,
        ],
        'change_ua_eq_user': [  # Совпадение UA смен с UA пользователя
            0,
            -1,
            0,
        ],
    }
    data['birthday']['factor'] = {  # Описание факторов аналогично факторам names
        'intermediate': -1,
        'intermediate_depth': -1,  # Фактор глубины для лучшего промежуточного совпадения - если совпадение найдено
        'registration': 1,  # Означает неточное совпадение (без учета года)
        'current': 2,  # Означает точное совпадение
        'change_count': 1,
        'change_depth': [
            -1,
            -1,
            -1,
        ],
        'change_ip_eq_user': [
            -1,
            -1,
            -1,
        ],
        'change_subnet_eq_user': [
            -1,
            -1,
            -1,
        ],
        'change_ua_eq_user': [
            0,
            -1,
            0,
        ],
        'change_ip_eq_reg': [
            -1,
            -1,
            -1,
        ],
        'change_subnet_eq_reg': [
            -1,
            -1,
            -1,
        ],
        'change_ua_eq_reg': [
            0,
            -1,
            0,
        ],
    }
    data['passwords']['actual'] = {
        'last_change_request': {  # Информация о последнем принуждении к смене пароля
            'admin': 'alexco',
            'comment': 'broken',
            'change_required': True,  # Признак, было ли принуждение выставлено или снято
            'origin_info': {
                'timestamp': 1,
                'user_ip': '5.45.207.254',
                'yandexuid': '123',
            },
        },
        'last_change': {  # Информация о последней смене пароля, выполненной пользователем
            'origin_info': {
                'user_ip': '5.45.207.254',
                'timestamp': 1000,
                'yandexuid': 'yandexuid',
            },
            'change_type': 'forced',  # Тип смены; другие значения - voluntary, restore
        },
        'change_ip_first_auth': [{  # Информация о первой авторизации с IP последней смены
            'timestamp': 500,
            'status': 'successful',
            'authtype': 'imap',
        }],
        'change_subnet_first_auth': [{  # Информация о первой авторизации с subnet последней смены
            'timestamp': 10,
            'status': 'successful',
            'authtype': 'imap',
        }],
        'change_ua_first_auth': [{  # Информация о первой авторизации с UA последней смены
            'timestamp': 10,
            'status': 'successful',
            'authtype': 'imap',
        }],
    }
    data['passwords']['factor'] = {
        'entered_count': 1,  # Число введенных вариантов пароля
        'auth_found': [  # Список факторов-признаков того, найдена ли авторизация паролем в истории.
                         # Если поиск не выполнялся, значение -1. Всегда 3 элемента.
            0,
            -1,
            -1,
        ],
        'auth_date': [  # Список факторов нечеткого сравнения дат (по одному для каждого варианта пароля), значение от 0.0 до 1.0,
                        # либо -1, если не было сравнения. Всегда 3 элемента.
            -1,
            -1,
            -1,
        ],
        'first_auth_depth': [  # Глубина заведения пароля, если он был найден, для каждого из введенных вариантов
            -1,
            -1,
            -1,
        ],
        'change_count': 0,  # Число смен пароля
        'forced_change_pending': 1,  # Признак того, требуется ли принудительная смена
        'last_change_is_forced_change': -1,  # Признак того, что последняя смена - принудительная
        'change_depth': [-1],  # Глубина последней смены
        'change_ip_first_auth_depth': [-1],  # Глубина первой авторизации с IP последней смены
        'change_subnet_first_auth_depth': [0.0],  # Глубина первой авторизации с subnet последней смены
        'change_ua_first_auth_depth': [0.0],  # Глубина первой авторизации с UA последней смены
        'change_ip_eq_user': [-1],  # Фактор совпадения IP последней смены с пользовательским
        'change_subnet_eq_user': [-1],  # Фактор совпадения subnet последней смены с пользовательским
        'change_ua_eq_user': [-1],  # Фактор совпадения UA последней смены с пользовательским
    }
    data['answer']['factor'].update({
        # Факторы смены для найденных совпадений - для первого и последнего по времени задания значений
        # Пользователь вводит одно значение, однако оно может быть задано несколько раз
        'match_depth': [1.0, 1.0],
        'match_ip_eq_reg': [-1, -1],
        'match_ip_eq_user': [0, 1],
        'match_subnet_eq_reg': [-1, -1],
        'match_subnet_eq_user': [1, 1],
        'match_ua_eq_reg': [0, 0],
        'match_ua_eq_user': [0, 3],
        'match_ip_first_auth_depth': [-1, 0.7],  # Глубина первой авторизации с IP задания совпавшего значения (первого и посл.)
        'match_subnet_first_auth_depth': [-1, 1.0],
        'match_ua_first_auth_depth': [0.0, -1],
    })
    data['answer']['actual'] = {
        # Информация о найденных авторизациях для окружений, в которых были заданы совпавшие значения
        # (первое и последнее по времени совпавшее значение)
        'match_ip_first_auth': [None, {'status': 'successful', 'timestamp': 500, 'authtype': 'imap'}],
        'match_subnet_first_auth': [None, {'status': 'successful', 'timestamp': 10, 'authtype': 'imap'}],
        'match_ua_first_auth': [{'status': 'successful', 'timestamp': 10, 'authtype': 'imap'}, None],
    }
    data['phone_numbers']['factor'].update({
        # Факторы смены для найденных совпадений - для первого и последнего по времени задания значений
        # Аналогично КО
        'match_depth': [1.0, 1.0],  # Обычный фактор глубины для времени задания
        'match_ip_eq_reg': [-1, -1],
        'match_ip_eq_user': [1, 1],
        'match_subnet_eq_reg': [-1, -1],
        'match_subnet_eq_user': [1, 1],
        'match_ua_eq_reg': [0, 0],
        'match_ua_eq_user': [0, 0],
        'match_ip_first_auth_depth': [-1, -1],
        'match_subnet_first_auth_depth': [-1, -1],
        'match_ua_first_auth_depth': [-1, -1],
    })
    data['phone_numbers']['actual'] = {
        # Информация о найденных авторизациях для окружений, в которых были заданы совпавшие значения
        # (первое и последнее по времени совпавшее значение)
        'match_ip_first_auth': [None, None],
        'match_subnet_first_auth': [None, None],
        'match_ua_first_auth': [None, None],
    }
    return data


def _build_version_multistep_43():
    data = _build_version_multistep_42()
    data['version'] = 'multistep.4.3'
    data['passwords']['factor'].update({
        'equals_current': [0, -1, -1],
    })
    return data


TEST_FACTORS_DATA_VERSION_MULTISTEP_42 = _build_version_multistep_42()


TEST_FACTORS_DATA_VERSION_MULTISTEP_43 = _build_version_multistep_43()
