import copy
import enum
from typing import Any
from typing import Dict

import pytest

from contractor_merch_integration_api.utils import helpers_for_api


def convert_query_params_to_dict(query_params):
    return {
        param.split('=')[0]: param.split('=')[1]
        for param in query_params.split('&')
    }


class PaymentStatusCMP(enum.Enum):
    PENDING_MERCHANT_APPROVE: str = 'pending_merchant_approve'
    MERCHANT_APPROVED: str = 'merchant_approved'
    PENDING_PAYMENT_EXECUTION: str = 'pending_payment_execution'
    PAYMENT_PASSED: str = 'payment_passed'
    PAYMENT_FAILED: str = 'payment_failed'
    CONTRACTOR_DECLINED: str = 'contractor_declined'
    MERCHANT_CANCELED: str = 'merchant_canceled'
    PAYMENT_EXPIRED: str = 'payment_expired'


PAYMENT_ID = '872321'

DEFAULT_REQUEST_TO_CMIA = {
    'params': {'payment_id': PAYMENT_ID},
    'headers': {
        'X-Client-Id': 'washing_merchant',
        'X-YaTaxi-API-Key': '........',
    },
}

CONTRACTOR = {'park_id': '......', 'contractor_id': '......'}
MERCHANT = {
    'merchant_id': copy.deepcopy(
        DEFAULT_REQUEST_TO_CMIA['headers']['X-Client-Id'],
    ),
    'merchant_name': 'washing_merchant',
}

PAYMENT = {
    'status': PaymentStatusCMP.PAYMENT_PASSED.value,
    'contractor': CONTRACTOR,
    'created_at': '2021-12-21T16:41:47.786813+00:00',
    'updated_at': '2021-12-21T16:43:11.470543+00:00',
    'merchant': MERCHANT,
    'price': '123',
}

DEFAULT_REQUEST_TO_CMP_STATUS = {'params': {'payment_id': PAYMENT_ID}}
DEFAULT_RESPONSE_FROM_CMP_STATUS = {'payment': PAYMENT}
DEFAULT_REQUEST_TO_CMP_REFUNDS = {
    'params': {
        'payment_id': PAYMENT_ID,
        'merchant_id': helpers_for_api.LOYKA_MERCHANT_ID,
    },
}
DEFAULT_RESPONSE_FROM_CMP_REFUNDS: Dict[str, list] = {'refunds': []}
DEFAULT_RESPONSE_FROM_CMIA: Dict[str, Any] = {
    'payment_id': PAYMENT_ID,
    'price': PAYMENT['price'],
    'created_at': '2021-12-21T19:41:47.786813+03:00',  # local time
    'status': helpers_for_api.PAYMENT_STATUS_CMP_TO_EXTERNAL[
        PAYMENT['status']
    ],
}

NOT_FOUND_RESPONSE_FROM_CMP_STATUS = {
    'code': '404',
    'message': 'payment id not found',
}

PAYMENT_PENDING_RESPONSE_FROM_CMIA = {'status': 'payment_pending'}

INVALID_MERCHANT_RESPONSE_FROM_CMP_STATUS: Dict = copy.deepcopy(
    DEFAULT_RESPONSE_FROM_CMP_STATUS,
)
INVALID_MERCHANT_RESPONSE_FROM_CMP_STATUS['payment']['merchant'][
    'merchant_name'
] = 'keking_online'

NOT_FOUND_RESPONSE_FROM_CMIA = NOT_FOUND_RESPONSE_FROM_CMP_STATUS.copy()

PAYMENT_WITHOUT_PRICE_RESPONSE_FROM_CMP = copy.deepcopy(
    DEFAULT_RESPONSE_FROM_CMP_STATUS,
)
PAYMENT_WITHOUT_PRICE_RESPONSE_FROM_CMP['payment'].pop('price')

WITH_REFUNDS_RESPONSE_FROM_CMP_REFUNDS = copy.deepcopy(
    DEFAULT_RESPONSE_FROM_CMP_REFUNDS,
)
WITH_REFUNDS_RESPONSE_FROM_CMP_REFUNDS['refunds'].append(
    {
        'id': '.....',
        'amount': '100',
        'currency': 'RUB',
        'created_at': '2021-12-21T16:43:11.470543+00:00',
    },
)

