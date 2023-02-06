import uuid

import pytest

from test_transactions import helpers
from transactions.stq import compensation_events_handler
from transactions.stq import events_handler


CONFIG_HOST = 'http://a.net'
CONFIG_BASE_URL = CONFIG_HOST + '/callback/'
CONFIG_PREFIX = '/callback/{invoice_id}'


@pytest.mark.config(
    TRANSACTIONS_TRUST_BACK_URL={
        'taxi': {'card': {'host': CONFIG_HOST, 'prefix': CONFIG_PREFIX}},
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_SEND_BACK_URL_TO_TRUST={'taxi': {'card': 'enabled'}},
)
async def test_happy_path(
        db,
        web_app_client,
        stq,
        stq3_context,
        mock_trust_successful_basket,
        mock_trust_successful_compensation,
        mock_trust_resize,
        fill_service_orders_success,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
        mock_experiments3,
):
    fill_service_orders_success(return_input_order_id=True)
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()

    # given fresh invoice with two merchants
    await _create_invoice(web_app_client, 'two-merchants-invoice-id')

    await _update_invoice(
        web_app_client,
        invoice_id='two-merchants-invoice-id',
        payment_items=_build_payment_items(
            item_id='ride',
            amount='100',
            product_id='first-product-id',
            merchant_id='first-merchant-id',
            merchant_order_id='first-alias-id',
            fiscal_receipt_info=_build_fiscal_receipt_info('nds_0'),
        ),
    )

    mock_trust_successful_basket(
        'trust-basket-token',
        expected_orders=[
            {
                'order_id': 'first-alias-id',
                'price': '100.00',
                'qty': '1',
                'fiscal_nds': 'nds_0',
                'fiscal_title': 'some fiscal title',
            },
        ],
        expected_back_url=(CONFIG_BASE_URL + 'two-merchants-invoice-id'),
    )
    await _handle_payments(stq, stq3_context, 'two-merchants-invoice-id')

    await _update_invoice(
        web_app_client,
        invoice_id='two-merchants-invoice-id',
        payment_items=_build_payment_items(
            item_id='ride',
            amount='200',
            product_id='second-product-id',
            merchant_id='second-merchant-id',
            merchant_order_id='second-alias-id',
            fiscal_receipt_info=_build_fiscal_receipt_info('nds_20'),
        ),
    )
    mock_trust_successful_basket(
        'trust-basket-token',
        expected_orders=[
            {
                'order_id': 'second-alias-id',
                'price': '200.00',
                'qty': '1',
                'fiscal_nds': 'nds_20',
                'fiscal_title': 'some fiscal title',
            },
        ],
        expected_back_url=(CONFIG_BASE_URL + 'two-merchants-invoice-id'),
    )

    await _compensate_invoice(
        web_app_client,
        'two-merchants-invoice-id',
        amount='50',
        product_id='second-product-id',
    )

    mock_trust_resize(
        purchase_token='trust-basket-token', service_order_id='first-alias-id',
    )
    # when we handle this invoice payments
    await _handle_payments(stq, stq3_context, 'two-merchants-invoice-id')

    # and when we handle this invoice compensations
    mock_trust_successful_compensation('compensation-basket-token')
    await _handle_compensations(stq, stq3_context, 'two-merchants-invoice-id')

    invoice = await _fetch_invoice(db, 'two-merchants-invoice-id')

    # then we will create two transactions
    transactions = invoice['billing_tech']['transactions']
    assert len(transactions) == 2

    # first transaction will be resized to zero
    assert transactions[0]['status'] == 'hold_success'
    assert transactions[0]['sum'] == {'ride': 0}
    assert transactions[0]['initial_sum'] == {'ride': 1000000}
    assert len(transactions[0]['resizes']) == 1

    # second transaction will be successful
    assert transactions[1]['status'] == 'hold_success'
    assert transactions[1]['sum'] == {'ride': 2000000}

    # we will create one compensation
    compensations = invoice['billing_tech']['compensations']
    assert len(compensations) == 1

    # this compensation will be successful
    assert compensations[0]['sum'] == {'ride': 500000}
    assert compensations[0]['status'] == 'compensation_success'

    # we will create two products for both merchants
    assert invoice['invoice_request']['products'] == {
        'ride|first-merchant-id': 'first-product-id',
        'ride|second-merchant-id': 'second-product-id',
    }

    # we will create two service orders for both merchants
    # and service order for compensation
    assert invoice['billing_tech']['service_orders'] == {
        'ride|first-merchant-id': 'first-alias-id',
        'ride|second-merchant-id': 'second-alias-id',
        'ride': 'alias-id-from-db',
    }


async def test_merchant_change_after_clear(
        db,
        web_app_client,
        stq,
        stq3_context,
        mock_trust_successful_basket,
        mock_trust_successful_clear,
        mock_trust_successful_refund,
        fill_service_orders_success,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
        mock_experiments3,
):
    fill_service_orders_success(return_input_order_id=True)
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()

    # given fresh invoice with two merchants
    await _create_invoice(web_app_client, 'two-merchants-invoice-id')

    await _update_invoice(
        web_app_client,
        invoice_id='two-merchants-invoice-id',
        payment_items=_build_payment_items(
            item_id='ride',
            amount='100',
            product_id='first-product-id',
            merchant_id='first-merchant-id',
            merchant_order_id='first-alias-id',
            fiscal_receipt_info=_build_fiscal_receipt_info('nds_0'),
        ),
    )

    mock_trust_successful_basket('trust-basket-token')
    await _handle_payments(stq, stq3_context, 'two-merchants-invoice-id')
    # and cleared transaction for first merchant
    await _clear_invoice(
        web_app_client, 'two-merchants-invoice-id', '2018-01-01T00:00+00:00',
    )
    mock_trust_successful_clear()
    await _handle_payments(stq, stq3_context, 'two-merchants-invoice-id')

    await _update_invoice(
        web_app_client,
        invoice_id='two-merchants-invoice-id',
        payment_items=_build_payment_items(
            item_id='ride',
            amount='200',
            product_id='second-product-id',
            merchant_id='second-merchant-id',
            merchant_order_id='second-alias-id',
            fiscal_receipt_info=_build_fiscal_receipt_info('nds_20'),
        ),
    )
    mock_trust_successful_refund()
    mock_trust_successful_basket('trust-basket-token')
    await _disable_clear(db, 'two-merchants-invoice-id')

    # when we handle this invoice payments
    await _handle_payments(stq, stq3_context, 'two-merchants-invoice-id')

    invoice = await _fetch_invoice(db, 'two-merchants-invoice-id')

    # then we will create two transactions
    transactions = invoice['billing_tech']['transactions']
    assert len(transactions) == 2

    # first transaction will be refunded
    assert transactions[0]['status'] == 'clear_success'
    assert transactions[0]['sum'] == {'ride': 1000000}
    assert len(transactions[0]['refunds']) == 1
    assert transactions[0]['refunds'][0]['status'] == 'refund_success'
    assert transactions[0]['refunds'][0]['sum'] == {'ride': 1000000}

    # second transaction will be successful
    assert transactions[1]['status'] == 'hold_success'
    assert transactions[1]['sum'] == {'ride': 2000000}

    # we will create two products for both merchants
    assert invoice['invoice_request']['products'] == {
        'ride|first-merchant-id': 'first-product-id',
        'ride|second-merchant-id': 'second-product-id',
    }

    # we will create two service orders for both merchants
    assert invoice['billing_tech']['service_orders'] == {
        'ride|first-merchant-id': 'first-alias-id',
        'ride|second-merchant-id': 'second-alias-id',
    }


async def _create_invoice(client, invoice_id):
    body = {
        'id': invoice_id,
        'invoice_due': '2019-05-01 03:00:00Z',
        'billing_service': 'card',
        'currency': 'RUB',
        'yandex_uid': '123',
        'payments': [],
        'personal_phone_id': 'personal-id',
        'pass_params': {},
        'user_ip': '127.0.0.1',
    }
    response = await client.post('/v2/invoice/create', json=body)
    assert response.status == 200


async def _update_invoice(client, invoice_id, payment_items):
    body = {
        'id': invoice_id,
        'items_by_payment_type': payment_items,
        'operation_id': uuid.uuid4().hex,
        'originator': 'processing',
        'yandex_uid': '123',
        'payments': [
            {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'},
        ],
    }
    response = await client.post('/v2/invoice/update', json=body)
    assert response.status == 200


async def _compensate_invoice(client, invoice_id, amount, product_id):
    body = {
        'invoice_id': invoice_id,
        'operation_id': uuid.uuid4().hex,
        'originator': 'processing',
        'gross_amount': amount,
        'acquiring_rate': '0',
        'product_id': product_id,
        'region_id': 666,
    }
    response = await client.post('/v3/invoice/compensation/create', json=body)
    assert response.status == 200


async def _handle_payments(stq, stq_context, invoice_id):
    for i in range(20):
        with stq.flushing():
            await _run_task(stq_context, invoice_id, 'transactions_events')
            if stq.transactions_events.times_called == 0:
                return
    raise ValueError(
        'Couldn\'t handle invoice payments in 20 iterations. '
        'Something is wrong. Look at the logs.',
    )


async def _handle_compensations(stq, stq_context, invoice_id):
    for i in range(20):
        with stq.flushing():
            await _run_compensation_task(
                stq_context, invoice_id, 'transactions_compensation_events',
            )
            if stq.transactions_compensation_events.times_called == 0:
                return
    raise ValueError(
        'Couldn\'t handle invoice compensations in 20 iterations. '
        'Something is wrong. Look at the logs.',
    )


async def _fetch_invoice(db, invoice_id):
    query = {'_id': invoice_id}
    invoice = await db.orders.find_one(query)
    return invoice


async def _run_task(stq_context, invoice_id, queue):
    await events_handler.task(
        stq_context, helpers.create_task_info(queue=queue), invoice_id,
    )


async def _run_compensation_task(stq_context, invoice_id, queue):
    await compensation_events_handler.task(
        stq_context, helpers.create_task_info(queue=queue), invoice_id,
    )


def _build_payment_items(
        item_id,
        amount,
        product_id,
        merchant_id,
        merchant_order_id,
        fiscal_receipt_info,
):
    return [
        {
            'payment_type': 'card',
            'items': [
                {
                    'item_id': item_id,
                    'amount': amount,
                    'product_id': product_id,
                    'merchant': {
                        'id': merchant_id,
                        'order_id': merchant_order_id,
                    },
                    'fiscal_receipt_info': fiscal_receipt_info,
                },
            ],
        },
    ]


def _build_fiscal_receipt_info(vat):
    return {'title': 'some fiscal title', 'vat': vat}


async def _clear_invoice(client, invoice_id, clear_eta):
    response = await client.post(
        '/invoice/clear', json={'id': invoice_id, 'clear_eta': clear_eta},
    )
    assert response.status == 200


async def _disable_clear(db, invoice_id):
    query = {'_id': invoice_id}
    update = {'$unset': {'invoice_payment_tech.clear_eta': True}}
    await db.orders.update_one(query, update)
