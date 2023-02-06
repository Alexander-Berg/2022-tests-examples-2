import datetime
import typing

import psycopg2
import pytz

DEVICE_ID_NO_PARTNER = '12349fbd4c7767aef1a6c4a123456789'
DEVICE_PRIMARY_KEY_NO_PARTNER = 5
DRIVER_NAME_NO_PARTNER = None
VEHICLE_PLATE_NUMBER_NO_PARTNER = None

DEVICE_ID_PARTNER_1 = '6b3b9123656f4a808ce3e7c52a0be835'
DEVICE_PRIMARY_KEY_PARTNER_1 = 3
DEVICE_NAME_PARTNER_1 = 'signalq1_3'
DRIVER_NAME_PARTNER_1 = 'Настенька'
VEHICLE_PLATE_NUMBER_PARTNER_1 = None

DEVICE_ID_PARTNER_2 = '77748dae0a3244ebb9e1b8d244982c28'
DEVICE_PRIMARY_KEY_PARTNER_2 = 4
DEVICE_NAME_PARTNER_2 = ''
DRIVER_NAME_PARTNER_2 = None
VEHICLE_PLATE_NUMBER_PARTNER_2 = None

DEVICE_ID_MISSING = '7a580c9f6cbeb31b3b73c2b107691a1d'

PARTNER_PASSPORT_UID_1 = '54591353'
PARTNER_PASSPORT_UID_2 = '121766829'
PARTNER_PASSPORT_UID_NONEXISTENT = '6755068'
YA_TEAM_PASSPORT_UID = '63504250'

OLD_UPDATED_AT = datetime.datetime(
    1999,
    1,
    1,
    12,
    0,
    0,
    tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None),
)

# `tvmknife unittest service --src 111 --dst 2016267`
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxCLiHs:NnLj18bjvNK1BNWUBc'
    'HKTNjeXkLh7xHowhQUxF7XjcFEibaG5NLaTCtH-eKcfY3PcTWMNue'
    'reDTyW2pm9N5-rCd_p-RZ_cyFqqH8rq0w7Sj_jnE1sKs3XuzK3IPm'
    'C83XNKspEYsr4u_KgWGQcV_gIXmpPcTunHD1l72MzqYk7yg'
)
MOCK_USER_TICKET = 'valid_user_ticket'
PARTNER_HEADERS_1 = {
    'X-Ya-User-Ticket': MOCK_USER_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Yandex-UID': PARTNER_PASSPORT_UID_1,
}
PARTNER_HEADERS_2 = {
    'X-Ya-User-Ticket': MOCK_USER_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Yandex-UID': PARTNER_PASSPORT_UID_2,
}
PARTNER_HEADERS_NONEXISTENT = {
    'X-Ya-User-Ticket': MOCK_USER_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Yandex-UID': PARTNER_PASSPORT_UID_NONEXISTENT,
}
YA_TEAM_HEADERS = {
    'X-Ya-User-Ticket': MOCK_USER_TICKET,
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Yandex-UID': YA_TEAM_PASSPORT_UID,
}
YA_TEAM_HEADERS_WITHOUT_USER_TICKET = {
    'X-Ya-User-Ticket-Provider': 'yandex_team',
    'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET,
    'X-Yandex-UID': YA_TEAM_PASSPORT_UID,
}

DEMO_DEVICES = [
    {
        'id': 'dev1',
        'serial_number': '11111',
        'mac_wlan0': '11111',
        'group_id': 'sg1',
        'vehicle_id': 'v1',
        'driver_id': 'dr1',
        'is_online': True,
    },
    {
        'id': 'dev2',
        'serial_number': '77777',
        'mac_wlan0': '77777',
        'group_id': 'g2',
        'driver_id': 'dr2',
    },
    {
        'id': 'dev3',
        'serial_number': '33333',
        'mac_wlan0': '33333',
        'is_in_park': False,
    },
]

