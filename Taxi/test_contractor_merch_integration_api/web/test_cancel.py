import pytest

from contractor_merch_integration_api.utils import helpers_for_api
from contractor_merch_integration_api.utils import operation_class

DEFAULT_REQUEST_FROM_MOBI = {
    'operation': 'cancel',
    'mmTranId': 478650,
    'cancelReason': 'товар не получен',
}
helpers_for_api.update_with_signature(DEFAULT_REQUEST_FROM_MOBI)

DEFAULT_RESPONSE_FROM_CMP = {'status_before': 'pending_merchant_approve'}

DEFAULT_RESPONSE_TO_MOBI = {'result': 0, 'result_description': 'success'}
helpers_for_api.update_with_signature(DEFAULT_RESPONSE_TO_MOBI)

INCORRECT_SIGNATURE_REQUEST_FROM_MOBI = DEFAULT_REQUEST_FROM_MOBI.copy()
INCORRECT_SIGNATURE_REQUEST_FROM_MOBI.update({'signature': '123'})

INCORRECT_SIGNATURE_RESPONSE_TO_MOBI = {
    'result': -1,
    'result_description': 'incorrect signature',
}
helpers_for_api.update_with_signature(INCORRECT_SIGNATURE_RESPONSE_TO_MOBI)

TRANSACTION_NOT_FOUND_REQUEST_FROM_MOBI = DEFAULT_REQUEST_FROM_MOBI.copy()
TRANSACTION_NOT_FOUND_REQUEST_FROM_MOBI.update({'mmTranId': 123456})
helpers_for_api.update_with_signature(TRANSACTION_NOT_FOUND_REQUEST_FROM_MOBI)

OPERATION_NOT_FOUND_RESPONSE_TO_MOBI = {
    'result': -2,
    'result_description': 'transaction not found',
}
helpers_for_api.update_with_signature(OPERATION_NOT_FOUND_RESPONSE_TO_MOBI)


@pytest.mark.pgsql(
    'contractor_merch_integration_api', files=['insert_records.sql'],
)
@pytest.mark.parametrize(
    'request_from_mobi,response_to_mobi,response_from_cmp,mobi_code',
    [
        pytest.param(
            DEFAULT_REQUEST_FROM_MOBI,
            DEFAULT_RESPONSE_TO_MOBI,
            DEFAULT_RESPONSE_FROM_CMP,
            200,
        ),
    ],
)
async def test_cancel_default(
        taxi_contractor_merch_integration_api_web,
        request_from_mobi,
        response_to_mobi,
        response_from_cmp,
        mobi_code,
        mock_contractor_merch_payments,
):
    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/cancel',
    )
    async def _handler(request):
        return response_from_cmp

    response = await taxi_contractor_merch_integration_api_web.post(
        '/contractor-merchants/v1/external/v1/operation', request_from_mobi,
    )
    assert response.status == mobi_code
    assert await response.json() == operation_class.convert_naming(
        response_to_mobi, False,
    )


@pytest.mark.pgsql(
    'contractor_merch_integration_api', files=['insert_records.sql'],
)
@pytest.mark.parametrize(
    'request_from_mobi,response_to_mobi,response_from_cmp,mobi_code',
    [
        pytest.param(
            INCORRECT_SIGNATURE_REQUEST_FROM_MOBI,
            INCORRECT_SIGNATURE_RESPONSE_TO_MOBI,
            DEFAULT_RESPONSE_FROM_CMP,
            200,
        ),
        pytest.param(
            TRANSACTION_NOT_FOUND_REQUEST_FROM_MOBI,
            OPERATION_NOT_FOUND_RESPONSE_TO_MOBI,
            DEFAULT_RESPONSE_FROM_CMP,
            200,
        ),
    ],
)
async def test_cancel_logic_check_before_cmp(
        taxi_contractor_merch_integration_api_web,
        request_from_mobi,
        response_to_mobi,
        response_from_cmp,
        mobi_code,
):
    response = await taxi_contractor_merch_integration_api_web.post(
        '/contractor-merchants/v1/external/v1/operation', request_from_mobi,
    )
    assert response.status == mobi_code
    assert await response.json() == operation_class.convert_naming(
        response_to_mobi, False,
    )


BARCODE_NOT_FOUND_REQUEST_FROM_MOBI = DEFAULT_REQUEST_FROM_MOBI.copy()
BARCODE_NOT_FOUND_REQUEST_FROM_MOBI.update(
    {'cancelReason': 'barcode_not_found'},
)
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

INTERNAL_ERROR_REQUEST_FROM_MOBI = DEFAULT_REQUEST_FROM_MOBI.copy()
INTERNAL_ERROR_REQUEST_FROM_MOBI.update({'cancelReason': 'internal'})
helpers_for_api.update_with_signature(INTERNAL_ERROR_REQUEST_FROM_MOBI)
INTERNAL_ERROR_RESPONSE_TO_MOBI = {
    'result': operation_class.ResultType.INTERNAL_ERROR.value,
    'resultDesc': 'internal error',
}
helpers_for_api.update_with_signature(INTERNAL_ERROR_RESPONSE_TO_MOBI)


