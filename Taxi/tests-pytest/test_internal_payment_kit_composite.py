import decimal

import pytest

from taxi.external import plus_wallet as plus_wallet_service
from taxi.internal.payment_kit import composite
from taxi.internal.payment_kit import payable as payable_module

_ONE_PAYMENT_METHOD = plus_wallet_service.PaymentSplit(
    elements=[
        plus_wallet_service.SplitElement(
            'card',
            'card-01',
            decimal.Decimal(100),
            'ride',
        ),
        plus_wallet_service.SplitElement(
            'card',
            'card-01',
            decimal.Decimal(10),
            'tips',
        )
    ],
    currency='RUB',
)
_EXPECTED_ONE = composite.Transactions(
    now=composite.Transaction(
        sum_to_pay={'ride': 1000000, 'tips': 100000},
        payment_method=payable_module.PaymentMethod(
            type='card',
            id='card-01',
        )
    ),
    next=None,
)

_TWO_PAYMENT_METHODS = plus_wallet_service.PaymentSplit(
    elements=[
        plus_wallet_service.SplitElement(
            'personal_wallet',
            'wallet_id/2',
            decimal.Decimal(100),
            'ride',
        ),
        plus_wallet_service.SplitElement(
            'card',
            'card-01',
            decimal.Decimal(50),
            'ride',
        ),
        plus_wallet_service.SplitElement(
            'card',
            'card-01',
            decimal.Decimal(15),
            'tips',
        )
    ],
    currency='RUB',
)

_EXPECTED_TWO = composite.Transactions(
    now=composite.Transaction(
        sum_to_pay={'ride': 1000000},
        payment_method=payable_module.PaymentMethod(
            type='personal_wallet',
            id='wallet_id/2',
        )
    ),
    next=composite.Transaction(
        sum_to_pay={'ride': 500000, 'tips': 150000},
        payment_method=payable_module.PaymentMethod(
            type='card',
            id='card-01',
        )
    ),
)


@pytest.mark.parametrize('split,expected', [
    (_ONE_PAYMENT_METHOD, _EXPECTED_ONE),
    (_TWO_PAYMENT_METHODS, _EXPECTED_TWO),
])
@pytest.mark.filldb(_fill=False)
def test_get_transactions(split, expected):
    assert composite.get_transactions(split) == expected
