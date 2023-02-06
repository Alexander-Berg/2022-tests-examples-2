# -*- coding: utf-8 -*-

TEST_UID = 1
TEST_ANOTHER_UID = 321
TEST_LOGIN = 'test.oauth.wrap'
TEST_ANOTHER_LOGIN = TEST_LOGIN + '2'
TEST_REMOTE_ADDR = '1.2.3.4'
TEST_HOST = 'oauth.yandex.ru'
TEST_INTERNAL_HOST = 'oauth-internal.yandex.ru'
TEST_REQUEST_ID = 'request-id'

# FIXME: оставить только одну копию из OTHER / ANOTHER
TEST_OTHER_UID = 2
TEST_OTHER_LOGIN = 'login2'
TEST_GRANT_TYPE = 'authorization_code'
TEST_USER_IP = TEST_REMOTE_ADDR
TEST_YANDEX_IP = '37.9.101.188'
TEST_LOGIN = 'test.user'
TEST_NORMALIZED_LOGIN = 'test-user'
TEST_DISPLAY_NAME = {
    'name': 'Coool user',
}
TEST_AVATAR_ID = '0/0-0'
TEST_GROUP = 'staff:yandex'
TEST_DEVICE_ID = 'ifridge'
TEST_DEVICE_NAME = 'I Am the Fridge'
TEST_OTHER_DEVICE_ID = 'kolonka'

TEST_LOGIN_ID = 'login-id'

TEST_FAKE_UUID = 'fake_uuid'

TEST_TVM_TICKET = (
    '3:serv:CBAQ__________9_IhkI5QEQHBoIYmI6c2VzczEaCGJiOnNlc3My:WUPx1cTf05fjD1exB35T5j2DCHWH1YaLJon_a'
    '4rN-D7JfXHK1Ai4wM4uSfboHD9xmGQH7extqtlEk1tCTCGm5qbRVloJwWzCZBXo3zKX6i1oBYP_89WcjCNPVe1e8jwGdLsnu6'
    'PpxL5cn0xCksiStILH5UmDR6xfkJdnmMG94o8'
)
TEST_TVM_CLIENT_ID = 229


TEST_LOGIN_TO_UID_MAPPING_CONFIG = {
    'test_login': 1,
    'other_login': 2,
    'hacker': 3,
}


TEST_SCOPES_CONFIG = {
    '1': {
        'keyword': 'test:foo',
        'allowed_for_turboapps': True,
        'tags': ['test_tag'],
    },
    '2': {
        'keyword': 'test:bar',
        'ttl': None,
        'is_ttl_refreshable': False,
        'requires_approval': False,
        'is_hidden': False,
        'visible_for_logins': [],
        'has_xtoken_grant': False,
    },
    '3': {
        'keyword': 'test:ttl',
        'ttl': 60,
    },
    '4': {
        'keyword': 'test:ttl_refreshable',
        'ttl': 300,
        'is_ttl_refreshable': True,
    },
    '5': {
        'keyword': 'test:premoderate',
        'requires_approval': True,
    },
    '6': {
        'keyword': 'test:hidden',
        'is_hidden': True,
        'visible_for': ['test_login'],
    },
    '7': {
        'keyword': 'test:invisible',
        'is_hidden': True,
        'visible_for': ['other_login'],
        'visible_for_consumers': ['dev'],
    },
    '8': {
        'keyword': 'test:xtoken',
        'has_xtoken_grant': True,
    },
    '9': {
        'keyword': 'lunapark:use',
    },
    '10': {
        'keyword': 'test:limited:grant_type:password',
        'is_hidden': True,
    },
    '11': {
        'keyword': 'test:limited:grant_type:assertion',
        'is_hidden': True,
    },
    '12': {
        'keyword': 'test:limited:ip',
        'is_hidden': True,
    },
    '13': {
        'keyword': 'test:limited:client',
        'is_hidden': True,
    },
    '14': {
        'keyword': 'test:unlimited',
        'is_hidden': True,
    },
    '15': {
        'keyword': 'deleted:test:zar',
    },
    '16': {
        'keyword': 'app_password:calendar',
    },
    '17': {
        'keyword': 'money:all',
    },
    '18': {
        'keyword': 'test:abc',
        'is_hidden': True,
    },
    '19': {
        'keyword': 'test:default_phone',
        'is_hidden': True,
        'allowed_for_turboapps': True,
    },
    '20': {
        'keyword': 'test:basic_scope',
        'is_hidden': True,
    },
}


