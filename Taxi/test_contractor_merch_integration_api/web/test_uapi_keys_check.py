import aiohttp
import pytest

PAYMENT_ID = '872321'
X_CLIENT_ID = 'washing_merchant'

DEFAULT_REQUEST_TO_CMIA = {
    'json': {'payment_id': PAYMENT_ID},
    'headers': {
        'X-Client-Id': X_CLIENT_ID,
        'X-YaTaxi-API-Key': 'ApiKeySecretK3kLol',
    },
}

DEFAULT_REQUEST_TO_UAPI_KEYS = {
    'headers': {
        'X-API-Key': DEFAULT_REQUEST_TO_CMIA['headers']['X-YaTaxi-API-Key'],
    },
    'json': {
        'consumer_id': 'contractor-merch-integration-api',
        'client_id': DEFAULT_REQUEST_TO_CMIA['headers']['X-Client-Id'],
        'entity_id': '',
        'permission_ids': '/some/handler',
    },
}

DEFAULT_RESPONSE_FROM_UAPI_KEYS = {'key_id': '1603'}

DEFAULT_RESPONSE_FROM_CMIA = ''

RESTRICTED_RESPONSE_FROM_UAPI_KEYS = {
    'code': 'restricted',
    'message': 'restricted',
}

RESTRICTED_RESPONSE_FROM_CMIA = {
    'code': 'access_restricted',
    'message': 'access restricted',
}


@pytest.mark.parametrize(
    'request_data_to_cmia,'
    'request_data_to_uapi_keys,'
    'response_data_from_uapi_keys,'
    'response_code_from_uapi_keys,'
    'response_data_from_cmia,'
    'response_code_from_cmia,'
    'cancel_times_called,'
    'uapi_keys_times_called',
    [
        pytest.param(
            DEFAULT_REQUEST_TO_CMIA,
            DEFAULT_REQUEST_TO_UAPI_KEYS,
            DEFAULT_RESPONSE_FROM_UAPI_KEYS,
            200,
            DEFAULT_RESPONSE_FROM_CMIA,
            200,
            1,
            1,
        ),
        pytest.param(
            DEFAULT_REQUEST_TO_CMIA,
            DEFAULT_REQUEST_TO_UAPI_KEYS,
            RESTRICTED_RESPONSE_FROM_UAPI_KEYS,
            403,
            RESTRICTED_RESPONSE_FROM_CMIA,
            403,
            0,
            1,
        ),
    ],
)
async def test_cancel_universal_default(
        taxi_contractor_merch_integration_api_web,
        request_data_to_cmia,
        request_data_to_uapi_keys,
        response_data_from_uapi_keys,
        response_code_from_uapi_keys,
        response_data_from_cmia,
        response_code_from_cmia,
        cancel_times_called,
        uapi_keys_times_called,
        mock_contractor_merch_payments,
        mock_uapi_keys,
        mockserver,
):
    @mock_uapi_keys('/v2/authorization')
    async def _handler_authorization(request):
        assert (
            request.json['client_id']
            == request_data_to_cmia['headers']['X-Client-Id']
        )
        assert (
            request.json['consumer_id'] == 'contractor-merch-integration-api'
        )
        assert request.json['entity_id'] == ''
        assert request.json['permission_ids'] == [
            '/contractor-merchants/v1/external/v1/cancel:POST',
        ]
        assert (
            request.headers['X-API-Key']
            == request_data_to_cmia['headers']['X-YaTaxi-API-Key']
        )
        return mockserver.make_response(
            status=response_code_from_uapi_keys,
            json=response_data_from_uapi_keys,
        )

    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/cancel',
    )
    async def _handler_cancel(request):
        return mockserver.make_response(
            status=200, json={'status_before': 'merchant_approved'},
        )

    response = await taxi_contractor_merch_integration_api_web.post(
        '/contractor-merchants/v1/external/v1/cancel', **request_data_to_cmia,
    )
    assert response.status == response_code_from_cmia
    try:
        assert await response.json() == response_data_from_cmia
    except aiohttp.client_exceptions.ContentTypeError:
        assert await response.text() == response_data_from_cmia

    assert _handler_cancel.times_called == cancel_times_called
    assert _handler_authorization.times_called == uapi_keys_times_called