@pytest.mark.pgsql(
    'contractor_merch_integration_api', files=['insert_records.sql'],
)
@pytest.mark.parametrize(
    'request_from_mobi,response_to_mobi,response_from_cmp,mobi_code,cmp_code',
    [
        pytest.param(
            BARCODE_NOT_FOUND_REQUEST_FROM_MOBI,
            BARCODE_NOT_FOUND_RESPONSE_TO_MOBI,
            BARCODE_NOT_FOUND_RESPONSE_FROM_CMP,
            200,
            404,
        ),
        pytest.param(
            INTERNAL_ERROR_REQUEST_FROM_MOBI,
            INTERNAL_ERROR_RESPONSE_TO_MOBI,
            DEFAULT_RESPONSE_FROM_CMP,
            200,
            500,
        ),
    ],
)
async def test_cancel_cmp_requests(
        taxi_contractor_merch_integration_api_web,
        request_from_mobi,
        response_to_mobi,
        response_from_cmp,
        mobi_code,
        cmp_code,
        mock_contractor_merch_payments,
        mockserver,
):
    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/cancel',
    )
    async def _handler(request):
        return mockserver.make_response(
            json=response_from_cmp, status=cmp_code,
        )

    response = await taxi_contractor_merch_integration_api_web.post(
        '/contractor-merchants/v1/external/v1/operation', request_from_mobi,
    )
    assert response.status == mobi_code
    assert await response.json() == operation_class.convert_naming(
        response_to_mobi, False,
    )


TRANSACTION_CAN_BE_ONLY_REFUNDED_REQUEST_FROM_MOBI = (
    DEFAULT_REQUEST_FROM_MOBI.copy()
)  # noqa: E501
TRANSACTION_CAN_BE_ONLY_REFUNDED_REQUEST_FROM_MOBI.update(
    {'cancelReason': 'can not cancel only refund'},
)
helpers_for_api.update_with_signature(
    TRANSACTION_CAN_BE_ONLY_REFUNDED_REQUEST_FROM_MOBI,
)

TRANSACTION_CAN_BE_ONLY_REFUNDED_CANCEL_RESPONSE_FROM_CMP = {
    'code': '1234',
    'message': 'transaction can not be cancelled',
    'status_before': 'payment_passed',
}

TRANSACTION_CAN_BE_ONLY_REFUNDED_REFUND_RESPONSE_FROM_CMP_200 = {
    'id': '1234',
    'amount': '1234',
    'currency': 'RUB',
    'created_at': '1234',
}

TRANSACTION_CAN_BE_ONLY_REFUNDED_REFUND_RESPONSE_FROM_CMP_409 = {
    'code': '1234',
    'message': 'transaction can not be refunded',
}


@pytest.mark.pgsql(
    'contractor_merch_integration_api', files=['insert_records.sql'],
)
@pytest.mark.parametrize(
    'request_from_mobi,response_to_mobi,'
    'response_from_cmp_cannot_cancel,'
    'response_from_cmp_refund,mobi_code,cmp_code_refund',
    [
        pytest.param(
            TRANSACTION_CAN_BE_ONLY_REFUNDED_REQUEST_FROM_MOBI,
            DEFAULT_RESPONSE_TO_MOBI,
            TRANSACTION_CAN_BE_ONLY_REFUNDED_CANCEL_RESPONSE_FROM_CMP,
            TRANSACTION_CAN_BE_ONLY_REFUNDED_REFUND_RESPONSE_FROM_CMP_200,
            200,
            200,
        ),
        pytest.param(
            TRANSACTION_CAN_BE_ONLY_REFUNDED_REQUEST_FROM_MOBI,
            INTERNAL_ERROR_RESPONSE_TO_MOBI,
            TRANSACTION_CAN_BE_ONLY_REFUNDED_CANCEL_RESPONSE_FROM_CMP,
            TRANSACTION_CAN_BE_ONLY_REFUNDED_REFUND_RESPONSE_FROM_CMP_409,
            200,
            409,
        ),
    ],
)
async def test_cancel_cmp_requests_if_cannot_cancel(
        taxi_contractor_merch_integration_api_web,
        request_from_mobi,
        response_to_mobi,
        response_from_cmp_cannot_cancel,
        response_from_cmp_refund,
        mobi_code,
        cmp_code_refund,
        mock_contractor_merch_payments,
        mockserver,
):
    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/cancel',
    )
    async def _handler_cancel(request):
        return mockserver.make_response(
            json=response_from_cmp_cannot_cancel, status=409,
        )

    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/refund',
    )
    async def _handler_refund(request):
        return mockserver.make_response(
            status=cmp_code_refund, json=response_from_cmp_refund,
        )

    response = await taxi_contractor_merch_integration_api_web.post(
        '/contractor-merchants/v1/external/v1/operation', request_from_mobi,
    )
    assert response.status == mobi_code
    assert await response.json() == operation_class.convert_naming(
        response_to_mobi, False,
    )