DELETED_SCOPE_ID = 15


TEST_SCOPE_LOCALIZATIONS_CONFIG = {
    'ru': {
        'test:foo': 'фу',
        'test:bar': 'бар',
        'test:ttl': 'протухать',
        'test:ttl_refreshable': 'подновляться',
        'test:premoderate': 'премодерироваться',
        'test:hidden': 'прятаться',
        'test:invisible': 'скрываться',
        'lunapark:use': 'стрелять',
        'test:xtoken': 'выдавать',
        'test:limited:grant_type:password': 'позволять только с паролем',
        'test:limited:grant_type:assertion': 'позволять только по доверенности',
        'test:limited:ip': 'позволять только по IP',
        'test:limited:client': 'позволять только приложению',
        'test:unlimited': 'позволять всё',
        'app_password:calendar': 'пользоваться календарём',
        'money:all': 'тратить деньги',
        'test:abc': 'управлять в ABC',
        'test:default_phone': 'узнавать телефон',
        'test:basic_scope': 'ничего не делать',
    },
    'en': {
        'test:foo': 'foo',
        'test:bar': 'bar',
        'test:ttl': 'expire',
        'test:ttl_refreshable': 'refresh',
        'test:premoderate': 'premoderate',
        'test:hidden': 'hide',
        'test:invisible': 'disappear',
        'lunapark:use': 'shoot',
        'test:xtoken': 'issue',
        'test:limited:grant_type:password': 'allow password',
        'test:limited:grant_type:assertion': 'allow assertion',
        'test:limited:ip': 'allow IP',
        'test:limited:client': 'allow client',
        'test:unlimited': 'allow all',
        'app_password:calendar': 'calendar',
        'money:all': 'spend money',
        'test:abc': 'manage via ABC',
        'test:default_phone': 'get phone number',
        'test:basic_scope': 'do nothing',
    },
    'tr': {
        'test:foo': '',
        'test:bar': '',
        'test:ttl': '',
        'test:ttl_refreshable': '',
        'test:premoderate': '',
        'test:hidden': '',
        'test:invisible': '',
        'lunapark:use': '',
        'test:xtoken': '',
        'test:limited:grant_type:password': '',
        'test:limited:grant_type:assertion': '',
        'test:limited:ip': '',
        'test:limited:client': '',
        'test:unlimited': '',
        'app_password:calendar': '',
        'money:all': '',
        'test:abc': '',
        'test:default_phone': '',
        'test:basic_scope': '',
    },
    'uk': {
        'test:foo': '',
        'test:bar': '',
        'test:ttl': '',
        'test:ttl_refreshable': '',
        'test:premoderate': '',
        'test:hidden': '',
        'test:invisible': '',
        'lunapark:use': '',
        'test:xtoken': '',
        'test:limited:grant_type:password': '',
        'test:limited:grant_type:assertion': '',
        'test:limited:ip': '',
        'test:limited:client': '',
        'test:unlimited': '',
        'app_password:calendar': '',
        'money:all': '',
        'test:abc': '',
        'test:default_phone': '',
        'test:basic_scope': '',
    },
}


TEST_SCOPE_SHORT_LOCALIZATIONS_CONFIG = {
    'ru': {
        'test:foo': 'ф',
    },
    'en': {
        'test:foo': 'f',
    },
    'tr': {
        'test:foo': '',
    },
    'uk': {
        'test:foo': '',
    },
}

TEST_SERVICE_LOCALIZATIONS_CONFIG = {
    'ru': {
        'test': 'Тестирование OAuth',
        'lunapark': 'Стрельбы по OAuth',
        'app_password': 'Пароли приложений',
        'money': 'Деньги',
    },
    'en': {
        'test': 'OAuth test',
        'lunapark': 'OAuth tank',
        'app_password': 'App passwords',
        'money': 'Money',
    },
    'tr': {
        'test': '',
        'lunapark': '',
        'app_password': '',
        'money': '',
    },
    'uk': {
        'test': '',
        'lunapark': '',
        'app_password': '',
        'money': '',
    },
}


