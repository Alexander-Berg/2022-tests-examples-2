import pytest

from contractor_merch_integration_api.utils import operation_class

FAILED_JSON_RESPONSE = {
    'signature': (
        '0a814d580c2f1b42c6008074609bf5576c17f1e0f9da81a8c182f77f07d54537'
    ),
    'result': -2,
    'resultDesc': 'transaction not found',
}

FULL_JSON_RESPONSE = {
    'signature': (
        'ef0155271afba620242ab4615f401591be967975b6dca2f1214d2f4076bf1d6c'
    ),
    'result': 0,
    'refundId': '8e496157-c676-4ea6-9473-f49d21e204b3',
    'refundTime': '2021-11-12T15:00:00+03:00',
    'refundAmount': '123.45',
    'resultDesc': 'success',  # Пока не поддерживаем валюты
    'refundCurrency': 643,
}

MAP_IDS_TO_ERRORS = {
    'd9d519e2-a637-43b5-aba4-ffe370204869': 'cannot_refund_more_than_paid',
    'f8fd201c-322b-4b98-a713-e73b0471b62a': 'invalid_currency',
    'bf3bb294-a9ae-49a4-9f09-e814e069a243': 'too_many_refunds',
    '4bc0a6d2-c53e-4886-906f-83b7a409ae2e': 'invalid_amount',
}


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


def get_mobi_request(
        mobi_transaction_id: int, mobi_refund_id: int, currency: int,
):
    json = {
        'operation': 'refund',
        'mmTranId': mobi_transaction_id,
        'mmRefundId': mobi_refund_id,
        'amount': '123.45',
        'currency': currency,
        'refundReason': 'refund_reason',
    }
    json['signature'] = operation_class.create_signature(
        secret_key='QWERTY12345', parameters=json,
    )
    return json


@pytest.mark.pgsql(
    'contractor_merch_integration_api', files=['refund_records.sql'],
)
@pytest.mark.parametrize(
    'data,result',
    [
        (
            get_mobi_request(1, 1, 643),
            operation_class.ResultType.SUCCESS,
            # everything OK + refunds 200 not refunded
        ),
        (
            get_mobi_request(15, 10, 643),
            operation_class.ResultType.SUM_FOR_REFUND_GREATER,
            # refund 400 sum greater
        ),
        (
            get_mobi_request(23, 23, 643),
            operation_class.ResultType.INCORRECT_CURRENCY,
            # refund 400 invalid currency
        ),
        (
            get_mobi_request(24, 24, 643),
            operation_class.ResultType.LIMIT_EXCEEDED,
            # refund 400 too many refunds
        ),
        (
            get_mobi_request(25, 25, 643),
            operation_class.ResultType.INTERNAL_ERROR,
            # refund 400 invalid amount
        ),
        (
            get_mobi_request(27, 27, 643),
            operation_class.ResultType.TRANSACTION_NOT_FOUND,
            # refund 404
        ),
        (
            get_mobi_request(28, 28, 643),
            operation_class.ResultType.INTERNAL_ERROR,
            # refund 409
        ),
        (
            get_mobi_request(20, 4, 643),
            operation_class.ResultType.INTERNAL_ERROR,
            # refund 500
        ),
        (
            get_mobi_request(500, 489, 643),
            operation_class.ResultType.TRANSACTION_NOT_FOUND,
            # bd notfound
        ),
        (
            get_mobi_request(123, 489, 100),
            operation_class.ResultType.INCORRECT_CURRENCY,
            # no currency CMIA
        ),
    ],
)
async def test_refund(
        mockserver, taxi_contractor_merch_integration_api_web, data, result,
):
    @mockserver.json_handler(
        '/contractor-merch-payments/internal/'
        'contractor-merch-payments/v1/payment/refund',
    )
    async def _refund_handler(request):
        payment_id = request.args.get('payment_id')
        if payment_id == 'ac4ba28c-7863-473e-951c-ccb3cc154a85':
            return mockserver.make_response(
                status=200,
                json=refunds_handler_response(
                    ['8e496157-c676-4ea6-9473-f49d21e204b3'], False, 1,
                )['refunds'][0],
            )
        if payment_id in MAP_IDS_TO_ERRORS.keys():
            return mockserver.make_response(
                status=400,
                json={
                    'code': MAP_IDS_TO_ERRORS[payment_id],
                    'message': MAP_IDS_TO_ERRORS[payment_id],
                },
            )
        if payment_id == 'bce26b92-24a1-4831-ad8b-1c47c419c289':
            return mockserver.make_response(
                status=404, json={'code': '404', 'message': 'not found'},
            )
        if payment_id == 'a13eabc3-9361-4f24-b4e7-1848f27f27d0':
            return mockserver.make_response(
                status=409, json={'code': '409', 'message': 'incorrect state'},
            )
        if payment_id == '34ceeee0-dd8c-4625-b80f-8fa416b90263':
            return mockserver.make_response(status=500)

        return mockserver.make_response(status=404, json={})

    response = await taxi_contractor_merch_integration_api_web.post(
        path='/contractor-merchants/v1/external/v1/operation', json=data,
    )
    assert response.status == 200
    if result == operation_class.ResultType.TRANSACTION_NOT_FOUND:
        assert await response.json() == FAILED_JSON_RESPONSE
    elif result == operation_class.ResultType.SUCCESS:
        assert await response.json() == FULL_JSON_RESPONSE
    assert (await response.json())['result'] == int(result)