WITH_REFUNDS_RESPONSE_FROM_CMIA = copy.copy(DEFAULT_RESPONSE_FROM_CMIA)
WITH_REFUNDS_RESPONSE_FROM_CMIA['refunds'] = [
    {
        'refund_id': '.....',
        'amount': '100',
        'created_at': '2021-12-21T19:43:11.470543+03:00',
    },
]

NOT_FOUND_RESPONSE_FROM_CMP_REFUNDS = NOT_FOUND_RESPONSE_FROM_CMP_STATUS.copy()


@pytest.mark.parametrize(
    'request_data_to_cmia,'
    'request_data_to_cmp_status,'
    'response_data_from_cmp_status,'
    'response_code_from_cmp_status,'
    'request_data_to_cmp_refunds,'
    'response_data_from_cmp_refunds,'
    'response_code_from_cmp_refunds,'
    'response_data_from_cmia,'
    'response_code_from_cmia,'
    'status_times_called,'
    'refunds_times_called',
    [
        pytest.param(
            DEFAULT_REQUEST_TO_CMIA,
            DEFAULT_REQUEST_TO_CMP_STATUS,
            DEFAULT_RESPONSE_FROM_CMP_STATUS,
            200,
            DEFAULT_REQUEST_TO_CMP_REFUNDS,
            DEFAULT_RESPONSE_FROM_CMP_REFUNDS,
            200,
            DEFAULT_RESPONSE_FROM_CMIA,
            200,
            1,
            1,
        ),
        pytest.param(
            DEFAULT_REQUEST_TO_CMIA,
            DEFAULT_REQUEST_TO_CMP_STATUS,
            NOT_FOUND_RESPONSE_FROM_CMP_STATUS,
            404,
            None,
            None,
            None,
            PAYMENT_PENDING_RESPONSE_FROM_CMIA,
            200,
            1,
            0,
        ),
        pytest.param(
            DEFAULT_REQUEST_TO_CMIA,
            DEFAULT_REQUEST_TO_CMP_STATUS,
            DEFAULT_RESPONSE_FROM_CMP_STATUS,
            200,
            DEFAULT_REQUEST_TO_CMP_REFUNDS,
            WITH_REFUNDS_RESPONSE_FROM_CMP_REFUNDS,
            200,
            WITH_REFUNDS_RESPONSE_FROM_CMIA,
            200,
            1,
            1,
        ),
    ],
)
async def test_status_universal_default(
        taxi_contractor_merch_integration_api_web,
        request_data_to_cmia,
        request_data_to_cmp_status,
        response_data_from_cmp_status,
        response_code_from_cmp_status,
        request_data_to_cmp_refunds,
        response_data_from_cmp_refunds,
        response_code_from_cmp_refunds,
        response_data_from_cmia,
        response_code_from_cmia,
        status_times_called,
        refunds_times_called,
        mock_contractor_merch_payments,
        mock_uapi_keys,
        mockserver,
):
    @mock_uapi_keys('/v2/authorization')
    async def _handler_authorization(request):
        return mockserver.make_response(status=200, json={'key_id': '1630'})

    @mock_contractor_merch_payments(
        '/internal/v1/contractor-merch-payments/payment/status',
    )
    async def _handler_status(request):
        params = convert_query_params_to_dict(request.query_string.decode())
        assert (
            params['payment_id']
            == request_data_to_cmp_status['params']['payment_id']
        )
        return mockserver.make_response(
            status=response_code_from_cmp_status,
            json=response_data_from_cmp_status,
        )

    @mock_contractor_merch_payments(
        '/internal/contractor-merch-payments/v1/payment/refunds',
    )
    async def _handler_refunds(request):
        params = convert_query_params_to_dict(request.query_string.decode())
        assert (
            params['payment_id']
            == request_data_to_cmp_refunds['params']['payment_id']
        )
        assert (
            params['merchant_id']
            == request_data_to_cmp_refunds['params']['merchant_id']
        )
        return mockserver.make_response(
            status=response_code_from_cmp_refunds,
            json=response_data_from_cmp_refunds,
        )

    response = await taxi_contractor_merch_integration_api_web.get(
        '/contractor-merchants/v1/external/v1/status', **request_data_to_cmia,
    )
    assert response.status == response_code_from_cmia
    assert await response.json() == response_data_from_cmia

    assert _handler_status.times_called == status_times_called
    assert _handler_refunds.times_called == refunds_times_called
