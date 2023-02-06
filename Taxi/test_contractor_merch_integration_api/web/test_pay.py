import pytest

from contractor_merch_integration_api.utils import helpers_for_api
from contractor_merch_integration_api.utils import operation_class

PAYMENT_CMP = {
    'payment': {
        'status': 'pending_merchant_approve',
        'created_at': '2021-11-29T11:44:47.790779',
        'updated_at': '2021-11-29T13:44:47.790779',
        'contractor': {'park_id': '123', 'contractor_id': '18-92'},
        'price': '123.45',
    },
}

DEFAULT_REQUEST_FROM_MOBI = {
    'operation': 'pay',
    'barcode': '872321',
    'amount': '12397',
    'mmTranId': 478650,
    'mmTranTime': '2007-12-03T10:15:30+01:00',
    'product': '12345',
    'description': 'Пополнение номера 79998887768',
    'extra': {
        'brand_name': 'Лента',
        'city': 'Москва',
        'address': 'ул. Пушкина, д. Колотушкина',
    },
}
helpers_for_api.update_with_signature(DEFAULT_REQUEST_FROM_MOBI)
DEFAULT_RESPONSE_FROM_CMP = {
    'contractor': {'contractor_id': 'vasi*****ail.com', 'park_id': '456456'},
    'created_at': '2007-12-03T10:15:30+00:00',
}
DEFAULT_RESPONSE_TO_MOBI = {
    'result': operation_class.ResultType.ACCEPT_YANDEX.value,
    'yandex_transaction_id': '872321',
    'yandex_transaction_time': '2007-12-03T13:15:30+03:00',
    'client_login': '456456_vasi*****ail.com',
}
helpers_for_api.update_with_signature(DEFAULT_RESPONSE_TO_MOBI)

INCORRECT_SIGNATURE_REQUEST_FROM_MOBI = DEFAULT_REQUEST_FROM_MOBI.copy()
INCORRECT_SIGNATURE_REQUEST_FROM_MOBI.update({'signature': '123'})
INCORRECT_SIGNATURE_RESPONSE_FROM_MOBI = {
    'result': operation_class.ResultType.INCORRECT_SIGNATURE.value,
    'resultDesc': 'incorrect signature',
}
helpers_for_api.update_with_signature(INCORRECT_SIGNATURE_RESPONSE_FROM_MOBI)

DEFAULT_REQUEST_FROM_MOBI_WITH_CURRENCY = DEFAULT_REQUEST_FROM_MOBI.copy()
DEFAULT_REQUEST_FROM_MOBI_WITH_CURRENCY.update({'currency': 643})
helpers_for_api.update_with_signature(DEFAULT_REQUEST_FROM_MOBI_WITH_CURRENCY)

DEFAULT_REQUEST_TO_CMP_WITH_CURRENCY = {
    'currency': 'RUB',
    'merchant_id': helpers_for_api.MERCHANT_ID_MOBI,
    'price': DEFAULT_REQUEST_FROM_MOBI['amount'],
    'integrator': helpers_for_api.INTEGRATOR,
    'seller': {
        'address': 'Москва ул. Пушкина, д. Колотушкина',
        'name': 'Лента',
    },
}


@pytest.mark.parametrize(
    'request_from_mobi,'
    'response_to_mobi,'
    'request_to_cmp,'
    'response_from_cmp,'
    'expected_code',
    [
        pytest.param(
            DEFAULT_REQUEST_FROM_MOBI,
            DEFAULT_RESPONSE_TO_MOBI,
            None,
            DEFAULT_RESPONSE_FROM_CMP,
            200,
        ),
        pytest.param(
            INCORRECT_SIGNATURE_REQUEST_FROM_MOBI,
            INCORRECT_SIGNATURE_RESPONSE_FROM_MOBI,
            None,
            DEFAULT_RESPONSE_FROM_CMP,
            200,
        ),
        pytest.param(
            DEFAULT_REQUEST_FROM_MOBI_WITH_CURRENCY,
            DEFAULT_RESPONSE_TO_MOBI,
            DEFAULT_REQUEST_TO_CMP_WITH_CURRENCY,
            DEFAULT_RESPONSE_FROM_CMP,
            200,
        ),
    ],
)
async def test_pay_default(
        taxi_contractor_merch_integration_api_web,
        pgsql,
        load,
        request_from_mobi,
        response_to_mobi,
        request_to_cmp,
        response_from_cmp,
        expected_code,
        mock_contractor_merch_payments,
):
    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/price',
    )
    async def _handler_price(request):
        if request_to_cmp:
            assert request.json == request_to_cmp
        return response_from_cmp

    @mock_contractor_merch_payments(
        '/internal/v1/contractor-merch-payments/payment/status',
    )
    async def _handler_status(request):
        return PAYMENT_CMP

    response = await taxi_contractor_merch_integration_api_web.post(
        '/contractor-merchants/v1/external/v1/operation', request_from_mobi,
    )
    assert response.status == expected_code
    assert await response.json() == operation_class.convert_naming(
        response_to_mobi, False,
    )
    if request_from_mobi == DEFAULT_REQUEST_FROM_MOBI:
        with pgsql['contractor_merch_integration_api'].cursor() as cursor:
            cursor.execute(
                load('get_mobi_id_by_ya_id.sql'),
                (request_from_mobi['barcode'],),
            )
            result = list(row[0] for row in cursor)
            assert len(result) == 1
            assert result[0] == 478650


