import base64
import hashlib
import hmac

import pytest

ENDPOINT = '/v1/driver/loyalty-status'
LOYALTY_ENDPOINT = '/loyalty/service/loyalty/v1/status/by-bank-driver-id'

SECDIST_SECRET_KEY = 'dGVzdF9zZWNyZXRfa2V5'


def get_encoded_api_key(api_key):
    return base64.b64encode(
        hmac.new(
            base64.b64decode(SECDIST_SECRET_KEY),
            msg=api_key.encode(),
            digestmod=hashlib.sha256,
        ).digest(),
    ).decode()


def build_params(bank_id, bank_driver_id):
    return {'bank_id': bank_id, 'bank_driver_id': bank_driver_id}


def build_headers(api_key):
    return {'X-API-Key': api_key}


def build_response(bank_id, bank_driver_id, loyalty_status):
    return {
        'bank_id': bank_id,
        'bank_driver_id': bank_driver_id,
        'loyalty': {'status': loyalty_status},
    }


def build_loyalty_response(status):
    return {'loyalty': {'status': status}}


OK_PARAMS = [
    ('tinkoff_test_api_key', 'tinkoff', 'bank_driver_id_1', 'silver'),
    ('tinkoff_test_api_key', 'tinkoff', 'bank_driver_id_2', 'none'),
]


@pytest.mark.parametrize(
    'api_key, bank_id, bank_driver_id, expected_status', OK_PARAMS,
)
async def test_ok(
        taxi_banks_integration_api,
        mockserver,
        taxi_config,
        api_key,
        bank_id,
        bank_driver_id,
        expected_status,
):
    taxi_config.set_values(
        dict(
            BANKS_INTEGRATION_API_KEYS={get_encoded_api_key(api_key): bank_id},
        ),
    )

    @mockserver.json_handler(LOYALTY_ENDPOINT)
    async def _mock_loyalty(request):
        return build_loyalty_response(expected_status)

    response = await taxi_banks_integration_api.get(
        ENDPOINT,
        params=build_params(bank_id, bank_driver_id),
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 200, response.text
    assert response.json() == build_response(
        bank_id, bank_driver_id, expected_status,
    )


FORBIDDEN_PARAMS = [
    ('invalid_api_key', 'tinkoff', 'bank_driver_id_1'),
    ('tinkoff_test_api_key', 'invalid_bank_id', 'bank_driver_id_1'),
]


@pytest.mark.parametrize('api_key, bank_id, bank_driver_id', FORBIDDEN_PARAMS)
async def test_forbidden(
        taxi_banks_integration_api,
        taxi_config,
        api_key,
        bank_id,
        bank_driver_id,
):
    response = await taxi_banks_integration_api.get(
        ENDPOINT,
        params=build_params(bank_id, bank_driver_id),
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 403, response.text
    assert response.json() == {
        'code': '403',
        'message': 'Invalid bank id or api key',
    }


NOT_FOUND_PARAMS = [
    ('tinkoff_test_api_key', 'tinkoff', 'invalid_bank_driver_id'),
]


@pytest.mark.parametrize('api_key, bank_id, bank_driver_id', NOT_FOUND_PARAMS)
async def test_not_found(
        taxi_banks_integration_api,
        mockserver,
        taxi_config,
        api_key,
        bank_id,
        bank_driver_id,
):
    taxi_config.set_values(
        dict(
            BANKS_INTEGRATION_API_KEYS={get_encoded_api_key(api_key): bank_id},
        ),
    )

    @mockserver.json_handler(LOYALTY_ENDPOINT)
    async def _mock_loyalty(request):
        return mockserver.make_response(
            json={'code': '404', 'message': 'Not found'}, status=404,
        )

    response = await taxi_banks_integration_api.get(
        ENDPOINT,
        params=build_params(bank_id, bank_driver_id),
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 404, response.text
    assert response.json() == {'code': '404', 'message': 'Driver not found'}


LOYALTY_ERROR_PARAMS = [
    ('tinkoff_test_api_key', 'tinkoff', 'some_bank_driver_id'),
]


@pytest.mark.parametrize('api_key, bank_id, bank_driver_id', NOT_FOUND_PARAMS)
async def test_loyalty_error(
        taxi_banks_integration_api,
        mockserver,
        taxi_config,
        api_key,
        bank_id,
        bank_driver_id,
):
    taxi_config.set_values(
        dict(
            BANKS_INTEGRATION_API_KEYS={get_encoded_api_key(api_key): bank_id},
        ),
    )

    @mockserver.json_handler(LOYALTY_ENDPOINT)
    async def _mock_loyalty(request):
        return mockserver.make_response(
            json={'code': 'bad_request', 'message': 'Bad request'}, status=400,
        )

    response = await taxi_banks_integration_api.get(
        ENDPOINT,
        params=build_params(bank_id, bank_driver_id),
        headers={'X-API-Key': api_key},
    )
    assert response.status_code == 500, response.text
    assert response.json() == {
        'code': '500',
        'message': 'Internal Server Error',
    }
