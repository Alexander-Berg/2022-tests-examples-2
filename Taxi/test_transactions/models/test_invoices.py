import datetime as dt

import pytest

from transactions.generated.stq3 import stq_context
from transactions.internal import basket
from transactions.models import fields
from transactions.models import invoice_operations
from transactions.models import invoices
from transactions.models import wrappers


async def test_commit_processing_touches_updated(
        stq3_context: stq_context.Context,
):
    invoice_id = 'old-order'
    collection = stq3_context.transactions.invoices
    invoice = await collection.find_one({'_id': invoice_id})
    initial_updated = dt.datetime(2020, 1, 1)
    assert invoice['updated'] == initial_updated
    assert invoice['billing_tech']['refresh_attempts_count'] == 100500
    update = {'$set': {'billing_tech.refresh_attempts_count': 0}}
    invoice = await invoice_operations.commit_processing(
        invoice, update, stq3_context,
    )
    assert invoice['updated'] != initial_updated


@pytest.mark.now('2020-01-01T00:06:00')
@pytest.mark.parametrize(
    'values, expected',
    [
        ({'created': dt.datetime(2020, 1, 1)}, False),
        ({'created': dt.datetime(2020, 1, 1), 'ttl': 360}, False),
        (
            {'created': dt.datetime(2020, 1, 1), 'ttl': 359, 'status': 'init'},
            True,
        ),
        (
            {
                'created': dt.datetime(2020, 1, 1),
                'ttl': 359,
                'status': 'processing',
            },
            True,
        ),
        (
            {'created': dt.datetime(2020, 1, 1), 'ttl': 359, 'status': 'done'},
            False,
        ),
    ],
)
def test_is_expired_operation(values, expected):
    operation = invoices.Operation('operations', 0, values)
    assert invoices.is_expired_operation(operation) is expected


@pytest.mark.parametrize(
    'invoice_data, expected',
    [
        (
            {
                'invoice_request': {'operations': [{'status': 'obsolete'}]},
                'invoice_payment_tech': {
                    'items_by_payment_type': [],
                    'payments': [],
                },
            },
            False,
        ),
        (
            {
                'invoice_payment_tech': {
                    'items_by_payment_type': [],
                    'payments': [],
                },
                'invoice_request': {
                    'operations': [
                        {
                            'created': dt.datetime(2020, 1, 1),
                            'id': 'some_id',
                            'status': 'processing',
                            'ttl': 359,
                        },
                    ],
                },
                'billing_tech': {'transactions': [{'request_id': 'some_id'}]},
            },
            False,
        ),
        (
            {
                'invoice_payment_tech': {
                    'items_by_payment_type': [],
                    'payments': [],
                },
                'invoice_request': {
                    'operations': [
                        {
                            'created': dt.datetime(2020, 1, 1),
                            'id': 'some_id',
                            'status': 'processing',
                            'ttl': 359,
                        },
                    ],
                },
                'billing_tech': {
                    'transactions': [{'request_id': 'another_id'}],
                },
            },
            True,
        ),
        (
            {
                'invoice_payment_tech': {
                    'items_by_payment_type': [],
                    'payments': [],
                },
                'invoice_request': {
                    'operations': [
                        {
                            'created': dt.datetime(2020, 1, 1),
                            'id': 'some_id',
                            'status': 'processing',
                            'ttl': 359,
                        },
                    ],
                },
                'billing_tech': {
                    'transactions': [
                        {
                            'request_id': 'another_id',
                            'refunds': [{'request_id': 'some_id'}],
                        },
                    ],
                },
            },
            False,
        ),
    ],
)
@pytest.mark.now('2020-01-01T00:06:00')
def test_should_expire_operation(invoice_data, expected):
    invoice = wrappers.make_invoice(invoice_data, fields.TaxiOrderFields())
    assert invoices.should_expire_operation(invoice) is expected


@pytest.mark.parametrize(
    'service_orders, keys, expected',
    [
        pytest.param(
            {
                'first_item_id|first_merchant_id': 'first_order_id',
                'second_item_id': 'second_order_id',
            },
            {
                basket.Key('first_item_id', 'first_merchant_id'),
                basket.Key.from_item_id('second_item_id'),
                basket.Key.from_item_id('not_created_item_id'),
            },
            {basket.Key.from_item_id('not_created_item_id')},
            id='should return keys without created service_orders',
        ),
    ],
)
def test_select_keys_without_service_orders(service_orders, keys, expected):
    invoice_data = {
        'billing_tech': {'service_orders': service_orders},
        'invoice_payment_tech': {},
    }
    invoice = wrappers.make_invoice(invoice_data, fields.TaxiOrderFields())
    actual = invoice.select_keys_without_service_orders(keys)
    assert actual == expected
