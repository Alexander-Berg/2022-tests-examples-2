import decimal

import dateutil
import pytest

FLEET_PARKS_REQUEST = {'query': {'park': {'ids': ['PARK-01', 'PARK-02']}}}
FLEET_PARKS_RESPONSE = {
    'parks': [
        {
            'id': 'PARK-01',
            'login': 'login1',
            'name': 'name1',
            'is_active': True,
            'city_id': 'city1',
            'locale': 'locale1',
            'is_billing_enabled': False,
            'is_franchising_enabled': False,
            'country_id': 'cid1',
            'demo_mode': False,
            'driver_partner_source': 'yandex',
            'tz_offset': 3,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
        {
            'id': 'PARK-02',
            'login': 'login1',
            'name': 'name1',
            'is_active': True,
            'city_id': 'city1',
            'locale': 'locale1',
            'is_billing_enabled': False,
            'is_franchising_enabled': False,
            'country_id': 'cid1',
            'demo_mode': False,
            'driver_partner_source': 'yandex',
            'tz_offset': 3,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
        {
            'id': 'PARK-03',
            'login': 'login1',
            'name': 'name1',
            'is_active': True,
            'city_id': 'city1',
            'locale': 'locale1',
            'is_billing_enabled': False,
            'is_franchising_enabled': False,
            'country_id': 'cid1',
            'demo_mode': False,
            'driver_partner_source': 'yandex',
            'tz_offset': 3,
            'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
        },
    ],
}

MODULBANK_AUTH_HEADERS = [
    'f0000000-0000-0000-0000-000000000001',
    'f0000000-0000-0000-0000-000000000002',
]
MODULBANK_RESPONSE = {
    'status': 'success',
    'data': {
        'id': 'a0000000-0000-0000-0000-000000000001',
        'status': 'enabled',
        'balance': 1000,
    },
}

FLEET_NOTIFICATIONS_REQUEST = {
    'request_id': 'Balance notification',
    'payload': {
        'title': 'Пополните баланс банковского счета',
        'text': 'Баланс вашего счета в банке Модульбанк ниже 2000.05',
        'entity': {
            'type': 'contractor-instant-payouts/low-account-balance',
            'url': '/account-management',
        },
    },
    'destinations': [
        {'park_id': 'PARK-02', 'position': 'director'},
        {'park_id': 'PARK-02', 'user_id': 'user1'},
        {'park_id': 'PARK-02', 'user_id': 'user2'},
    ],
}

DISPATCHER_ACCESS_CONTROL_REQUEST = {
    'query': {'park': {'id': 'PARK-02'}, 'user': {'is_enabled': True}},
    'offset': 0,
}

DISPATCHER_ACCESS_CONTROL_RESPONSE = {
    'users': [
        {
            'id': 'superuser',
            'email': 'superuser@yandex.ru',
            'park_id': 'park',
            'is_enabled': True,
            'is_confirmed': True,
            'is_superuser': True,
            'is_usage_consent_accepted': True,
        },
        {
            'id': 'user1',
            'email': 'user1@yandex.ru',
            'park_id': 'park',
            'is_enabled': True,
            'is_confirmed': True,
            'is_superuser': False,
            'is_usage_consent_accepted': True,
        },
        {
            'id': 'user2',
            'email': 'user2@yandex.ru',
            'park_id': 'park',
            'is_enabled': True,
            'is_confirmed': True,
            'is_superuser': False,
            'is_usage_consent_accepted': True,
        },
    ],
    'offset': 0,
}

PERSONAL_REQUEST = {
    'items': [
        {'value': 'superuser@yandex.ru'},
        {'value': 'user1@yandex.ru'},
        {'value': 'user2@yandex.ru'},
    ],
    'validate': False,
}

PERSONAL_RESPONSE = {
    'items': [
        {'id': 'superuser', 'value': 'superuser@yandex.ru'},
        {'id': 'user1', 'value': 'user1@yandex.ru'},
        {'id': 'user2', 'value': 'user2@yandex.ru'},
    ],
    'offset': 0,
}


def build_sticker_request(send_to):
    return {
        'body': (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<mails>'
            '<mail encoding="utf-8">'
            '<from>'
            'fleet &lt;no-reply@yandex-team.ru&gt;'
            '</from>'
            '<mime-version>'
            '1.0'
            '</mime-version>'
            '<content-transfer-encoding>'
            '8bit'
            '</content-transfer-encoding>'
            '<content-type>'
            'text/html; charset="UTF-8"'
            '</content-type>'
            '<subject encoding="yes">'
            'Пополните баланс банковского счета'
            '</subject>'
            '<parts>'
            '<part type="text/html">'
            '<body>'
            '<div>'
            'Баланс вашего счета в банке Модульбанк ниже 2000.05'
            '</div>'
            '</body>'
            '</part>'
            '</parts>'
            '</mail>'
            '</mails>'
        ),
        'idempotence_token': '0feebfe2-5e2b-596f-8594-4147654b6ba1_' + send_to,
        'send_to': [send_to],
    }


STICKER_REQUESTS = [
    build_sticker_request('superuser'),
    build_sticker_request('user1'),
    build_sticker_request('user2'),
]

NOW = '2021-01-01T12:00:00+0000'


@pytest.mark.now(NOW)
async def test_ok(
        taxi_contractor_instant_payouts, mockserver, testpoint, pg_dump,
):
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def mock_fleet_parks(request):
        return FLEET_PARKS_RESPONSE

    @mockserver.json_handler(
        '/contractor-instant-payouts-modulbank'
        '/api/accounts/a0000000-0000-0000-0000-000000000001',
    )
    def mock_balance(request):
        return MODULBANK_RESPONSE

    @mockserver.json_handler('dispatcher-access-control/v1/parks/users/list')
    def mock_dispatcher_access_control(request):
        return DISPATCHER_ACCESS_CONTROL_RESPONSE

    @mockserver.json_handler('/personal/v1/emails/bulk_store')
    def mock_personal(request):
        return PERSONAL_RESPONSE

    @mockserver.json_handler('/fleet-notifications/v1/notifications/create')
    def mock_fleet_notifications(request):
        return {}

    @mockserver.json_handler('/sticker/send/')
    def mock_sticker(request):
        return {}

    @testpoint('notificator-get-balances-and-send-notifications-completed')
    def notificator_completed(data):
        pass

    pg_initial = pg_dump()

    async with taxi_contractor_instant_payouts.spawn_task(
            'distlock/notificator-component-task',
    ):
        await notificator_completed.wait_call()

    assert mock_fleet_parks.times_called == 1
    assert mock_fleet_parks.next_call()['request'].json == FLEET_PARKS_REQUEST

    assert mock_balance.times_called == 2
    assert (
        mock_balance.next_call()['request'].headers['Authorization']
        in MODULBANK_AUTH_HEADERS
    )
    assert (
        mock_balance.next_call()['request'].headers['Authorization']
        in MODULBANK_AUTH_HEADERS
    )

    assert mock_fleet_notifications.times_called == 1
    fleet_notifications_request = mock_fleet_notifications.next_call()[
        'request'
    ]
    assert fleet_notifications_request.json == FLEET_NOTIFICATIONS_REQUEST

    assert (
        fleet_notifications_request.headers['X-Idempotency-Token']
        == '0feebfe2-5e2b-596f-8594-4147654b6ba1'
    )

    assert mock_dispatcher_access_control.times_called == 1
    assert (
        mock_dispatcher_access_control.next_call()['request'].json
        == DISPATCHER_ACCESS_CONTROL_REQUEST
    )

    assert mock_personal.times_called == 1
    assert mock_personal.next_call()['request'].json == PERSONAL_REQUEST

    assert mock_sticker.times_called == 3
    assert mock_sticker.next_call()['request'].json in STICKER_REQUESTS
    assert mock_sticker.next_call()['request'].json in STICKER_REQUESTS
    assert mock_sticker.next_call()['request'].json in STICKER_REQUESTS

    assert pg_dump() == {
        **pg_initial,
        'account': {
            101: (
                0,
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                999,
                dateutil.parser.parse('2020-01-01T12:00:00+03:00'),
                'modulbank',
                'PARK-01',
                '00000000-0000-0000-0000-000000000001',
                False,
                True,
                'Account 1',
                'f0000000-0000-0000-0000-000000000001',
                'a0000000-0000-0000-0000-000000000001',
                None,
                True,
                decimal.Decimal('500.0500'),
                [],
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                dateutil.parser.parse('2021-01-01T13:00:00+00:00'),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
            102: (
                0,
                999,
                dateutil.parser.parse('2020-01-01T13:00:00+03:00'),
                999,
                dateutil.parser.parse('2020-01-01T13:00:00+03:00'),
                'modulbank',
                'PARK-02',
                '00000000-0000-0000-0000-000000000002',
                False,
                True,
                'Account 2',
                'f0000000-0000-0000-0000-000000000002',
                'a0000000-0000-0000-0000-000000000001',
                None,
                True,
                decimal.Decimal('2000.0500'),
                ['user1', 'user2'],
                dateutil.parser.parse(NOW),
                dateutil.parser.parse('2021-01-02T12:00:00+00:00'),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
            103: (
                0,
                999,
                dateutil.parser.parse('2020-01-01T14:00:00+03:00'),
                999,
                dateutil.parser.parse('2020-01-01T14:00:00+03:00'),
                'modulbank',
                'PARK-03',
                '00000000-0000-0000-0000-000000000003',
                False,
                True,
                'Account 3',
                'f0000000-0000-0000-0000-000000000003',
                'a0000000-0000-0000-0000-000000000001',
                None,
                False,
                decimal.Decimal('0.0000'),
                [],
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
            104: (
                0,
                999,
                dateutil.parser.parse('2020-01-01T15:00:00+03:00'),
                999,
                dateutil.parser.parse('2020-01-01T15:00:00+03:00'),
                'modulbank',
                'PARK-01',
                '00000000-0000-0000-0000-100000000001',
                True,
                False,
                'Account 2',
                'f0000000-0000-0000-0000-000000000004',
                'a0000000-0000-0000-0000-000000000001',
                None,
                False,
                decimal.Decimal('0.0000'),
                [],
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                dateutil.parser.parse('1970-01-01T03:00:00+03:00'),
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
            ),
        },
    }