DEMO_DRIVERS = [
    {
        'id': 'dr1',
        'first_name': 'Roman',
        'last_name': 'Maresov',
        'phones': ['+77777777777'],
    },
    {'id': 'dr2', 'first_name': 'Grisha', 'last_name': 'Dergachev'},
]

DEMO_VEHICLES = [
    {'id': 'v1', 'plate_number': 'Y777RM'},
    {'id': 'v2', 'plate_number': 'Y777GD'},
]

DEMO_GROUPS = [
    {'id': 'g1', 'name': 'SuperWeb'},
    {'id': 'sg1', 'name': 'SignalQ', 'parent_group_id': 'g1'},
    {'id': 'g2', 'name': 'Scooters'},
]

DEMO_EVENTS = [
    {
        'id': 'e1',
        'event_type': 'seatbelt',
        'device_id': 'dev1',
        'vehicle_id': 'v2',
    },
    {
        'id': 'e2',
        'event_type': 'tired',
        'device_id': 'dev2',
        'driver_id': 'dr1',
        'with_comments': True,
    },
    {
        'id': 'e3',
        'event_type': 'sleep',
        'device_id': 'dev2',
        'driver_id': 'dr2',
    },
    {
        'id': 'e4',
        'event_type': 'ushel v edu',
        'device_id': 'dev2',
        'driver_id': 'dr2',
    },
    {
        'id': 'e5',
        'event_type': 'brosil signalq',
        'device_id': 'dev1',
        'vehicle_id': 'v2',
    },
    {
        'id': 'e6',
        'event_type': 'kak teper zhit',
        'device_id': 'dev1',
        'driver_id': 'dr1',
        'vehicle_id': 'v2',
    },
    {'id': 'e7', 'event_type': 'third eye', 'device_id': 'dev2'},
]


def get_demo_whitelist(critical_types=None):
    return [
        {
            'event_type': typing.cast(typing.Dict[str, str], event)[
                'event_type'
            ],
            'is_critical': (
                bool(critical_types)
                and (
                    typing.cast(typing.Dict[str, str], event)['event_type']
                    in critical_types
                )
            ),
            'is_violation': False,
            'fixation_config_path': 'some_path',
        }
        for event in DEMO_EVENTS
    ]


def get_fleet_parks_info(park_id='p1'):
    return {
        'city_id': 'CITY_ID1',
        'country_id': 'rus',
        'demo_mode': False,
        'id': park_id,
        'is_active': True,
        'is_billing_enabled': True,
        'is_franchising_enabled': False,
        'locale': 'ru',
        'login': 'LOGIN1',
        'name': 'NAME1',
        'geodata': {'lat': 1, 'lon': 1, 'zoom': 1},
    }


def is_ya_team_headers(headers):
    return headers['X-Ya-User-Ticket-Provider'] == 'yandex_team'


def message_404(device_id, is_ya_team):
    result = f'device with id `{device_id}` is not registered'
    if is_ya_team:
        result += ' or has no partner'
    return result


def select_web_info(pgsql, device_primary_key, fields):
    db = pgsql['signal_device_api_meta_db'].cursor()
    db.execute(
        'SELECT {} FROM signal_device_api.devices_web_info '
        'WHERE id={}'.format(','.join(fields), device_primary_key),
    )
    return {k: v for (k, v) in zip(fields, list(db)[0])}


def check_field_match(field_name, db_value, expected_value):
    assert (
        db_value == expected_value
    ), f'{field_name} in db = {db_value}, expected = {expected_value}'


def check_device_web_info_in_db(
        pgsql, device_primary_key, updated_at_newer_than=None, **kwargs,
):
    fields = [
        'device_name',
        'vehicle_plate_number',
        'driver_name',
        'partner_passport_uid',
        'updated_at',
    ]
    web_info = select_web_info(pgsql, device_primary_key, fields)
    for field in [f for f in fields if f != 'updated_at']:
        check_field_match(field, web_info[field], kwargs[field])
    if updated_at_newer_than:
        assert (
            web_info['updated_at'].replace(tzinfo=pytz.UTC)
            > updated_at_newer_than
        )