INCORRECT_CURRENCY_REQUEST_FROM_MOBI = DEFAULT_REQUEST_FROM_MOBI.copy()
INCORRECT_CURRENCY = 987
INCORRECT_CURRENCY_REQUEST_FROM_MOBI.update({'currency': INCORRECT_CURRENCY})
helpers_for_api.update_with_signature(INCORRECT_CURRENCY_REQUEST_FROM_MOBI)

INCORRECT_CURRENCY_RESPONSE_FROM_CMP = {
    'code': 'unsupported_currency',
    'message': 'Unsupported currency',
}

INCORRECT_CURRENCY_RESPONSE_TO_MOBI = {
    'result': operation_class.ResultType.INCORRECT_CURRENCY.value,
    'resultDesc': 'incorrect currency',
}
helpers_for_api.update_with_signature(INCORRECT_CURRENCY_RESPONSE_TO_MOBI)

BARCODE_NOT_FOUND_REQUEST_FROM_MOBI = DEFAULT_REQUEST_FROM_MOBI.copy()
BARCODE_NOT_EXIST = '000'
BARCODE_NOT_FOUND_REQUEST_FROM_MOBI.update({'barcode': BARCODE_NOT_EXIST})
helpers_for_api.update_with_signature(BARCODE_NOT_FOUND_REQUEST_FROM_MOBI)

BARCODE_NOT_FOUND_RESPONSE_FROM_CMP = {
    'code': 'barcode_not_found',
    'message': 'Barcode not found',
}

BARCODE_NOT_FOUND_RESPONSE_TO_MOBI = {
    'result': operation_class.ResultType.BARCODE_NOT_FOUND.value,
    'resultDesc': 'barcode not found',
}
helpers_for_api.update_with_signature(BARCODE_NOT_FOUND_RESPONSE_TO_MOBI)

TRANSACTION_TIME_LIMIT_EXCEEDED_REQUEST_FROM_MOBI = (
    DEFAULT_REQUEST_FROM_MOBI.copy()
)
BARCODE_TIME_LIMIT_EXCEEDED = '1337'
TRANSACTION_TIME_LIMIT_EXCEEDED_REQUEST_FROM_MOBI.update(
    {'barcode': BARCODE_TIME_LIMIT_EXCEEDED},
)
helpers_for_api.update_with_signature(
    TRANSACTION_TIME_LIMIT_EXCEEDED_REQUEST_FROM_MOBI,
)

TRANSACTION_TIME_LIMIT_EXCEEDED_RESPONSE_FROM_CMP = {
    'code': 'transaction_time_limit_exceeded',
    'message': 'Transaction time limit exceeded',
}

TRANSACTION_TIME_LIMIT_EXCEEDED_RESPONSE_TO_MOBI = {
    'result': operation_class.ResultType.ACCEPT_TIME_LIMIT_EXCEEDED.value,
    'resultDesc': 'accept time limit exceeded',
}
helpers_for_api.update_with_signature(
    TRANSACTION_TIME_LIMIT_EXCEEDED_RESPONSE_TO_MOBI,
)

INTERNAL_ERROR_REQUEST_FROM_MOBI = DEFAULT_REQUEST_FROM_MOBI.copy()
INTERNAL_ERROR_RESPONSE_TO_MOBI = {
    'result': operation_class.ResultType.INTERNAL_ERROR.value,
    'resultDesc': 'internal error',
}
helpers_for_api.update_with_signature(INTERNAL_ERROR_RESPONSE_TO_MOBI)


