import aiohttp
import pytest


def convert_query_params_to_dict(query_params):
    return {
        param.split('=')[0]: param.split('=')[1]
        for param in query_params.split('&')
    }


PAYMENT_ID = '872321'
X_CLIENT_ID = 'washing_merchant'

DEFAULT_REQUEST_TO_CMIA = {
    'json': {'payment_id': PAYMENT_ID},
    'headers': {'X-Client-Id': X_CLIENT_ID, 'X-YaTaxi-API-Key': '........'},
}

DEFAULT_REQUEST_TO_CMP_CANCEL = {
    'params': {'payment_id': PAYMENT_ID, 'merchant_id': X_CLIENT_ID},
}

DEFAULT_RESPONSE_FROM_CMP_CANCEL = {'status_before': 'merchant_approved'}

RESPONSE_DATA_FROM_CMIA = ''

NOT_FOUND_RESPONSE_FROM_CMP_CANCEL = {
    'code': 'payment_not_found',
    'message': 'payment not found',
}

NOT_FOUND_RESPONSE_FROM_CMIA = NOT_FOUND_RESPONSE_FROM_CMP_CANCEL.copy()

CANNOT_CANCEL_RESPONSE_FROM_CMP_CANCEL = {
    'code': 'merchant_cannot_cancel',
    'message': 'merchant cannot cancel',
    'status_before': 'pending_payment_execution',
}

CANNOT_CANCEL_RESPONSE_FROM_CMIA = (
    CANNOT_CANCEL_RESPONSE_FROM_CMP_CANCEL.copy()
)
CANNOT_CANCEL_RESPONSE_FROM_CMIA.pop('status_before')


@pytest.mark.parametrize(
    'request_data_to_cmia,'
    'request_data_to_cmp_cancel,'
    'response_data_from_cmp_cancel,'
    'response_code_from_cmp_cancel,'
    'response_data_from_cmia,'
    'response_code_from_cmia,'
    'cancel_times_called',
    [
        pytest.param(
            DEFAULT_REQUEST_TO_CMIA,
            DEFAULT_REQUEST_TO_CMP_CANCEL,
            DEFAULT_RESPONSE_FROM_CMP_CANCEL,
            200,
            RESPONSE_DATA_FROM_CMIA,
            200,
            1,
        ),
        pytest.param(
            DEFAULT_REQUEST_TO_CMIA,
            DEFAULT_REQUEST_TO_CMP_CANCEL,
            NOT_FOUND_RESPONSE_FROM_CMP_CANCEL,
            404,
            NOT_FOUND_RESPONSE_FROM_CMIA,
            404,
            1,
        ),
        pytest.param(
            DEFAULT_REQUEST_TO_CMIA,
            DEFAULT_REQUEST_TO_CMP_CANCEL,
            CANNOT_CANCEL_RESPONSE_FROM_CMP_CANCEL,
            409,
            CANNOT_CANCEL_RESPONSE_FROM_CMIA,
            409,
            1,
        ),
    ],
)
async def test_cancel_universal_default(
        taxi_contractor_merch_integration_api_web,
        request_data_to_cmia,
        request_data_to_cmp_cancel,
        response_data_from_cmp_cancel,
        response_code_from_cmp_cancel,
        response_data_from_cmia,
        response_code_from_cmia,
        cancel_times_called,
        mock_contractor_merch_payments,
        mock_uapi_keys,
        mockserver,
):
    @mock_uapi_keys('/v2/authorization')
    async def _handler_authorization(request):
        return mockserver.make_response(status=200, json={'key_id': '1630'})

    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/cancel',
    )
    async def _handler_cancel(request):
        params = convert_query_params_to_dict(request.query_string.decode())
        assert params == request_data_to_cmp_cancel['params']
        return mockserver.make_response(
            status=response_code_from_cmp_cancel,
            json=response_data_from_cmp_cancel,
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
