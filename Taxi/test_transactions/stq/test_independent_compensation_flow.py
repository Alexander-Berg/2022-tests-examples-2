# pylint: disable=protected-access,too-many-lines
import datetime as dt
import decimal
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from taxi.billing.util import rounding

from test_transactions import helpers
from transactions.stq import compensation_events_handler
from . import _state


_NOW_DATETIME = dt.datetime(2020, 1, 1, tzinfo=dt.timezone.utc)

PAYMENT_CARD = {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'}
IMPOSSIBLE_ACQUIRING_RATE = decimal.Decimal('0.999')
IMPOSSIBLE_NET_AMOUNT = decimal.Decimal('0.0001')


@pytest.mark.now(_NOW_DATETIME.isoformat())
@pytest.mark.config(TRANSACTIONS_SAVE_IS_HANDLED={'__default__': 1})
async def test_compensation_and_refund(
        stq3_context,
        mockserver,
        db,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        trust_clear_init_success,
        trust_clear_pending_success,
        trust_create_refund_success,
        mock_trust_start_refund,
        mock_check_refund,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
        personal_phones_store,
        personal_emails_store,
        personal_tins_bulk_store,
        cardstorage_update_card,
        cardstorage_card,
):
    fill_service_orders_success(
        expect={'region_id': None, 'product_id': 'taxi_107819207_ride'},
    )
    trust_clear_init_success()
    mock_trust_start_refund(status='success', expect_headers={'X-Uid': '123'})
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    personal_phones_store()
    personal_emails_store()
    personal_tins_bulk_store()
    cardstorage_update_card()
    cardstorage_card()
    invoice_id = 'happy-composite'
    with stq.flushing():
        await _create_invoice(
            web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty

    mock_trust_create_basket('trust-compensation-basket-token')
    mock_trust_pay_basket(
        'trust-compensation-basket-token',
        payment_status='cleared',
        expect_headers={'X-Uid': '123'},
    )
    mock_trust_check_basket(
        purchase_token='trust-compensation-basket-token',
        payment_status='cleared',
        user_phone='+70001234567',
        user_email='vasya@example.com',
        orders=[],
        expect_headers={'X-Uid': '123'},
    )
    mock_trust_check_basket_full(
        purchase_token='trust-compensation-basket-token',
        payment_status='cleared',
        user_phone='+70001234567',
        user_email='vasya@example.com',
        orders=[
            {'fiscal_inn': 'none'},
            {},
            {'fiscal_inn': '12345'},
            {'fiscal_inn': '67890'},
        ],
        expect_headers={'X-Uid': '123'},
    )
    # Initiate compensation
    operation_id = 'compensate'
    with stq.flushing():
        callbacks = [
            {
                'payload': {'arbitrary': 'data'},
                'queue': 'callback_with_payload',
            },
            {'queue': 'callback_without_payload'},
        ]
        await _create_compensation(
            web_app_client,
            invoice_id,
            operation_id=operation_id,
            gross_amount=decimal.Decimal('150.0'),
            acquiring_rate=decimal.Decimal('0.02'),
            product_id='taxi_107819207_ride',
            callbacks=callbacks,
        )
        assert stq.transactions_compensation_events.times_called == 0
    state = _state._ExpectedState.empty(invoice_id)
    state.add_compensation_operation(
        operation_id=operation_id, status='processing',
    )
    state.add_compensation(
        status='compensation_init',
        refunds=[],
        terminal_id=None,
        owner_uid='123',
    )

    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[0].status = 'compensation_pending'
        state.is_handled = None
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[0].status = 'compensation_success'
        state.compensations[0].terminal_id = 12345
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        state.compensation_operations[-1].status = 'done'
        state.is_handled = True
        assert stq.order_payment_result.times_called == 1
        assert stq.order_payment_result.next_call() == {
            'args': [
                'happy-composite',
                'compensate',
                'done',
                'compensation_operation_finish',
            ],
            'eta': dt.datetime(1970, 1, 1, 0, 0),
            'id': (
                'happy-composite:compensate:done:compensation_operation_finish'
            ),
            'kwargs': {
                'created_at': {'$date': int(_NOW_DATETIME.timestamp() * 1000)},
                'log_extra': None,
                'transactions': [],
            },
            'queue': 'order_payment_result',
        }
        assert stq['callback_with_payload'].times_called == 1
        assert stq['callback_without_payload'].times_called == 1
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty

    mock_trust_create_basket('trust-refunded-compensation-basket-token')
    mock_trust_pay_basket(
        purchase_token='trust-refunded-compensation-basket-token',
        payment_status='refunded',
        expect_headers={'X-Uid': '123'},
    )
    mock_trust_check_basket(
        purchase_token='trust-refunded-compensation-basket-token',
        payment_status='refunded',
        user_phone='+70001234567',
        user_email='vasya@example.com',
        orders=[],
        expect_headers={'X-Uid': '123'},
    )
    mock_trust_check_basket_full(
        purchase_token='trust-refunded-compensation-basket-token',
        payment_status='refunded',
        user_phone='+70001234567',
        user_email='vasya@example.com',
        orders=[
            {'fiscal_inn': 'none'},
            {},
            {'fiscal_inn': '12345'},
            {'fiscal_inn': '67890'},
        ],
        expect_headers={'X-Uid': '123'},
    )
    personal_phones_store(http_status=500)
    personal_emails_store(http_status=500)
    personal_tins_bulk_store(http_status=500)
    # Initiate refunded compensation
    operation_id = 'refunded_compensation'
    with stq.flushing():
        await _create_compensation(
            web_app_client,
            invoice_id,
            operation_id=operation_id,
            gross_amount=decimal.Decimal('150.0'),
            acquiring_rate=decimal.Decimal('0.02'),
            product_id='taxi_107819207_ride',
        )
        assert stq.transactions_compensation_events.times_called == 0
    state.add_compensation_operation(
        operation_id=operation_id, status='processing',
    )
    state.add_compensation(
        status='compensation_init',
        refunds=[],
        terminal_id=None,
        owner_uid='123',
    )
    state.is_handled = False
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[1].status = 'compensation_pending'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[1].status = 'compensation_success'
        state.compensations[1].terminal_id = 12345
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        state.compensation_operations[-1].status = 'done'
        state.is_handled = True
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty

    await _check_compensation_fail(
        test_case_id='trust-failed-compensation-1',
        payment_status='canceled',
        invoice_id=invoice_id,
        operation_id='failed_compensation_1',
        state=state,
        stq3_context=stq3_context,
        db=db,
        stq=stq,
        mock_trust_create_basket=mock_trust_create_basket,
        mock_trust_pay_basket=mock_trust_pay_basket,
        web_app_client=web_app_client,
    )

    await _check_compensation_fail(
        test_case_id='trust-failed-compensation-not-authorized',
        payment_status='not_authorized',
        invoice_id=invoice_id,
        operation_id='failed_compensation_not_authorized',
        state=state,
        stq3_context=stq3_context,
        db=db,
        stq=stq,
        mock_trust_create_basket=mock_trust_create_basket,
        mock_trust_pay_basket=mock_trust_pay_basket,
        web_app_client=web_app_client,
    )

    mock_trust_create_basket('trust-failed-compensation-2')
    mock_trust_pay_basket(
        purchase_token='trust-failed-compensation-2',
        payment_status='cleared',
        expect_headers={'X-Uid': '123'},
    )
    mock_trust_check_basket(
        purchase_token='trust-failed-compensation-2',
        payment_status='canceled',
        expect_headers={'X-Uid': '123'},
    )
    mock_trust_check_basket_full(
        purchase_token='trust-failed-compensation-2',
        payment_status='canceled',
        expect_headers={'X-Uid': '123'},
    )
    # Initiate compensation that fails on checking basket
    operation_id = 'failed_compensation_2'
    with stq.flushing():
        await _create_compensation(
            web_app_client,
            invoice_id,
            operation_id=operation_id,
            gross_amount=decimal.Decimal('150.0'),
            acquiring_rate=decimal.Decimal('0.02'),
            product_id='taxi_107819207_ride',
        )
        assert stq.transactions_compensation_events.times_called == 0
    state.add_compensation_operation(
        operation_id=operation_id, status='processing',
    )
    state.add_compensation(
        status='compensation_init',
        refunds=[],
        terminal_id=None,
        owner_uid='123',
    )
    state.is_handled = False
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[-1].status = 'compensation_pending'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[-1].status = 'compensation_fail'
        state.compensations[-1].terminal_id = 12345
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensation_operations[-1].status = 'failed'
        state.is_handled = True
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty

    # Initiate compensation refund
    trust_create_refund_success(expect_headers={'X-Uid': '123'})
    mock_trust_start_refund(
        status='wait_for_notification', expect_headers={'X-Uid': '123'},
    )
    mock_check_refund(
        status='wait_for_notification', expect_headers={'X-Uid': '123'},
    )
    operation_id = 'refund_compensation'
    with stq.flushing():
        await _create_compensation_refund(
            web_app_client,
            invoice_id,
            operation_id=operation_id,
            trust_payment_id='trust-payment-id',
            net_amount=decimal.Decimal('147.0'),
            callbacks=callbacks,
        )
        assert stq.transactions_compensation_events.times_called == 0
    state.add_compensation_operation(
        operation_id=operation_id, status='processing',
    )
    state.compensations[0].add_refund(status='refund_pending')
    state.is_handled = False
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[0].refunds[0].status = 'refund_waiting'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[0].refunds[0].status = 'refund_waiting'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[0].refunds[0].status = 'refund_success'
        mock_check_refund(status='success', expect_headers={'X-Uid': '123'})
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensation_operations[-1].status = 'done'
        state.is_handled = True
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq['callback_with_payload'].times_called == 1
        assert stq['callback_without_payload'].times_called == 1
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty
    db_invoice = await _get_db_invoice(db, state.invoice_id)
    assert db_invoice['billing_tech']['version'] == 24


async def test_only_compensation(
        stq3_context,
        mockserver,
        db,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
):
    invoice_id = 'happy-composite'
    fill_service_orders_success(
        expect={'region_id': 225, 'product_id': 'taxi_100500_ride'},
    )
    mock_trust_create_basket('trust-compensation-basket-token')
    mock_trust_pay_basket(
        'trust-compensation-basket-token',
        payment_status='cleared',
        expect_headers={'X-Uid': '123'},
    )
    mock_trust_check_basket(
        purchase_token='trust-compensation-basket-token',
        payment_status='cleared',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-compensation-basket-token',
        payment_status='cleared',
    )
    with stq.flushing():
        await _create_invoice(
            web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty

    # Initiate compensation
    operation_id = 'compensate'
    with stq.flushing():
        await _create_compensation(
            web_app_client,
            invoice_id,
            operation_id=operation_id,
            gross_amount=decimal.Decimal('150.0'),
            acquiring_rate=decimal.Decimal('0.02'),
            product_id='taxi_100500_ride',
            region_id=225,
        )
        assert stq.transactions_compensation_events.times_called == 0
    state = _state._ExpectedState.empty(invoice_id)
    state.add_compensation_operation(
        operation_id=operation_id, status='processing',
    )
    state.add_compensation(
        status='compensation_init',
        refunds=[],
        terminal_id=None,
        owner_uid='123',
    )
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[-1].status = 'compensation_pending'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[-1].status = 'compensation_success'
        state.compensations[-1].terminal_id = 12345
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        state.compensation_operations[-1].status = 'done'
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty
    db_invoice = await _get_db_invoice(db, state.invoice_id)
    assert db_invoice['billing_tech']['version'] == 6


async def _check_compensation_fail(
        test_case_id,
        payment_status,
        invoice_id,
        operation_id,
        state,
        stq3_context,
        db,
        stq,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        web_app_client,
):
    mock_trust_create_basket(test_case_id)
    mock_trust_pay_basket(
        purchase_token=test_case_id, payment_status=payment_status,
    )
    # Initiate failed compensation
    with stq.flushing():
        await _create_compensation(
            web_app_client,
            invoice_id,
            operation_id=operation_id,
            gross_amount=decimal.Decimal('150.0'),
            acquiring_rate=decimal.Decimal('0.02'),
            product_id='taxi_107819207_ride',
        )
        assert stq.transactions_compensation_events.times_called == 0
    state.add_compensation_operation(
        operation_id=operation_id, status='processing',
    )
    state.add_compensation(
        status='compensation_init',
        refunds=[],
        terminal_id=None,
        owner_uid='123',
    )
    state.is_handled = False
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.compensations[-1].status = 'compensation_fail'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        state.compensation_operations[-1].status = 'failed'
        state.is_handled = True
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty


async def _check_state(db, web_app_client, state: _state._ExpectedState):
    invoice = await _get_invoice(web_app_client, state.invoice_id)
    state.check(invoice)
    db_invoice = await _get_db_invoice(db, state.invoice_id)
    state.check_db(db_invoice)
    state.check_db_is_handled(db_invoice)


def _assert_next_iter_planned(stq, invoice_id):
    assert stq.transactions_compensation_events.times_called == 1
    task = stq.transactions_compensation_events.next_call()
    assert task['id'] == invoice_id


def _assert_next_iter_not_planned(stq, invoice_id):
    assert stq.transactions_compensation_events.times_called == 0


async def _get_invoice(client, invoice_id):
    body = {'id': invoice_id}
    response = await client.post('/v2/invoice/retrieve', json=body)
    assert response.status == 200
    content = await response.json()
    return content


async def _get_db_invoice(db, invoice_id):
    return await db.orders.find_one({'_id': invoice_id})


async def _create_invoice(client, invoice_id, payments):
    response = await client.post(
        '/v2/invoice/create',
        json={
            'id': invoice_id,
            'invoice_due': '2019-05-01 03:00:00Z',
            'billing_service': 'card',
            'payments': payments,
            'currency': 'RUB',
            'yandex_uid': '123',
            'personal_phone_id': 'personal-id',
            'pass_params': {},
            'user_ip': '127.0.0.1',
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}


async def _create_compensation(
        client,
        invoice_id: str,
        operation_id: str,
        gross_amount: decimal.Decimal,
        acquiring_rate: decimal.Decimal,
        product_id: Optional[str] = None,
        region_id: Optional[int] = None,
        callbacks: Optional[List[dict]] = None,
):
    body: Dict[str, Any] = {
        'invoice_id': invoice_id,
        'operation_id': operation_id,
        'originator': 'processing',
        'gross_amount': str(gross_amount),
        'acquiring_rate': str(acquiring_rate),
    }
    if product_id is not None:
        body['product_id'] = product_id
    if region_id is not None:
        body['region_id'] = region_id
    if callbacks is not None:
        body['callbacks'] = callbacks
    response = await client.post('/v3/invoice/compensation/create', json=body)
    assert response.status == 200
    content = await response.json()
    expected_content = {
        'gross_amount': str(gross_amount),
        'net_amount': str(
            rounding.round_2(
                gross_amount * (decimal.Decimal(1) - acquiring_rate),
            ),
        ),
    }
    assert content == expected_content


async def _create_compensation_refund(
        client,
        invoice_id: str,
        operation_id: str,
        trust_payment_id: str,
        net_amount: decimal.Decimal,
        callbacks: Optional[List[dict]] = None,
):
    body: dict = {
        'invoice_id': invoice_id,
        'operation_id': operation_id,
        'originator': 'processing',
        'trust_payment_id': trust_payment_id,
        'net_amount': str(net_amount),
    }
    if callbacks is not None:
        body['callbacks'] = callbacks
    response = await client.post('/v3/invoice/compensation/refund', json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {}


def _select_compensation(db_invoice: dict, basket_id: str) -> dict:
    return [
        a_compensation
        for a_compensation in db_invoice['billing_tech']['compensations']
        if a_compensation['purchase_token'] == basket_id
    ][0]


async def _run_task(stq_context, invoice_id):
    await compensation_events_handler.task(
        stq_context,
        helpers.create_task_info(queue='transactions_compensation_events'),
        invoice_id,
    )