@pytest.mark.parametrize(
    'request_from_mobi,response_to_mobi,response_from_cmp,expected_code',
    [
        pytest.param(
            INCORRECT_CURRENCY_REQUEST_FROM_MOBI,
            INCORRECT_CURRENCY_RESPONSE_TO_MOBI,
            INCORRECT_CURRENCY_RESPONSE_FROM_CMP,
            200,
        ),
        pytest.param(
            BARCODE_NOT_FOUND_REQUEST_FROM_MOBI,
            BARCODE_NOT_FOUND_RESPONSE_TO_MOBI,
            BARCODE_NOT_FOUND_RESPONSE_FROM_CMP,
            200,
        ),
        pytest.param(
            TRANSACTION_TIME_LIMIT_EXCEEDED_REQUEST_FROM_MOBI,
            TRANSACTION_TIME_LIMIT_EXCEEDED_RESPONSE_TO_MOBI,
            TRANSACTION_TIME_LIMIT_EXCEEDED_RESPONSE_FROM_CMP,
            200,
        ),
        pytest.param(INTERNAL_ERROR_REQUEST_FROM_MOBI, None, None, 500),
    ],
)
async def test_pay_responses_from_cmp(
        taxi_contractor_merch_integration_api_web,
        request_from_mobi,
        expected_code,
        response_to_mobi,
        response_from_cmp,
        mock_contractor_merch_payments,
        mockserver,
):
    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/price',
    )
    async def _handler_price(request):
        payment_id = request.query_string.decode().split('=')[1]

        if request.json.get('currency') == str(INCORRECT_CURRENCY):
            return mockserver.make_response(json=response_from_cmp, status=400)
        if payment_id == BARCODE_NOT_EXIST:
            return mockserver.make_response(json=response_from_cmp, status=404)
        if payment_id == BARCODE_TIME_LIMIT_EXCEEDED:
            return mockserver.make_response(json=response_from_cmp, status=410)
        if not response_from_cmp:
            return mockserver.make_response(status=500)

    @mock_contractor_merch_payments(
        '/internal/v1/contractor-merch-payments/payment/status',
    )
    async def _handler_status(request):
        payment_id = request.query_string.decode().split('=')[1]
        if payment_id == BARCODE_NOT_EXIST:
            return mockserver.make_response(json=response_from_cmp, status=404)
        return PAYMENT_CMP

    response = await taxi_contractor_merch_integration_api_web.post(
        '/contractor-merchants/v1/external/v1/operation', request_from_mobi,
    )
    assert response.status == expected_code
    if response_to_mobi:
        assert await response.json() == operation_class.convert_naming(
            response_to_mobi, False,
        )


@pytest.mark.pgsql(
    'contractor_merch_integration_api', files=['insert_records.sql'],
)
@pytest.mark.parametrize(
    'request_from_mobi,'
    'response_to_mobi,'
    'response_from_cmp,'
    'expected_code',
    [
        pytest.param(
            DEFAULT_REQUEST_FROM_MOBI,
            INTERNAL_ERROR_RESPONSE_TO_MOBI,
            DEFAULT_RESPONSE_FROM_CMP,
            200,
        ),
    ],
)
async def test_pay_db_error(
        taxi_contractor_merch_integration_api_web,
        request_from_mobi,
        expected_code,
        response_to_mobi,
        response_from_cmp,
        mock_contractor_merch_payments,
):
    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/price',
    )
    async def _handler_price(request):
        return response_from_cmp

    @mock_contractor_merch_payments(
        '/internal/v1/contractor-merch-payments/payment/status',
    )
    async def _handler_status(request):
        return PAYMENT_CMP

    response = await taxi_contractor_merch_integration_api_web.post(
        '/contractor-merchants/v1/external/v1/operation', request_from_mobi,
    )
    assert response.status == expected_code
    assert await response.json() == operation_class.convert_naming(
        response_to_mobi, False,
    )


async def test_signature_with_extra_fields(
        taxi_contractor_merch_integration_api_web,
        mock_contractor_merch_payments,
):
    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/price',
    )
    async def _handler_price(request):
        return DEFAULT_RESPONSE_FROM_CMP

    @mock_contractor_merch_payments(
        '/internal/v1/contractor-merch-payments/payment/status',
    )
    async def _handler_status(request):
        return PAYMENT_CMP

    request_from_mobi_with_extra = {
        'operation': 'pay',
        'barcode': 'YANDEXPRO-4119e2d49f624792b880cda03de69518',
        'amount': '1.00',
        'currency': 643,
        'mmTranId': 309635907,
        'mmTranTime': '2022-02-16T12:35:26+03:00',
        'description': '1',
        'extra': {
            'store_id': '1',
            'address': 'Красная пл., дом 1',
            'trans_create_time': '2022-02-16T09:35:26Z',
            'city': 'Москва',
            'orderID': '9421',
            'trans_name': 'test_yandexpro',
            'brand_name': 'Магазин для sbp mirea',
            'sum': '1',
            'buyer_identity_code': (
                'YANDEXPRO-4119e2d49f624792b880cda03de69518'  # noqa: E501
            ),
        },
        'signature': '30fef74297f7dd6a6c9516e7783d17837dec9af54480a1d7b1308b564da33624',  # noqa: E501
    }

    response = await taxi_contractor_merch_integration_api_web.post(
        '/contractor-merchants/v1/external/v1/operation',
        request_from_mobi_with_extra,
    )
    assert response.status == 200
    assert (await response.json())['result'] == 1
