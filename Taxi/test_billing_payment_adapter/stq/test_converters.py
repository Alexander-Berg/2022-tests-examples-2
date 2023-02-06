import datetime as dt

import pytest

from billing_payment_adapter.stq import converters


@pytest.mark.parametrize(
    'invoice_created_at, use_trust_payment_id_since, '
    'trust_payment_id, purchase_token, expected',
    [
        pytest.param(
            dt.datetime(2021, 1, 1),
            dt.datetime(2021, 1, 1),
            'some_trust_payment_id',
            'some_purchase_token',
            'some_trust_payment_id',
            id='it should return trust_payment_id for new invoices',
        ),
        pytest.param(
            dt.datetime(2021, 1, 1),
            dt.datetime(2021, 1, 1, 0, 0, 1),
            'some_trust_payment_id',
            'some_purchase_token',
            'some_purchase_token',
            id='it should return purchase_token for old invoices',
        ),
    ],
)
@pytest.mark.nofilldb()
def test_get_payment_id(
        invoice_created_at,
        use_trust_payment_id_since,
        trust_payment_id,
        purchase_token,
        expected,
):
    actual = converters.get_payment_id(
        invoice_created_at=invoice_created_at,
        use_trust_payment_id_since=use_trust_payment_id_since,
        trust_payment_id=trust_payment_id,
        purchase_token=purchase_token,
    )
    assert actual == expected
