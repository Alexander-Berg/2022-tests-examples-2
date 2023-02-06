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

CLOUD_KASSIR_DATA_CASHBOX = {
    'cashbox_type': 'cloud_kassir',
    'tax_identification_number': '0123456789',
    'tax_scheme_type': 'simple',
    'public_id': 'super_park',
    'api_secret': 'passw0rd',
}

CLOUD_KASSIR_DATA_CASHBOX_WRONG_PASS = {
    'cashbox_type': 'cloud_kassir',
    'tax_identification_number': '0123456789',
    'tax_scheme_type': 'simple',
    'public_id': 'super_park',
    'api_secret': '!passw0rd',
}

CLOUD_KASSIR_DATA_CASHBOX_WRONG_TIN = {
    'cashbox_type': 'cloud_kassir',
    'tax_identification_number': '0123456788',
    'tax_scheme_type': 'simple',
    'public_id': 'super_park',
    'api_secret': 'passw0rd',
}

CLOUD_KASSIR_DATA_CASHBOX_NOT_CONFIGURED = {
    'cashbox_type': 'cloud_kassir',
    'tax_identification_number': '0123456788',
    'tax_scheme_type': 'simple',
    'public_id': 'super_park',
    'api_secret': 'passw0rd2',
}


def pop_secrets(cashbox):
    res = {**cashbox}
    res.pop('public_id')
    res.pop('api_secret')
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
        fleet_parks,
        pgsql,
        personal_tins_store,
        cloud_kassir_service,
):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        json={'cashbox': CLOUD_KASSIR_DATA_CASHBOX},
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 200, response.text
    assert personal_tins_store.times_called == 1
    response_body = response.json()
    response_id = response_body.pop('id', None)
    assert response_id is not None
    assert response_body == {
        'cashbox': pop_secrets(CLOUD_KASSIR_DATA_CASHBOX),
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
        'cashbox_type': CLOUD_KASSIR_DATA_CASHBOX['cashbox_type'],
        'details': {
            'tin_pd_id': '0123456789_id',
            'tax_scheme_type': CLOUD_KASSIR_DATA_CASHBOX['tax_scheme_type'],
        },
        'secrets': {
            'public_id': 'M5a7svvcrnA7E5axBDY2sw==',
            'api_secret': 'dCKumeJhRuUkLWmKppFyPQ==',
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
            CLOUD_KASSIR_DATA_CASHBOX['cashbox_type'],
            json.dumps(
                {
                    'tin_pd_id': CLOUD_KASSIR_DATA_CASHBOX[
                        'tax_identification_number'
                    ],
                    'tax_scheme_type': CLOUD_KASSIR_DATA_CASHBOX[
                        'tax_scheme_type'
                    ],
                },
            ),
            json.dumps(
                {
                    'public_id': CLOUD_KASSIR_DATA_CASHBOX['public_id'],
                    'api_secret': CLOUD_KASSIR_DATA_CASHBOX['api_secret'],
                },
            ),
        ),
    ],
)
async def test_retry(
        taxi_cashbox_integration,
        fleet_parks,
        pgsql,
        personal_tins_store,
        cloud_kassir_service,
):
    rows_before = utils.get_all_cashboxes(pgsql)

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        json={'cashbox': CLOUD_KASSIR_DATA_CASHBOX},
        headers=AUTHORIZED_HEADERS,
    )
    assert response.status_code == 200, response.text
    assert personal_tins_store.times_called == 1
    response_body = response.json()
    response_id = response_body.pop('id', None)
    assert response_id == 'abc123'
    assert response_body == {
        'cashbox': pop_secrets(CLOUD_KASSIR_DATA_CASHBOX),
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
        json={
            'cashbox': {
                **CLOUD_KASSIR_DATA_CASHBOX,
                'tax_identification_number': tin,
            },
        },
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert personal_tins_store.times_called == 0


async def test_wrong_credentials(
        taxi_cashbox_integration,
        fleet_parks,
        pgsql,
        personal_tins_store,
        cloud_kassir_service,
):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        json={'cashbox': CLOUD_KASSIR_DATA_CASHBOX_WRONG_PASS},
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'invalid_cashbox_data'


async def test_wrong_tin(
        taxi_cashbox_integration,
        fleet_parks,
        pgsql,
        personal_tins_store,
        cloud_kassir_service,
):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        json={'cashbox': CLOUD_KASSIR_DATA_CASHBOX_WRONG_TIN},
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'invalid_cashbox_data'


async def test_not_configured(
        taxi_cashbox_integration,
        fleet_parks,
        pgsql,
        personal_tins_store,
        cloud_kassir_service,
):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        json={'cashbox': CLOUD_KASSIR_DATA_CASHBOX_NOT_CONFIGURED},
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == 'cashbox_not_configured'


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
        ENDPOINT,
        json={'cashbox': CLOUD_KASSIR_DATA_CASHBOX},
        headers=AUTHORIZED_HEADERS,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'