TEST_SCOPE_GRANTS_CONFIG = {
    'grant_type:assertion': {
        'grants': {
            'grant_type': [
                '*',
            ],
            'client': [
                '*',
            ],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
    },
    'test:limited:grant_type:password': {
        'grants': {
            'grant_type': [
                'password',
            ],
            'client': [
                '*',
            ],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
    },
    'test:limited:grant_type:assertion': {
        'grants': {
            'grant_type': [
                'assertion',
            ],
            'client': [
                '*',
            ],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
    },
    'test:limited:ip': {
        'grants': {
            'grant_type': [
                '*',
            ],
            'client': [
                '*',
            ],
        },
        'networks': [
            '192.168.0.1/24',
            '127.0.0.1',
            'fe80::fe7b:fcff:fe3c:8e01',
        ],
    },
    'test:limited:client': {
        'grants': {
            'grant_type': [
                '*',
            ],
            'client': [
                'a' * 32,  # в тестах заменится нужным
            ],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
    },
    'test:unlimited': {
        'grants': {
            'grant_type': [
                '*',
            ],
            'client': [
                '*',
            ],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
    },
}


TEST_API_GRANTS_CONFIG = {
    'intranet': {
        'grants': {
            'api': [
                '*',
            ],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
    },
    'blackbox': {
        'grants': {
            'api': [
                'verify_token',
                'verify_token_alias',
            ],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
    },
    'external': {
        'grants': {
            'api': [
                'client_info',
                'revoke_token',
            ],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
    },
    'oauth_frontend': {
        'grants': {
            'iface_api': [
                '*',
            ],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
    },
    'dev': {
        'grants': {
            'api': [
                '*',
            ],
            'tvm_api': [
                '*',
            ],
            'tvm_abc_api': [
                '*',
            ],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
    },
    'tvm_dev': {
        'grants': {
            'iface_api': ['*'],
            'api': ['*'],
            'tvm_api': ['*'],
            'tvm_abc_api': ['*'],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
        'client': {
            'client_id': TEST_TVM_CLIENT_ID,
            'client_name': 'Test client',
        },
    },
    'tvm_dev_2': {
        'grants': {
            'iface_api': ['*'],
            'api': ['*'],
            'tvm_api': ['*'],
            'tvm_abc_api': ['*'],
        },
        'networks': [
            '0.0.0.0/0',
            '::/0',
        ],
        'client': {
            'client_id': TEST_TVM_CLIENT_ID + 1,
            'client_name': 'Test client 2',
        },
    },
    'noname': {
        'grants': {
            'api': ['test'],
        },
        'networks': [
            '8.8.8.8/32',
        ],
    },
    'mobileproxy_substitute_ip': {
        'grants': {},
        'networks': [
            '255.255.255.255',
        ],
    },
}


TEST_GRANTS_CONFIG = dict(TEST_SCOPE_GRANTS_CONFIG, **TEST_API_GRANTS_CONFIG)


TEST_ACL_CONFIG = {
    'test_login': [
        'action:*',
        'service:*',
    ],
    'other_login': [
        'action:enter_admin',
        'service:test',
    ],
    'hacker': [],
}


# Отображение * -> (model, manufacturer) нас не интересует, так как при наличии model
# manufacturer не учитываем.
# Отображения manufacturer -> model и (model, manufacturer) -> manufacturer невозможны.
TEST_DEVICE_NAMES_MAPPING_CONFIG = [
    {
        'from': {'model': 'iphone7'},
        'to': {'model': 'iPhone 7'},
    },
    {
        'from': {'model': 'iphone7', 'manufacturer': 'sony'},
        'to': {'model': 'iPhone Cheap'},
    },
    {
        'from': {'manufacturer': 'sony'},
        'to': {'manufacturer': 'Sony'},
    },
]


TEST_TOKEN_PARAMS_CONFIG = {
    'force_stateless': {
        'rule1': {
            'client_id': 'client_id_1',
            'app_id': 'app_id_1',
            'app_platform': 'ios',
            'min_app_version': '1.2.3',
            'denominator': 2,
        },
        'rule2': {
            'client_id': 'client_id_2',
        },
        'rule3': {
            'app_id': 'app_id_2',
        },
        'rule4': {
            'client_id': 'client_id_1',
            'denominator': 0,
        },
    },
}


TEST_CIPHER_KEYS = {
    1: '*' * 32,
    2: '*' * 32,
}


TEST_ABC_SERVICE_ID = 1042
TEST_OTHER_ABC_SERVICE_ID = 1043
