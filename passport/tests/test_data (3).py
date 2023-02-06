# -*- coding: utf-8 -*-
from datetime import (
    datetime,
    timedelta,
)


TEST_GSM_TEXT = u'Tèst'
TEST_UNICODE16_TEXT = u'Галочка, ты сейчас умрешь. Или станешь сильнее'
TEST_UNICODE16_LONG_TEXT = u'Дверь в лето' * 160
TEST_LONG_TEXT = u'foo' * (160 * 6)

TEST_TEMPLATE_TEXT = u'abcdфываф {{param_1  }} 321 {{  param_2}} '
TEST_TEMPLATE_PARAMS = u'{"param_1": "Тестовый параметр №1", "param_2": "Еще 1 параметр", "param_3": "Неиспользуемый"}'
TEST_TEMPLATE_RENDERED = u'abcdфываф Тестовый параметр №1 321 Еще 1 параметр'
TEST_TEMPLATE_RENDERED_MASKED = u'abcdфываф Т******************1 321 Е************р'

TEST_UID = 1001
TEST_FROM_UID = 1002
TEST_PHONE = '+79990010101'
TEST_MASKED_PHONE = '+7999001****'
TEST_OTHER_PHONE = '+79990010102'
TEST_BLOCKED_PHONE = '+78121311000'
TEST_INVALID_PHONE = '+001123123'
TEST_PHONE_ID = 123
TEST_OTHER_PHONE_ID = 321
TEST_SENDER = 'dev'
TEST_TAXI_SENDER = 'Yandex.Taxi'

TEST_DEFAULT_ROUTE = 'default'
TEST_TAXI_ROUTE = 'taxi'
TEST_ROUTE = 'rainbow'

TEST_GATE_ID = 1
TEST_AUTORU_GATE_ID = 2
TEST_GATE_ID_DEVNULL = 3
TEST_NOT_EXISTING_GATE_ID = 1111
TEST_CALLER = 'dev'
TEST_IDENTITY = 'step_1'
TEST_CONSUMER_IP = '127.0.0.1'

TEST_ROUTE_ACTION = 'route'
TEST_DUMP_ACTION = 'dump'
TEST_UNKNOWN_ACTION = 'random'
TEST_MESSAGE = 'UNSENDABLE'
TEST_SMS_ID = 1
TEST_SMS = {
    'smsid': TEST_SMS_ID,
    'phone': TEST_PHONE,
    'status': 'ready',
    'gateid': TEST_GATE_ID,
    'dlrmessage': None,
    'text': TEST_GSM_TEXT,
    'create_time': '0000-00-00 00:00:00',
    'touch_time': '0000-00-00 00:00:00',
    'sender': TEST_SENDER,
    'errors': 0,
}

TEST_GATE = {
    u'gateid': 12,
    u'fromname': 'Yandex',
    u'aliase': 'infobip',
}

TEST_BLACKBOX_CLIENT_ID = 1
TEST_KOLMOGOR_CLIENT_ID = 2

TEST_SMS_TO_SEND = {
    u'errors': 0,
    u'sender': 'passport',
    u'text': 'abc',
    u'smsid': 39,
    u'phone': '+79104714456',
    u'gateid': 12,
}

TEST_CACHED_ROUTES = [
    {'gateid': 1, 'gateid2': 7, 'gateid3': 8, 'prefix': '+', 'mode': 'default', 'weight': 1, 'aliase': 'infobip'},
    {'gateid': 2, 'gateid2': 0, 'gateid3': 0, 'prefix': '+70001', 'mode': 'autoru', 'weight': 1, 'aliase': 'infobip'},
    {'gateid': 3, 'gateid2': 0, 'gateid3': 0, 'prefix': '+70000', 'mode': 'default', 'weight': 1, 'aliase': 'devnull'},
    {'gateid': 4, 'gateid2': 0, 'gateid3': 0, 'prefix': '+', 'mode': 'taxi', 'weight': 1, 'aliase': 'infobipyt'},
    {'gateid': 7, 'gateid2': 1, 'gateid3': 8, 'prefix': '+', 'mode': 'default', 'weight': 1, 'aliase': 'mfms'},
    {'gateid': 8, 'gateid2': 1, 'gateid3': 7, 'prefix': '+7900', 'mode': 'default', 'weight': 1, 'aliase': 'gms'},
    {'gateid': 1, 'gateid2': 0, 'gateid3': 0, 'prefix': '+7000', 'mode': 'default', 'weight': 2, 'aliase': 'infobip'},
]

