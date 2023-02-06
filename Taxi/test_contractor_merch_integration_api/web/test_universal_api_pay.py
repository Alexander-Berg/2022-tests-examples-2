import pytest

HEADERS = {
    'X-Client-Id': 'df099d2c-a344-4b7a-b232-d36fed0f3f7b',
    'X-YaTaxi-API-Key': '........',
}

PAY_HANDLER_RESPONSE = {
    'contractor': {'park_id': '111', 'contractor_id': '222'},
    'created_at': '2021-11-12T15:00:00+03:00',
}

DATA_FROM_CMIA = {
    'price': '100',
    'currency': 'RUB',
    'merchant_id': 'df099d2c-a344-4b7a-b232-d36fed0f3f7b',
    'integrator': 'integration-api-universal',
    'seller': {
        'address': 'Москва, улица Воздвиженка, д. 9 с. 2',
        'name': 'Keking Shop',
    },
    'external_id': 'Test',
}

STATUS_MAP = {
    '42cc9480-65be-4a5e-8e56-836ba182c534': 200,
    '9578876c-f3c5-4c74-b583-558b93cd05ed': 400,
    'bce26b92-24a1-4831-ad8b-1c47c419c289': 404,
    'a13eabc3-9361-4f24-b4e7-1848f27f27d0': 409,
    '34ceeee0-dd8c-4625-b80f-8fa416b90263': 410,
}


def get_error_response(code: str, message: str):
    return {'code': code, 'message': message}


def get_request(payment_id: str):
    return {
        'payment_id': payment_id,
        'price': '100',
        'external_payment_id': 'Test',
        'seller_name': 'Keking Shop',
        'seller_address': 'Москва, улица Воздвиженка, д. 9 с. 2',
    }


def get_cmia_response(payment_id: str):
    return {
        'price': '100',
        'created_at': '2021-11-12T15:00:00+03:00',
        'payment_id': '42cc9480-65be-4a5e-8e56-836ba182c534',
        'status': 'payment_pending',
    }


@pytest.mark.parametrize(
    'data_to_cmia,data_from_cmp,data_from_cmia,status',
    [
        (
            get_request('42cc9480-65be-4a5e-8e56-836ba182c534'),
            PAY_HANDLER_RESPONSE,
            get_cmia_response('42cc9480-65be-4a5e-8e56-836ba182c534'),
            200,
        ),
        # TODO: удалить тест после полной выкатки `price_limit_exceeded`
        (
            get_request('9578876c-f3c5-4c74-b583-558b93cd05ed'),
            get_error_response(
                code='price_limit_excceded', message='price_limit_excceded',
            ),
            get_error_response(code='400', message='Price limit exceeded'),
            400,
        ),
        (
            get_request('9578876c-f3c5-4c74-b583-558b93cd05ed'),
            get_error_response(
                code='price_limit_exceeded', message='price_limit_exceeded',
            ),
            get_error_response(code='400', message='Price limit exceeded'),
            400,
        ),
        (
            get_request('9578876c-f3c5-4c74-b583-558b93cd05ed'),
            get_error_response(code='400', message='unsupported_currency'),
            get_error_response(code='400', message='Some error occurred'),
            400,
        ),
        (
            get_request('bce26b92-24a1-4831-ad8b-1c47c419c289'),
            get_error_response(code='404', message='not found'),
            get_error_response(code='404', message='Transaction not found'),
            404,
        ),
        (
            get_request('a13eabc3-9361-4f24-b4e7-1848f27f27d0'),
            get_error_response(code='409', message='price already put'),
            get_error_response(code='409', message='Payment already started'),
            409,
        ),
        (
            get_request('a13eabc3-9361-4f24-b4e7-1848f27f27d0'),
            get_error_response(code='409', message='used_payment_id'),
            get_error_response(code='409', message='Payment already started'),
            409,
        ),
        (
            get_request('34ceeee0-dd8c-4625-b80f-8fa416b90263'),
            get_error_response(code='410', message='payment expired'),
            get_error_response(code='410', message='Payment expired'),
            410,
        ),
    ],
)
async def test_universal_pay(
        mockserver,
        taxi_contractor_merch_integration_api_web,
        data_to_cmia,
        data_from_cmp,
        data_from_cmia,
        status,
        mock_uapi_keys,
):
    @mock_uapi_keys('/v2/authorization')
    async def _handler_authorization(request):
        return mockserver.make_response(status=200, json={'key_id': '1630'})

    @mockserver.json_handler(
        '/contractor-merch-payments/internal/'
        'contractor-merch-payments/v1/payment/pay-async',
    )
    async def _price_handler(request):
        assert request.json == DATA_FROM_CMIA
        payment_id = request.args.get('payment_id')
        if payment_id in STATUS_MAP:
            return mockserver.make_response(
                status=STATUS_MAP[payment_id], json=data_from_cmp,
            )
        return mockserver.make_response(status=404, json={})

    response = await taxi_contractor_merch_integration_api_web.post(
        path='/contractor-merchants/v1/external/v1/pay',
        json=data_to_cmia,
        headers=HEADERS,
    )
    assert response.status == status
    if status != 500:
        assert (await response.json()) == data_from_cmia
