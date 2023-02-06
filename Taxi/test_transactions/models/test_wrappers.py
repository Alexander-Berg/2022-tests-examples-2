import pytest

from transactions.generated.stq3 import stq_context
from transactions.models import wrappers


@pytest.mark.parametrize(
    'invoice_id, expected_num_operations',
    [('with-cashback-operations', 1), ('missing-cashback-operations', 0)],
)
async def test_cashback_operations(
        stq3_context: stq_context.Context, invoice_id, expected_num_operations,
):
    collection = stq3_context.transactions.invoices
    invoice = await collection.find_one({'_id': invoice_id})
    num_operations = len(wrappers.cashback_operations(invoice))
    assert num_operations == expected_num_operations


@pytest.mark.parametrize(
    'invoice_id, expected',
    [
        ('card-invoice', 'card'),
        ('applepay-invoice', 'applepay'),
        ('coop-invoice', 'card'),
        ('no-payment-tech-invoice', None),
    ],
)
async def test_get_default_transaction_payment_method_type(
        stq3_context: stq_context.Context, invoice_id: str, expected: str,
):
    collection = stq3_context.transactions.invoices
    invoice = await collection.find_one({'_id': invoice_id})
    actual = wrappers.get_default_transaction_payment_method_type(invoice)
    assert actual == expected


@pytest.mark.parametrize(
    'data, expected',
    [
        pytest.param(
            {'transaction_payload': {'some': 'payload'}},
            {'some': 'payload'},
            id='should return payload if transaction_payload is present',
        ),
        pytest.param(
            {},
            None,
            id='should return None if transaction_payload is missing',
        ),
    ],
)
def test_transaction_transaction_payload(data, expected):
    transaction = wrappers.Transaction(0, data)
    assert transaction.transaction_payload == expected
