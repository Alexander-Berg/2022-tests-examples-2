import pytest
from services.transactions.transactions.internal import gateway_operations

from transactions.generated.stq3 import stq_context


@pytest.mark.config(
    TRANSACTIONS_TECHNICAL_ERROR_CODES_BY_CURRENCY={
        'RUB': {'authorization_reject': True, 'blacklisted': False},
    },
    TRANSACTIONS_TECHNICAL_ERROR_CODES_BY_TERMINAL={
        '123': {'declined_by_issuer': True, 'expired_card': False},
    },
    TRANSACTIONS_TECHNICAL_ERROR_CODES_DEFAULT={
        'authorization_reject': False,
        'blacklisted': True,
        'declined_by_issuer': False,
        'expired_card': True,
        'fail_3ds': False,
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.parametrize(
    'billing_response,is_technical_error',
    [
        (
            {'payment_resp_code': 'authorization_reject', 'currency': 'RUB'},
            True,
        ),
        ({'payment_resp_code': 'blacklisted', 'currency': 'RUB'}, False),
        (
            {'payment_resp_code': 'authorization_reject', 'currency': 'USD'},
            False,
        ),
        ({'payment_resp_code': 'blacklisted', 'currency': 'USD'}, True),
        (
            {
                'payment_resp_code': 'declined_by_issuer',
                'terminal': {'id': 123},
            },
            True,
        ),
        (
            {'payment_resp_code': 'expired_card', 'terminal': {'id': 123}},
            False,
        ),
        (
            {
                'payment_resp_code': 'declined_by_issuer',
                'terminal': {'id': 987},
            },
            False,
        ),
        ({'payment_resp_code': 'expired_card', 'terminal': {'id': 987}}, True),
        ({'payment_resp_code': 'fail_3ds'}, False),
        ({'payment_resp_code': 'random_tech_error'}, True),
    ],
)
async def test_transactions_technical_error(
        stq3_context: stq_context.Context,
        billing_response,
        is_technical_error,
):
    assert (
        gateway_operations.response_is_technical_error(
            billing_response, context=stq3_context,
        )
        == is_technical_error
    )
