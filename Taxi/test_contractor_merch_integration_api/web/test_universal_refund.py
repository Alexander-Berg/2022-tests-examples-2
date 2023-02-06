import pytest

MAP_IDS_TO_ERRORS = {
    'd9d519e2-a637-43b5-aba4-ffe370204869': 'cannot_refund_more_than_paid',
    'f8fd201c-322b-4b98-a713-e73b0471b62a': 'invalid_currency',
    'bf3bb294-a9ae-49a4-9f09-e814e069a243': 'too_many_refunds',
    '4bc0a6d2-c53e-4886-906f-83b7a409ae2e': 'invalid_amount',
}

HEADERS = {
    'X-Client-Id': '........',
    'X-YaTaxi-API-Key': '........',
    'X-Idempotency-Token': '.......................',
}

DATA_FROM_CMIA = {'amount': '100', 'currency': 'RUB'}


def get_error_response(code: str, message: str):
    return {'code': code, 'message': message}


def refunds_handler_response(ids: list, canceled: bool, mobi_refund_id: int):
    return {
        'refunds': [
            {
                'id': x,
                'amount': '100',
                'currency': 'RUB',
                'created_at': '2021-11-12T12:00:00+00:00',
                'metadata': {
                    'mobi_refund_id': str(mobi_refund_id),
                    'is_cancel': canceled,
                },
            }
            for x in ids
        ],
    }


def get_request(payment_id: str):
    return {'payment_id': payment_id, 'amount': '100', 'refund_reason': 'Test'}


def get_cmp_error_response(payment_id: str):
    return {
        'code': MAP_IDS_TO_ERRORS[payment_id],
        'message': MAP_IDS_TO_ERRORS[payment_id],
    }


def get_cmia_response(payment_id: str):
    return {
        'amount': '100',
        'created_at': '2021-11-12T15:00:00+03:00',
        'refund_id': '33cc9480-65be-4a5e-8e56-836ba182c534',
    }


@pytest.mark.parametrize(
    'data_to_cmia,data_from_cmp,data_from_cmia,status',
    [
        (
            get_request('42cc9480-65be-4a5e-8e56-836ba182c534'),
            refunds_handler_response(
                ['33cc9480-65be-4a5e-8e56-836ba182c534'], False, 1,
            )['refunds'][0],
            get_cmia_response('42cc9480-65be-4a5e-8e56-836ba182c534'),
            200,
        ),
        (
            get_request('d9d519e2-a637-43b5-aba4-ffe370204869'),
            get_cmp_error_response('d9d519e2-a637-43b5-aba4-ffe370204869'),
            get_error_response(
                code='400', message='cannot_refund_more_than_paid',
            ),
            400,
        ),
        (
            get_request('f8fd201c-322b-4b98-a713-e73b0471b62a'),
            get_cmp_error_response('f8fd201c-322b-4b98-a713-e73b0471b62a'),
            get_error_response(code='400', message='invalid_currency'),
            400,
        ),
        (
            get_request('bf3bb294-a9ae-49a4-9f09-e814e069a243'),
            get_cmp_error_response('bf3bb294-a9ae-49a4-9f09-e814e069a243'),
            get_error_response(code='400', message='too_many_refunds'),
            400,
        ),
        (
            get_request('4bc0a6d2-c53e-4886-906f-83b7a409ae2e'),
            get_cmp_error_response('4bc0a6d2-c53e-4886-906f-83b7a409ae2e'),
            get_error_response(code='400', message='invalid_amount'),
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
            get_error_response(code='409', message='incorrect state'),
            get_error_response(
                code='409', message='Can\'t refund this payment right now',
            ),
            409,
        ),
        (get_request('34ceeee0-dd8c-4625-b80f-8fa416b90263'), None, None, 500),
    ],
)
async def test_refund(
        mockserver,
        mock_uapi_keys,
        taxi_contractor_merch_integration_api_web,
        data_to_cmia,
        data_from_cmp,
        data_from_cmia,
        status,
):
    @mock_uapi_keys('/v2/authorization')
    async def _handler_authorization(request):
        return mockserver.make_response(status=200, json={'key_id': '1630'})

    @mockserver.json_handler(
        '/contractor-merch-payments/internal/'
        'contractor-merch-payments/v1/payment/refund',
    )
    async def _refund_handler(request):
        assert request.json == DATA_FROM_CMIA
        payment_id = request.args.get('payment_id')
        if payment_id == '42cc9480-65be-4a5e-8e56-836ba182c534':
            return mockserver.make_response(status=200, json=data_from_cmp)
        if payment_id in MAP_IDS_TO_ERRORS.keys():
            return mockserver.make_response(status=400, json=data_from_cmp)
        if payment_id == 'bce26b92-24a1-4831-ad8b-1c47c419c289':
            return mockserver.make_response(status=404, json=data_from_cmp)
        if payment_id == 'a13eabc3-9361-4f24-b4e7-1848f27f27d0':
            return mockserver.make_response(status=409, json=data_from_cmp)
        if payment_id == '34ceeee0-dd8c-4625-b80f-8fa416b90263':
            return mockserver.make_response(status=500)

        return mockserver.make_response(status=404, json={})

    response = await taxi_contractor_merch_integration_api_web.post(
        path='/contractor-merchants/v1/external/v1/refund',
        json=data_to_cmia,
        headers=HEADERS,
    )
    assert response.status == status
    if status != 500:
        assert (await response.json()) == data_from_cmia
    if status == 200:
        assert (await response.json())[
            'refund_id'
        ] == '33cc9480-65be-4a5e-8e56-836ba182c534'
        assert data_to_cmia['amount'] == (await response.json())['amount']
        assert (await response.json())[
            'created_at'
        ] == '2021-11-12T15:00:00+03:00'
    if status == 400:
        assert (
            MAP_IDS_TO_ERRORS[data_to_cmia['payment_id']]
            == (await response.json())['message']
        )
