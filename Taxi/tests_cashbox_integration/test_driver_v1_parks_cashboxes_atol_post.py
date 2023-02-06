import json

import pytest

from tests_cashbox_integration import utils

ENDPOINT = '/driver/cashbox/v1/parks/cashboxes'
PARK_ID = '123'

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

ATOL_CASHBOX = {
    'cashbox_type': 'atol_online',
    'tax_identification_number': '0123456789',
    'tax_scheme_type': 'simple',
    'login': 'super_park',
    'password': 'passw0rd',
    'group_code': 'super_park_group',
}


def pop_secrets(cashbox):
    res = {**cashbox}
    res.pop('login')
    res.pop('password')
    return res


@pytest.fixture(name='personal_tins_store')
def _personal_tins_store(mockserver):
    @mockserver.json_handler('/personal/v1/tins/store')
    async def mock_callback(request):
        return {
            'id': request.json['value'] + '_id',
            'value': request.json['value'],
        }

    return mock_callback


async def test_ok(
        taxi_cashbox_integration,
        pgsql,
        personal_tins_store,
        mockserver,
        fleet_parks,
):
    @mockserver.json_handler('cashbox-atol/api/partner/v1/integrationcheck')
    def _atol_validate_cashbox(request):
        return mockserver.make_response(status=200)

    response = await taxi_cashbox_integration.post(
        ENDPOINT, json={'cashbox': ATOL_CASHBOX}, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200, response.text
    assert personal_tins_store.times_called == 1
    response_body = response.json()
    response_id = response_body.pop('id', None)
    assert response_id is not None
    assert response_body == {
        'cashbox': pop_secrets(ATOL_CASHBOX),
        'park_id': PARK_ID,
        'cashbox_state': 'valid',
    }

    rows = utils.get_all_cashboxes(pgsql)
    assert len(rows) == 1
    assert rows[0].pop('date_created', None) is not None
    assert rows[0].pop('date_updated', None) is not None
    assert rows[0] == {
        'id': response_id,
        'park_id': PARK_ID,
        'idempotency_token': '100500',
        'state': 'valid',
        'is_current': False,
        'cashbox_type': 'atol_online',
        'details': {
            'tin_pd_id': '0123456789_id',
            'tax_scheme_type': 'simple',
            'group_code': 'super_park_group',
        },
        'secrets': {
            'login': 'M5a7svvcrnA7E5axBDY2sw==',
            'password': 'dCKumeJhRuUkLWmKppFyPQ==',
        },
    }


@pytest.mark.pgsql(
    'cashbox_integration',
    queries=[
        'INSERT INTO cashbox_integration.cashboxes '
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\',\'{}\','
        '       \'{}\',\'{}\',\'{}\',\'{}\',\'{}\')'.format(
            PARK_ID,
            'abc123',
            '100500',
            '2016-06-22 19:10:25-07',
            '2016-06-22 19:10:25-07',
            'valid',
            False,
            'atol_online',
            json.dumps(
                {
                    'tin_pd_id': '0123456789',
                    'tax_scheme_type': 'simple',
                    'group_code': 'super_park_group',
                },
            ),
            json.dumps({'login': 'super_park', 'password': 'passw0rd'}),
        ),
    ],
)
async def test_retry(
        taxi_cashbox_integration,
        pgsql,
        personal_tins_store,
        mockserver,
        fleet_parks,
):
    @mockserver.json_handler('cashbox-atol/api/partner/v1/integrationcheck')
    def _atol_validate_cashbox(request):
        return mockserver.make_response(status=200)

    rows_before = utils.get_all_cashboxes(pgsql)

    response = await taxi_cashbox_integration.post(
        ENDPOINT, json={'cashbox': ATOL_CASHBOX}, headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert personal_tins_store.times_called == 1
    response_body = response.json()
    response_id = response_body.pop('id', None)
    assert response_id == 'abc123'
    assert response_body == {
        'cashbox': pop_secrets(ATOL_CASHBOX),
        'park_id': PARK_ID,
        'cashbox_state': 'valid',
    }

    rows_after = utils.get_all_cashboxes(pgsql)
    assert rows_before == rows_after


@pytest.mark.parametrize('tin', ['01234567891', 'abcdabcdabcd'])
async def test_invalid_tin(
        taxi_cashbox_integration, personal_tins_store, tin, fleet_parks,
):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        json={'cashbox': {**ATOL_CASHBOX, 'tax_identification_number': tin}},
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'
    assert personal_tins_store.times_called == 0


async def test_wrong_credentials(
        taxi_cashbox_integration,
        pgsql,
        personal_tins_store,
        mockserver,
        fleet_parks,
):
    @mockserver.json_handler('cashbox-atol/api/partner/v1/integrationcheck')
    def _atol_validate_cashbox(request):
        return mockserver.make_response(
            status=400,
            json={'status': 400, 'response': {'codes': ['wrong_credentials']}},
        )

    response = await taxi_cashbox_integration.post(
        ENDPOINT, json={'cashbox': ATOL_CASHBOX}, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'invalid_cashbox_data'


async def test_not_self_assigned(
        taxi_cashbox_integration,
        fleet_parks,
        pgsql,
        personal_tins_store,
        mockserver,
):
    authorized_headers = AUTHORIZED_HEADERS
    authorized_headers['X-YaTaxi-Park-Id'] = 'big_park'

    response = await taxi_cashbox_integration.post(
        ENDPOINT, json={'cashbox': ATOL_CASHBOX}, headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'
