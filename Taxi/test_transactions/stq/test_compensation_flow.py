# pylint: disable=protected-access,too-many-lines
import decimal
from typing import Any
from typing import Dict
from typing import Optional

from taxi.billing.util import rounding

from test_transactions import helpers
from transactions.stq import events_handler
from . import _state


PAYMENT_CARD = {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'}
IMPOSSIBLE_ACQUIRING_RATE = decimal.Decimal('0.999')
IMPOSSIBLE_NET_AMOUNT = decimal.Decimal('0.0001')


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
        expect={
            'region_id': None,
            'product_id': 'taxi_107819207_ride',
            'order_id': '<alias_id>',
        },
    )
    mock_trust_create_basket('trust-basket-token')
    mock_trust_pay_basket(
        'trust-basket-token',
        payment_status='started',
        expect_headers={'X-Uid': '123'},
    )
    mock_trust_check_basket(
        purchase_token='trust-basket-token',
        payment_status='authorized',
        expect_headers={'X-Uid': '123'},
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token',
        payment_status='authorized',
        expect_headers={'X-Uid': '123'},
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
    operation_id = 'charge'
    with stq.flushing():
        await _charge_card(web_app_client, invoice_id, operation_id)
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id

    # Charge card
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(payment_type='card', status='hold_init', refunds=[])
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.transactions[0].status = 'hold_pending'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.transactions[0].status = 'hold_success'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.operations[0].status = 'done'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 0
        await _check_state(db, web_app_client, state)
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
        await _create_compensation(
            web_app_client,
            invoice_id,
            operation_id=operation_id,
            gross_amount=decimal.Decimal('150.0'),
            acquiring_rate=decimal.Decimal('0.02'),
            product_id='taxi_107819207_ride',
        )
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.add_operation(operation_id=operation_id, status='processing')
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
        state.operations[1].status = 'done'
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
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.add_operation(operation_id=operation_id, status='processing')
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
        state.operations[2].status = 'done'
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
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.add_operation(operation_id=operation_id, status='processing')
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
        state.compensations[-1].status = 'compensation_fail'
        state.compensations[-1].terminal_id = 12345
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.operations[-1].status = 'failed'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty

    operation_id = 'change_uid'
    with stq.flushing():
        await _charge_card(
            web_app_client, invoice_id, operation_id, uid='12345',
        )
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.operations[-1].status = 'done'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 0
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
            net_amount='147.0',
        )
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.add_operation(operation_id=operation_id, status='processing')
    state.compensations[0].add_refund(status='refund_pending')
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
        state.operations[-1].status = 'done'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty
    await _check_mangled_fields(
        db,
        state.invoice_id,
        mangled_basket_id='trust-compensation-basket-token',
        not_mangled_basket_id='trust-refunded-compensation-basket-token',
    )
    db_invoice = await _get_db_invoice(db, state.invoice_id)
    assert db_invoice['billing_tech']['version'] == 28


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
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state = _state._ExpectedState.empty(invoice_id)
    state.add_operation(operation_id=operation_id, status='processing')
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
        state.operations[-1].status = 'done'
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty
    db_invoice = await _get_db_invoice(db, state.invoice_id)
    assert db_invoice['billing_tech']['version'] == 6


