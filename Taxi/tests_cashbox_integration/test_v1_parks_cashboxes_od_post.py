import json

import pytest

from tests_cashbox_integration import utils

ENDPOINT = '/fleet/cashbox/v1/parks/cashboxes'


def pop_secrets(cashbox):
    res = {**cashbox}
    res.pop('signature_private_key')
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
        load_json,
):
    @mockserver.json_handler('cashbox-orange-data/api/v2/check')
    def _od_validate_cashbox(request):
        return mockserver.make_response(status=200)

    rsa = load_json('mock_rsa_keys.json')
    key = rsa['key']
    encoded_key = rsa['encoded_key']

    orange_data_cashbox = {
        'cashbox_type': 'orange_data',
        'tax_identification_number': '0123456789',
        'tax_scheme_type': 'simple',
        'signature_private_key': key,
    }

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': '123'},
        json={'cashbox': orange_data_cashbox},
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
        'cashbox': pop_secrets(orange_data_cashbox),
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
        'cashbox_type': orange_data_cashbox['cashbox_type'],
        'details': {
            'tin_pd_id': '0123456789_id',
            'tax_scheme_type': orange_data_cashbox['tax_scheme_type'],
        },
        'secrets': {'signature_private_key': encoded_key},
    }


@pytest.mark.pgsql('cashbox_integration', files=['test_retry.sql'])
async def test_retry(
        taxi_cashbox_integration,
        pgsql,
        personal_tins_store,
        mockserver,
        load_json,
):
    @mockserver.json_handler('cashbox-orange-data/api/v2/check')
    def _od_validate_cashbox(request):
        return mockserver.make_response(status=200)

    key = load_json('mock_rsa_keys.json')['key']
    orange_data_cashbox = {
        'cashbox_type': 'orange_data',
        'tax_identification_number': '0123456789',
        'tax_scheme_type': 'simple',
        'signature_private_key': key,
    }

    rows_before = utils.get_all_cashboxes(pgsql)

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': '123'},
        json={'cashbox': orange_data_cashbox},
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
        'cashbox': pop_secrets(orange_data_cashbox),
        'park_id': '123',
        'cashbox_state': 'valid',
    }

    rows_after = utils.get_all_cashboxes(pgsql)
    assert rows_before == rows_after


@pytest.mark.parametrize('tin', ['01234567891', 'abcdabcdabcd'])
async def test_invalid_tin(
        taxi_cashbox_integration, personal_tins_store, tin, load_json,
):
    key = load_json('mock_rsa_keys.json')['key']
    orange_data_cashbox = {
        'cashbox_type': 'orange_data',
        'tax_identification_number': '0123456789',
        'tax_scheme_type': 'simple',
        'signature_private_key': key,
    }

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': '123'},
        json={
            'cashbox': {
                **orange_data_cashbox,
                'tax_identification_number': tin,
            },
        },
        headers={
            'X-Idempotency-Token': '100500',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-UID': '123',
        },
    )

    assert response.status_code == 400, response.text
    assert personal_tins_store.times_called == 0


async def test_wrong_credentials(
        taxi_cashbox_integration,
        pgsql,
        personal_tins_store,
        mockserver,
        load_json,
):
    @mockserver.json_handler('cashbox-orange-data/api/v2/check')
    def _od_validate_cashbox(request):
        return mockserver.make_response(status=400, json={'errors': []})

    key = load_json('mock_rsa_keys.json')['key']
    orange_data_cashbox = {
        'cashbox_type': 'orange_data',
        'tax_identification_number': '0123456789',
        'tax_scheme_type': 'simple',
        'signature_private_key': key,
    }

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': '123'},
        json={'cashbox': orange_data_cashbox},
        headers={
            'X-Idempotency-Token': '100500',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-UID': '123',
        },
    )

    assert response.status_code == 400, response.text
    assert json.loads(response.text)['code'] == 'invalid_cashbox_data'


async def test_invalid_key(
        taxi_cashbox_integration,
        pgsql,
        personal_tins_store,
        mockserver,
        load_json,
):
    orange_data_cashbox = {
        'cashbox_type': 'orange_data',
        'tax_identification_number': '0123456789',
        'tax_scheme_type': 'simple',
        'signature_private_key': '1',
    }

    response = await taxi_cashbox_integration.post(
        ENDPOINT,
        params={'park_id': '123'},
        json={'cashbox': orange_data_cashbox},
        headers={
            'X-Idempotency-Token': '100500',
            'X-Ya-User-Ticket-Provider': 'yandex',
            'X-Yandex-UID': '123',
        },
    )

    assert response.status_code == 400, response.text
    assert json.loads(response.text)['code'] == 'invalid_private_key'