TEST_CACHED_GATES = [
    {'gateid': 1, 'aliase': 'infobip', 'fromname': 'Yandex'},
    {'gateid': 2, 'aliase': 'infobip', 'fromname': 'AUTO.RU'},
]

TEST_METADATA = {'service': 'dev'}

INITIAL_TEST_DB_DATA = {
    'smsrt': [
        {
            'ruleid': 1,
            'destination': '+',
            'gateid': 1,
            'gateid2': 7,
            'gateid3': 8,
            'mode': 'default',
            'weight': 1,
            'groupname': '',
        },
        {
            'ruleid': 2,
            'destination': '+70001',
            'gateid': 2,
            'gateid2': 0,
            'gateid3': 0,
            'mode': 'autoru',
            'weight': 1,
            'groupname': '',
        },
        {
            'ruleid': 3,
            'destination': '+70000',
            'gateid': 3,
            'gateid2': 0,
            'gateid3': 0,
            'mode': 'default',
            'weight': 1,
            'groupname': '',
        },
        {
            'ruleid': 4,
            'destination': '+70001',
            'gateid': 18,
            'gateid2': 0,
            'gateid3': 0,
            'mode': 'default',
            'weight': 1,
            'groupname': '',
        },
        {
            'ruleid': 5,
            'destination': '+',
            'gateid': 4,
            'gateid2': 0,
            'gateid3': 0,
            'mode': 'taxi',
            'weight': 1,
            'groupname': '',
        },
        {
            'ruleid': 7,
            'destination': '+7000',
            'gateid': 1,
            'gateid2': 0,
            'gateid3': 0,
            'mode': 'default',
            'weight': 2,
            'groupname': '',
        },
        {
            'ruleid': 8,
            'destination': '+',
            'gateid': 7,
            'gateid2': 1,
            'gateid3': 8,
            'mode': 'default',
            'weight': 1,
            'groupname': '',
        },
        {
            'ruleid': 9,
            'destination': '+7900',
            'gateid': 8,
            'gateid2': 1,
            'gateid3': 7,
            'mode': 'default',
            'weight': 1,
            'groupname': '',
        },
    ],
    'blockedphones': [
        {
            'blockid': 1,
            'phone': '+78121311000',
            'phoneid': 0,
            'blocktype': 'permanent',
            'blocktill': datetime.now() + timedelta(days=1),
        },
        {
            'blockid': 2,
            'phone': TEST_OTHER_PHONE,
            'phoneid': 0,
            'blocktype': 'temporary',
            'blocktill': datetime.now() - timedelta(days=1),
        },
    ],
    'smsgates': [
        {
            'gateid': 1,
            'aliase': 'infobip',
            'fromname': 'Yandex',
            'description': 'infobip',
            'delay': 0,
        },
        {
            'gateid': 2,
            'aliase': 'infobip',
            'fromname': 'AUTO.RU',
            'description': 'infobip; for auto.ru; alpha-name "AUTO.RU"',
            'delay': 0,
        },
        {
            'gateid': 3,
            'aliase': 'devnull',
            'fromname': 'Yandex',
            'description': '/dev/null',
            'delay': 0,
        },
        {
            'gateid': 4,
            'aliase': 'infobipyt',
            'fromname': 'Yandex.Taxi',
            'description': 'infobip; for taxi; alpha-name "Yandex.Taxi"',
            'delay': 0,
        },
        {
            'gateid': 6,
            'aliase': 'infobip_new',
            'fromname': 'Yandex.SomethingNew',
            'description': 'infobip_new; for something new; alpha-name "Yandex.SomethingNew"',
            'delay': 0,
        },
        {
            'gateid': 7,
            'aliase': 'mfms',
            'fromname': 'Yandex',
            'description': 'mfms for testing rerouting',
            'delay': 0,
        },
        {
            'gateid': 8,
            'aliase': 'gms',
            'fromname': 'Yandex.Global',
            'description': 'gms with expensive calls',
            'delay': 0,
        },
    ],
    'daemon_heartbeat': [
        {
            'hostname': 'yasms-dev.passport.yandex.net',
            'beat_time': datetime.now(),
        },
        {
            'hostname': 'phone-passport-dev.yandex.net',
            'beat_time': datetime.now() - timedelta(seconds=5),
        },
    ],
}
