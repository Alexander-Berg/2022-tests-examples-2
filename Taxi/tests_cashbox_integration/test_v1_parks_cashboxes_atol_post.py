import json

import pytest

from tests_cashbox_integration import utils

ENDPOINT = '/fleet/cashbox/v1/parks/cashboxes'

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
        taxi_cashbox_integration, pgsql, personal_tins_store, mockserver,
):
    @mockserver.json_handler('cashbox-atol/api/partner/v1/integrationcheck')
    def _atol_validate_cashbox(request):
        return mockserver.make_response(status=200)

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': '123'},
        json={'cashbox': ATOL_CASHBOX},
        headers={
            'X-Idempotency-Token': '100500',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-UID': '123',
        },
    )

    assert response.status_code == 200, response.text
    assert personal_tins_store.times_called == 1
    response_body = response.json()
    response_id = response_body.pop('id', None)
    assert response_id is not None
    assert response_body == {
        'cashbox': pop_secrets(ATOL_CASHBOX),
        'park_id': '123',
        'cashbox_state': 'valid',
    }

    rows = utils.get_all_cashboxes(pgsql)
    assert len(rows) == 1
    assert rows[0].pop('date_created', None) is not None
    assert rows[0].pop('date_updated', None) is not None
    assert rows[0] == {
        'id': response_id,
        'park_id': '123',
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
            '123',
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
        taxi_cashbox_integration, pgsql, personal_tins_store, mockserver,
):
    @mockserver.json_handler('cashbox-atol/api/partner/v1/integrationcheck')
    def _atol_validate_cashbox(request):
        return mockserver.make_response(status=200)

    rows_before = utils.get_all_cashboxes(pgsql)

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': '123'},
        json={'cashbox': ATOL_CASHBOX},
        headers={
            'X-Idempotency-Token': '100500',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-UID': '123',
        },
    )
    assert response.status_code == 200, response.text
    assert personal_tins_store.times_called == 1
    response_body = response.json()
    response_id = response_body.pop('id', None)
    assert response_id == 'abc123'
    assert response_body == {
        'cashbox': pop_secrets(ATOL_CASHBOX),
        'park_id': '123',
        'cashbox_state': 'valid',
    }

    rows_after = utils.get_all_cashboxes(pgsql)
    assert rows_before == rows_after


@pytest.mark.parametrize('tin', ['01234567891', 'abcdabcdabcd'])
async def test_invalid_tin(taxi_cashbox_integration, personal_tins_store, tin):
    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': '123'},
        json={'cashbox': {**ATOL_CASHBOX, 'tax_identification_number': tin}},
        headers={
            'X-Idempotency-Token': '100500',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-UID': '123',
        },
    )

    assert response.status_code == 400, response.text
    assert personal_tins_store.times_called == 0


async def test_wrong_credentials(
        taxi_cashbox_integration, pgsql, personal_tins_store, mockserver,
):
    @mockserver.json_handler('cashbox-atol/api/partner/v1/integrationcheck')
    def _atol_validate_cashbox(request):
        return mockserver.make_response(
            status=400,
            json={'status': 400, 'response': {'codes': ['wrong_credentials']}},
        )

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': '123'},
        json={'cashbox': ATOL_CASHBOX},
        headers={
            'X-Idempotency-Token': '100500',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-UID': '123',
        },
    )

    assert response.status_code == 400, response.text
    assert json.loads(response.text)['code'] == 'invalid_cashbox_data'
