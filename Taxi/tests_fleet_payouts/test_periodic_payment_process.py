import contextlib

import pytest

from tests_fleet_payouts.utils import pg
from tests_fleet_payouts.utils import xcmp


PAYMENT00_ORDER = {
    'kind': 'payment_order',
    'data': {
        'balance_id': '76000000',
        'payments': [
            {
                'clid': 'CLID00',
                'billing_contract_id': '800000',
                'billing_client_id': '30000000',
                'currency': 'RUB',
                'amount': xcmp.Decimal('9999.99'),
            },
            {
                'clid': 'CLID00',
                'billing_contract_id': '800001',
                'billing_client_id': '30000001',
                'currency': 'USD',
                'amount': xcmp.Decimal('1000.01'),
            },
            {
                'clid': 'CLID00',
                'billing_contract_id': '800002',
                'billing_client_id': '30000002',
                'currency': 'EUR',
                'amount': xcmp.Decimal('7777777777777777.77'),
            },
        ],
        'schema_version': 'v1',
    },
    'topic': 'taxi/payment_order/clid/CLID00',
    'external_ref': '76000000',
    'event_at': xcmp.Date('2020-03-21T15:10:00+03:00'),
}

PAYMENT01_ORDER = {
    'kind': 'payment_order',
    'data': {
        'balance_id': '76000000',
        'payments': [
            {
                'clid': 'CLID01',
                'billing_contract_id': '810000',
                'billing_client_id': '31000000',
                'currency': 'RUB',
                'amount': xcmp.Decimal('0.01'),
            },
        ],
        'schema_version': 'v1',
    },
    'topic': 'taxi/payment_order/clid/CLID01',
    'external_ref': '76000000',
    'event_at': xcmp.Date('2020-03-21T14:50:00+03:00'),
}

PAYMENT02_ORDER = {
    'kind': 'payment_order',
    'data': {
        'balance_id': '76000000',
        'payments': [
            {
                'clid': 'CLID02',
                'billing_contract_id': '820000',
                'billing_client_id': '32000000',
                'currency': 'RUB',
                'amount': xcmp.Decimal('0.01'),
            },
        ],
        'schema_version': 'v1',
    },
    'topic': 'taxi/payment_order/clid/CLID02',
    'external_ref': '76000000',
    'event_at': xcmp.Date('2020-03-21T14:40:00+03:00'),
}


def next_request(mock):
    request = mock.next_call()['request'].json
    with contextlib.suppress(TypeError, KeyError, AttributeError):
        request['orders'].sort(key=lambda x: x['topic'])
    return request