async def test_recreate_service_orders(
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
):
    invoice_id = 'happy-composite-with-saved-service-orders'
    orders_handler = fill_service_orders_success(
        expect={
            'region_id': 225,
            'product_id': 'taxi_100500_ride',
            'order_id': '<alias_id>',
        },
    )
    mock_trust_create_basket(
        'trust-compensation-basket-token',
        status='error',
        status_code='order_not_found',
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
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state = _state._ExpectedState.empty(invoice_id)
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    _assert_created_order(orders_handler)


def _assert_created_order(orders_handler):
    assert orders_handler.times_called == 2
    get_call = orders_handler.next_call()
    assert get_call['request'].method == 'GET'
    assert get_call['request'].path == '/trust-payments/v2/orders/<alias_id>'
    post_call = orders_handler.next_call()
    assert post_call['request'].method == 'POST'


async def test_refund_py2_compensation(
        stq3_context,
        mockserver,
        db,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        web_app_client,
        fill_service_orders_success,
        trust_create_refund_success,
        mock_trust_start_refund,
        mock_check_refund,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
):
    fill_service_orders_success(
        expect={'region_id': None, 'product_id': 'taxi_107819207_ride'},
    )
    trust_create_refund_success()
    mock_trust_start_refund(
        status='success', expect_headers={'X-Uid': '434129003'},
    )
    invoice_id = 'with-py2-compensations'
    with stq.flushing():
        await _create_invoice(
            web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty

    state = _state._ExpectedState.empty(invoice_id)
    state.add_compensation(
        status='compensation_success',
        refunds=[],
        terminal_id=None,
        owner_uid='434129003',
    )
    await _check_state(db, web_app_client, state)

    # Initiate compensation refund
    mock_trust_start_refund(
        status='wait_for_notification', expect_headers={'X-Uid': '434129003'},
    )
    mock_check_refund(
        status='wait_for_notification', expect_headers={'X-Uid': '434129003'},
    )
    operation_id = 'refund_compensation'
    with stq.flushing():
        await _create_compensation_refund(
            web_app_client,
            invoice_id,
            operation_id=operation_id,
            trust_payment_id='trust-payment-id-1',
            net_amount='191.0',
        )
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.add_operation(operation_id=operation_id, status='processing')
    state.compensations[0].add_refund(status='refund_pending')
    state.compensations[0].terminal_id = 123
    state.compensations[0].owner_uid = '434129003'
    mock_trust_check_basket(
        purchase_token='purchase-token-1',
        payment_status='authorized',
        terminal_id=123,
        uid='434129003',
        # ??
    )
    mock_trust_check_basket_full(
        purchase_token='purchase-token-1',
        payment_status='authorized',
        terminal_id=123,
        uid='434129003',
        # ??
    )
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
        mock_check_refund(
            status='success', expect_headers={'X-Uid': '434129003'},
        )
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
        state.operations[-1].status = 'done'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty


async def test_compensation_after_py2(
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
    mock_trust_create_basket('trust-compensation-basket-token')
    mock_trust_pay_basket(
        'trust-compensation-basket-token', payment_status='cleared',
    )
    mock_trust_check_basket(
        purchase_token='trust-compensation-basket-token',
        payment_status='cleared',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-compensation-basket-token',
        payment_status='cleared',
    )
    invoice_id = 'with-py2-compensations'
    with stq.flushing():
        await _create_invoice(
            web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty

    state = _state._ExpectedState.empty(invoice_id)
    state.add_compensation(
        status='compensation_success',
        refunds=[],
        terminal_id=None,
        owner_uid='434129003',
    )
    await _check_state(db, web_app_client, state)

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
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.add_operation(operation_id=operation_id, status='processing')
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
        state.operations[-1].status = 'done'
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty


async def test_invalid_requests(
        stq3_context,
        mockserver,
        db,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        web_app_client,
):
    invoice_id = 'happy-composite'
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
            gross_amount=decimal.Decimal('1.1'),
            acquiring_rate=decimal.Decimal('0.0'),
            product_id='taxi_100500_ride',
            region_id=225,
        )
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state = _state._ExpectedState.empty(invoice_id)
    state.add_operation(operation_id=operation_id, status='init')
    await _check_state(db, web_app_client, state)
    await _damage_compensation_request(
        db, invoice_id, operation_index=(len(state.operations) - 1),
    )
    state.operations[-1].status = 'failed'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty

    # Initiate compensation refund
    operation_id = 'refund_compensation'
    with stq.flushing():
        await _create_compensation_refund(
            web_app_client,
            invoice_id,
            operation_id=operation_id,
            trust_payment_id='trust-payment-id',
            net_amount='147.0',
        )
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.add_operation(operation_id=operation_id, status='init')
    await _check_state(db, web_app_client, state)
    await _damage_compensation_refund_request(
        db, invoice_id, operation_index=(len(state.operations) - 1),
    )
    state.operations[-1].status = 'failed'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    assert stq.is_empty


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
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.add_operation(operation_id=operation_id, status='processing')
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
        state.compensations[-1].status = 'compensation_fail'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(db, web_app_client, state)
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        state.operations[-1].status = 'failed'
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


async def _damage_compensation_request(
        db, invoice_id: str, operation_index: int,
):
    key = (
        f'invoice_request.operations.{operation_index}.compensation_request'
        f'.acquiring_rate'
    )
    await db.orders.update_one(
        {'_id': invoice_id},
        {
            '$currentDate': {'updated': True},
            '$set': {key: str(IMPOSSIBLE_ACQUIRING_RATE)},
        },
    )


async def _damage_compensation_refund_request(
        db, invoice_id: str, operation_index: int,
):
    key = (
        f'invoice_request.operations.{operation_index}.compensation_request'
        f'.net_amount'
    )
    await db.orders.update_one(
        {'_id': invoice_id},
        {
            '$currentDate': {'updated': True},
            '$set': {key: str(IMPOSSIBLE_NET_AMOUNT)},
        },
    )


def _assert_next_iter_planned(stq, invoice_id):
    assert stq.transactions_events.times_called == 1
    task = stq.transactions_events.next_call()
    assert task['id'] == invoice_id


def _assert_next_iter_not_planned(stq, invoice_id):
    assert stq.transactions_events.times_called == 0


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


async def _clear_invoice(client, invoice_id):
    response = await client.post(
        '/invoice/clear',
        json={'id': invoice_id, 'clear_eta': '2018-01-01T00:00:00'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}


async def _charge_card(client, invoice_id, operation_id, uid=None):
    await _update_invoice(
        client,
        invoice_id,
        operation_id=operation_id,
        payment_items=[
            {
                'payment_type': 'card',
                'items': [
                    {
                        'item_id': 'ride',
                        'amount': '900',
                        'product_id': 'taxi_107819207_ride',
                    },
                ],
            },
        ],
        uid=uid,
    )


async def _update_invoice(
        client,
        invoice_id,
        operation_id,
        payment_items,
        payments=None,
        uid=None,
):
    body = {
        'id': invoice_id,
        'operation_id': operation_id,
        'originator': 'processing',
        'yandex_uid': '123',
        'items_by_payment_type': payment_items,
    }
    if payments is not None:
        body['payments'] = payments
    if uid is not None:
        body['yandex_uid'] = uid
    response = await client.post('/v2/invoice/update', json=body)
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
    response = await client.post('/v2/invoice/compensation/create', json=body)
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
):
    body = {
        'invoice_id': invoice_id,
        'operation_id': operation_id,
        'originator': 'processing',
        'trust_payment_id': trust_payment_id,
        'net_amount': str(net_amount),
    }
    response = await client.post('/v2/invoice/compensation/refund', json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {}


async def _check_mangled_fields(
        db, invoice_id, mangled_basket_id, not_mangled_basket_id,
):
    db_invoice = await _get_db_invoice(db, invoice_id)
    mangled_compensation = _select_compensation(db_invoice, mangled_basket_id)
    assert mangled_compensation['billing_response'] == {
        'status': 'success',
        'purchase_token': mangled_basket_id,
        'payment_status': 'cleared',
        'terminal': {'id': 12345},
        'user_email': 'vasya@example.com',
        'user_email_pd_id': '4c3a6de6758742d0963496a9ac95663c',
        'user_phone': '+70001234567',
        'user_phone_pd_id': 'ef65e0f5b3274f7a9b8eb6bc7152b88f',
        'orders': [
            {'fiscal_inn': 'none'},
            {},
            {'fiscal_inn': '12345', 'fiscal_inn_pd_id': '0'},
            {'fiscal_inn': '67890', 'fiscal_inn_pd_id': '1'},
        ],
    }
    not_mangled_compensation = _select_compensation(
        db_invoice, not_mangled_basket_id,
    )
    assert not_mangled_compensation['billing_response'] == {
        'status': 'success',
        'purchase_token': not_mangled_basket_id,
        'payment_status': 'refunded',
        'terminal': {'id': 12345},
        'user_email': 'vasya@example.com',
        'user_phone': '+70001234567',
        'orders': [
            {'fiscal_inn': 'none'},
            {},
            {'fiscal_inn': '12345'},
            {'fiscal_inn': '67890'},
        ],
    }


def _select_compensation(db_invoice: dict, basket_id: str) -> dict:
    return [
        a_compensation
        for a_compensation in db_invoice['billing_tech']['compensations']
        if a_compensation['purchase_token'] == basket_id
    ][0]


async def _run_task(stq_context, invoice_id):
    await events_handler.task(
        stq_context,
        helpers.create_task_info(queue='transactions_events'),
        invoice_id,
    )
