import json

import pytest

ENDPOINT = '/driver/cashbox/v1/parks/cashboxes/list'
PARK_ID = 'park_123'
PARK_ID2 = 'park_456'
PARK_ID3 = 'park_124'

AUTHORIZED_HEADERS = {
    'Accept-Language': 'en-EN',
    'X-YaTaxi-Park-Id': PARK_ID,
    'X-YaTaxi-Driver-Profile-Id': 'driverSS',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
    'X-Idempotency-Token': '100500',
}

AUTHORIZED_HEADERS2 = {
    'Accept-Language': 'en-EN',
    'X-YaTaxi-Park-Id': PARK_ID2,
    'X-YaTaxi-Driver-Profile-Id': 'driverSS',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
    'X-Idempotency-Token': '100500',
}

AUTHORIZED_HEADERS3 = {
    'Accept-Language': 'en-EN',
    'X-YaTaxi-Park-Id': PARK_ID3,
    'X-YaTaxi-Driver-Profile-Id': 'driverSS',
    'X-Request-Application': 'taximeter',
    'X-Request-Application-Version': '9.07 (1234)',
    'X-Request-Version-Type': '',
    'X-Request-Platform': 'android',
    'User-Agent': 'Taximeter 9.07 (1234)',
    'X-Idempotency-Token': '100500',
}


@pytest.fixture(name='personal_tins_retrieve')
def _personal_tins_retrieve(mockserver):
    @mockserver.json_handler('/personal/v1/tins/retrieve')
    async def mock_callback(request):
        tin_id = request.json['id']
        return {'id': tin_id, 'value': tin_id[:-3]}

    return mock_callback


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        'INSERT INTO cashbox_integration.cashboxes '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\','
        '       \'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'.format(
            PARK_ID,
            'id_abc123',
            'idemp_100500',
            '2016-06-22 19:10:25-07',
            '2016-06-22 19:10:25-07',
            'valid',
            False,
            'atol_online',
            json.dumps(
                {
                    'tin_pd_id': '0123456789_id',
                    'tax_scheme_type': 'simple',
                    'group_code': 'super_park_group',
                },
            ),
            json.dumps(
                {
                    'login': 'M5a7svvcrnA7E5axBDY2sw==',
                    'password': 'dCKumeJhRuUkLWmKppFyPQ==',
                },
            ),
        ),
        'INSERT INTO cashbox_integration.cashboxes '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\','
        '       \'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'.format(
            PARK_ID,
            'id_abc456',
            'idemp_100000',
            '2016-06-22 19:10:25-07',
            '2016-06-22 19:10:25-07',
            'deleted',
            False,
            'atol_online',
            json.dumps(
                {
                    'tin_pd_id': '0123456789_id',
                    'tax_scheme_type': 'simple',
                    'group_code': 'super_park_group',
                },
            ),
            json.dumps(
                {
                    'login': 'M5a7svvcrnA7E5axBDY2sw==',
                    'password': 'dCKumeJhRuUkLWmKppFyPQ==',
                },
            ),
        ),
        'INSERT INTO cashbox_integration.cashboxes '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\','
        '       \'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'.format(
            PARK_ID3,
            'id_abc123',
            'idemp_100500',
            '2016-06-22 19:10:25-07',
            '2016-06-22 19:10:25-07',
            'valid',
            True,
            'atol_online',
            json.dumps(
                {
                    'tin_pd_id': '0123456789_id',
                    'tax_scheme_type': 'simple',
                    'group_code': 'super_park_group',
                },
            ),
            json.dumps(
                {
                    'login': 'M5a7svvcrnA7E5axBDY2sw==',
                    'password': 'dCKumeJhRuUkLWmKppFyPQ==',
                },
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'park_id, expected_response, tin_retrieve_times_called, '
    'authorized_headers',
    [
        (
            PARK_ID,
            {
                'cashboxes': [
                    {
                        'cashbox': {
                            'cashbox_type': 'atol_online',
                            'tax_identification_number': '0123456789',
                            'tax_scheme_type': 'simple',
                            'group_code': 'super_park_group',
                        },
                        'id': 'id_abc123',
                        'cashbox_state': 'valid',
                        'current': False,
                    },
                ],
            },
            1,
            AUTHORIZED_HEADERS,
        ),
        (
            PARK_ID3,
            {
                'cashboxes': [
                    {
                        'cashbox': {
                            'cashbox_type': 'atol_online',
                            'tax_identification_number': '0123456789',
                            'tax_scheme_type': 'simple',
                            'group_code': 'super_park_group',
                        },
                        'id': 'id_abc123',
                        'cashbox_state': 'valid',
                        'current': True,
                    },
                ],
            },
            1,
            AUTHORIZED_HEADERS3,
        ),
        ('park_456', {'cashboxes': []}, 0, AUTHORIZED_HEADERS2),
    ],
)
async def test_ok(
        taxi_cashbox_integration,
        fleet_parks,
        pgsql,
        personal_tins_retrieve,
        park_id,
        expected_response,
        tin_retrieve_times_called,
        authorized_headers,
):
    response = await taxi_cashbox_integration.get(
        ENDPOINT, headers=authorized_headers,
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response
    assert personal_tins_retrieve.times_called == tin_retrieve_times_called


async def test_not_self_assigned(
        taxi_cashbox_integration, fleet_parks, pgsql, personal_tins_retrieve,
):
    authorized_headers = AUTHORIZED_HEADERS
    authorized_headers['X-YaTaxi-Park-Id'] = 'big_park'

    response = await taxi_cashbox_integration.get(
        ENDPOINT, headers=authorized_headers,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'not_self_assigned'