@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.pgsql('fleet_payouts', files=['payments.sql'])
async def test_queue(
        taxi_fleet_payouts, mock_doc_store, mock_process_async, pgsql,
):
    # Step 1

    initial_payments = pg.dump_payments(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-process')

    assert mock_process_async.times_called == 1
    assert next_request(mock_process_async) == {
        'orders': [PAYMENT01_ORDER, PAYMENT02_ORDER],
    }

    doc01 = mock_doc_store.by_pk(
        (PAYMENT01_ORDER['topic'], PAYMENT01_ORDER['external_ref']),
    )
    doc02 = mock_doc_store.by_pk(
        (PAYMENT02_ORDER['topic'], PAYMENT02_ORDER['external_ref']),
    )
    updated_payments = pg.dump_payments(pgsql)

    assert updated_payments == {
        **initial_payments,
        'PAYMENT01': {
            **initial_payments['PAYMENT01'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'status': 'pending',
            'doc_id': doc01['doc_id'],
        },
        'PAYMENT02': {
            **initial_payments['PAYMENT02'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'status': 'pending',
            'doc_id': doc02['doc_id'],
        },
    }

    # Step 2

    initial_payments = updated_payments

    await taxi_fleet_payouts.run_task('periodic-payment-process')

    assert mock_process_async.times_called == 1
    assert next_request(mock_process_async) == {'orders': [PAYMENT00_ORDER]}

    doc00 = mock_doc_store.by_pk(
        (PAYMENT00_ORDER['topic'], PAYMENT00_ORDER['external_ref']),
    )
    updated_payments = pg.dump_payments(pgsql)

    assert updated_payments == {
        **initial_payments,
        'PAYMENT00': {
            **initial_payments['PAYMENT00'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'status': 'pending',
            'doc_id': doc00['doc_id'],
        },
    }

    # Step 3

    initial_payments = updated_payments

    await taxi_fleet_payouts.run_task('periodic-payment-process')

    assert mock_process_async.times_called == 0

    updated_payments = pg.dump_payments(pgsql)

    assert updated_payments == initial_payments


@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.pgsql('fleet_payouts', files=['payments.sql'])
@pytest.mark.config(
    FLEET_PAYOUTS_PERIODIC_PAYMENT_PROCESS={
        'enable': False,
        'period': 1,
        'max_payments': 10,
        'max_batch_size': 2,
    },
)
async def test_queue_parallel(
        taxi_fleet_payouts, mock_doc_store, mock_process_async, pgsql,
):
    # Step 1

    expected_orders = [PAYMENT00_ORDER, PAYMENT01_ORDER, PAYMENT02_ORDER]
    expected_orders.sort(key=lambda x: x['topic'])

    initial_payments = pg.dump_payments(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-process')

    assert mock_process_async.times_called == 2

    orders = []
    orders.extend(next_request(mock_process_async)['orders'])
    orders.extend(next_request(mock_process_async)['orders'])
    orders.sort(key=lambda order: order['topic'])
    assert expected_orders == orders

    doc00 = mock_doc_store.by_pk(
        (PAYMENT00_ORDER['topic'], PAYMENT00_ORDER['external_ref']),
    )
    doc01 = mock_doc_store.by_pk(
        (PAYMENT01_ORDER['topic'], PAYMENT01_ORDER['external_ref']),
    )
    doc02 = mock_doc_store.by_pk(
        (PAYMENT02_ORDER['topic'], PAYMENT02_ORDER['external_ref']),
    )
    updated_payments = pg.dump_payments(pgsql)

    assert updated_payments == {
        **initial_payments,
        'PAYMENT00': {
            **initial_payments['PAYMENT00'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'status': 'pending',
            'doc_id': doc00['doc_id'],
        },
        'PAYMENT01': {
            **initial_payments['PAYMENT01'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'status': 'pending',
            'doc_id': doc01['doc_id'],
        },
        'PAYMENT02': {
            **initial_payments['PAYMENT02'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
            'status': 'pending',
            'doc_id': doc02['doc_id'],
        },
    }

    # Step 2

    initial_payments = updated_payments

    await taxi_fleet_payouts.run_task('periodic-payment-process')

    assert mock_process_async.times_called == 0

    updated_payments = pg.dump_payments(pgsql)

    assert updated_payments == initial_payments


@pytest.mark.now('2020-03-21T21:00:00+03:00')
@pytest.mark.pgsql('fleet_payouts', files=['payments.sql'])
async def test_skip_on_error(taxi_fleet_payouts, mockserver, pgsql):
    @mockserver.json_handler('/billing-orders/v2/process/async')
    def mock_process_async(request):
        return mockserver.make_response(status=500)

    initial_payments = pg.dump_payments(pgsql)

    await taxi_fleet_payouts.run_task('periodic-payment-process')

    assert mock_process_async.times_called >= 2
    while mock_process_async.times_called > 0:
        assert next_request(mock_process_async) == {
            'orders': [PAYMENT01_ORDER, PAYMENT02_ORDER],
        }

    updated_payments = pg.dump_payments(pgsql)

    assert updated_payments == {
        **initial_payments,
        'PAYMENT01': {
            **initial_payments['PAYMENT01'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
        },
        'PAYMENT02': {
            **initial_payments['PAYMENT02'],
            'updated_at': xcmp.Date('2020-03-21T21:00:00+03:00'),
        },
    }
