# pylint: disable=protected-access
# pylint: disable=too-many-lines
import pytest

from test_transactions import helpers
from transactions.models import const
from transactions.models import wrappers
from transactions.stq import events_handler
from . import _state


PAYMENT_CARD = {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'}
PAYMENT_WALLET = {
    'type': 'personal_wallet',
    'method': 'wallet_id/12345',
    'service': 'eda',
    'account': {'id': 'wallet_id/12345'},
}
PAYMENT_SBP = {'type': 'sbp', 'method': 'sbp_qr'}
FISCAL_RECEIPT_INFO = {
    'personal_tin_id': 'tin_pd_id',
    'vat': 'nds_20',
    'title': 'food delivery',
}


@pytest.mark.config(
    TRANSACTIONS_SAVE_IS_HANDLED={'__default__': 1},
    TRANSACTIONS_FETCH_EXPERIMENTS_FOR_INVOICE={'eda': {'food_payment': 1.0}},
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
    TRANSACTIONS_BILLING_SERVICE_TOKENS={
        'food_payment': {
            'billing_api_key': 'food_payment_c808ddc93ffec050bf0624a4d3f3707c',
            'billing_payments_service_id': 629,
            'cardstorage_service_type': 'eats',
        },
    },
)
@pytest.mark.parametrize(
    'use_psp',
    [
        pytest.param(False, id='invoice should be handled via trust'),
        pytest.param(True, id='invoice should be handled via psp'),
    ],
)
async def test_happy_path(
        use_psp,
        eda_stq3_context,
        load_py_json,
        mockserver,
        stq,
        now,
        mock_get_pass_params,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        mock_cardstorage_payment_methods,
        trust_clear_init_success,
        trust_clear_pending_success,
        trust_create_refund_success,
        mock_trust_start_refund,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
):
    _mock_experiments(mockserver, use_psp)

    _mock_all_payment_system_calls(
        use_psp=use_psp,
        load_py_json=load_py_json,
        mockserver=mockserver,
        fill_service_orders_success=fill_service_orders_success,
        mock_trust_check_basket=mock_trust_check_basket,
        mock_trust_check_basket_full=mock_trust_check_basket_full,
        mock_trust_create_basket=mock_trust_create_basket,
        mock_trust_pay_basket=mock_trust_pay_basket,
        mock_trust_start_refund=mock_trust_start_refund,
        personal_phones_retrieve=personal_phones_retrieve,
        personal_tins_bulk_retrieve=personal_tins_bulk_retrieve,
        trust_clear_init_success=trust_clear_init_success,
        trust_create_refund_success=trust_create_refund_success,
    )
    invoice_id = 'happy-composite'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client,
            invoice_id,
            payments=[PAYMENT_WALLET, PAYMENT_CARD],
        )
        assert stq.is_empty
    with stq.flushing():
        operation_id = await _charge_wallet_and_card(
            eda_web_app_client,
            invoice_id,
            transaction_payload={'some': 'payload'},
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id
    # Charge wallet & card
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(
        payment_type='personal_wallet', status='hold_init', refunds=[],
    )
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_pending'
        _assert_called_get_pass_params(mock_get_pass_params, eda_stq3_context)
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.add_transaction(
            payment_type='card', status='hold_init', refunds=[],
        )
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[1].status = 'hold_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[1].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[0].status = 'done'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.transactions_eda_events.times_called == 0
        await _check_state(eda_web_app_client, state)
    assert stq.is_empty

    # Clear invoice
    trust_clear_pending_success()
    _mock_psp_events(mockserver, load_py_json, 'payment_captured_events.json')

    with stq.flushing():
        await _clear_invoice(eda_web_app_client, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'clear_init'
        state.transactions[1].status = 'clear_init'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)

    if use_psp:
        state.transactions[0].status = 'clear_pending'
        with stq.flushing():
            await _run_task(eda_stq3_context, invoice_id)
            _assert_next_iter_planned(stq, invoice_id)
            await _check_state(eda_web_app_client, state)
            state.transactions[0].status = 'clear_success'
            state.transactions[1].status = 'clear_pending'

        with stq.flushing():
            await _run_task(eda_stq3_context, invoice_id)
            _assert_next_iter_planned(stq, invoice_id)
            await _check_state(eda_web_app_client, state)
            state.transactions[1].status = 'clear_success'

        with stq.flushing():
            await _run_task(eda_stq3_context, invoice_id)
            _assert_next_iter_planned(stq, invoice_id)
            await _check_state(eda_web_app_client, state)
        with stq.flushing():
            await _run_task(eda_stq3_context, invoice_id)
            _assert_next_iter_not_planned(stq, invoice_id)
            await _check_state(eda_web_app_client, state)

        return
    state.transactions[0].status = 'clear_pending'
    state.transactions[1].status = 'clear_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'clear_success'
        state.transactions[1].status = 'clear_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)

    # Refund card & wallet. We expect card to refund first and THEN wallet.
    state.add_operation(operation_id='composite-refund', status='init')
    with stq.flushing():
        await _refund_wallet_and_card(eda_web_app_client, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[1].status = 'processing'
        state.transactions[1].status = 'refund_pending'
        state.transactions[1].add_refund(status='refund_pending')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[1].status = 'clear_success'
        state.transactions[1].refunds[0].status = 'refund_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'refund_pending'
        state.transactions[0].add_refund(status='refund_pending')
        state.is_handled = False
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_called_get_pass_params(mock_get_pass_params, eda_stq3_context)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        await _check_is_handled(eda_stq3_context, state)
        state.transactions[0].status = 'clear_success'
        state.transactions[0].refunds[0].status = 'refund_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[1].status = 'done'
        state.is_handled = True
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        await _check_is_handled(eda_stq3_context, state)


def _mock_experiments(mockserver, use_psp):
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _experiments_handler(request):
        for arg in request.json['args']:
            if (
                    arg['name'] == 'payment_type'
                    and arg['value'] == 'card'
                    and use_psp
            ):
                return {
                    'items': [
                        {
                            'name': 'use_psp_in_transactions',
                            'value': {'enabled': True},
                        },
                    ],
                }
        return {'items': []}


def _mock_all_payment_system_calls(
        use_psp,
        load_py_json,
        mockserver,
        fill_service_orders_success,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_start_refund,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
        trust_clear_init_success,
        trust_create_refund_success,
):
    fill_service_orders_success()
    mock_trust_create_basket('trust-basket-token')
    mock_trust_pay_basket('trust-basket-token', payment_status='started')
    mock_trust_check_basket(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    trust_clear_init_success()
    trust_create_refund_success()
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    mock_trust_start_refund(status='success')
    if use_psp:
        _mock_psp_calls(mockserver, load_py_json)


def _mock_psp_calls(mockserver, load_py_json):
    @mockserver.json_handler('psp/intents')
    def _create_intent_handler(request):
        del request  # unused
        return mockserver.make_response(
            status=200, json=load_py_json('intent_created_response.json'),
        )

    _mock_psp_events(
        mockserver, load_py_json, 'payment_authorized_events.json',
    )

    @mockserver.json_handler('psp/capture-payment')
    def _capture_payment_handler(request):
        assert 'cash' in request.json['params']
        assert 'cart' in request.json['params']
        return mockserver.make_response(
            status=200, json={'request_id': 'some_request_id'},
        )


def _mock_psp_events(mockserver, load_py_json, json_path):
    @mockserver.json_handler('psp/events')
    def _handler(request):
        del request  # unused
        return mockserver.make_response(
            status=200, json=load_py_json(json_path),
        )


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_wallet_hold_fail(
        eda_stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
):
    fill_service_orders_success()
    mock_trust_create_basket('trust-basket-token')
    mock_trust_pay_basket('trust-basket-token', payment_status='started')
    mock_trust_check_basket(
        purchase_token='trust-basket-token', payment_status='not_authorized',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token', payment_status='not_authorized',
    )
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    invoice_id = 'wallet-hold_fail-composite'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client,
            invoice_id,
            payments=[PAYMENT_WALLET, PAYMENT_CARD],
        )
        assert stq.is_empty
    with stq.flushing():
        operation_id = await _charge_wallet_and_card(
            eda_web_app_client, invoice_id,
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id

    # Charge wallet & card
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(
        payment_type='personal_wallet', status='hold_init', refunds=[],
    )
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_fail'
    with stq.flushing():
        # On this iteration, we process peer gateway failures
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[0].status = 'failed'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.parametrize(
    'disable_automatic_composite_refund', [False, None, True],
)
async def test_card_hold_fail(
        eda_stq3_context,
        mockserver,
        stq,
        now,
        mock_get_pass_params,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        mock_trust_resize,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
        disable_automatic_composite_refund,
):
    fill_service_orders_success()
    mock_trust_create_basket('trust-basket-token')
    mock_trust_pay_basket('trust-basket-token', payment_status='started')
    mock_trust_check_basket(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    mock_trust_resize(
        purchase_token='trust-basket-token',
        service_order_id='some_service_order_id',
    )
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()

    invoice_id = 'card-hold-fail-composite'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client,
            invoice_id,
            payments=[PAYMENT_WALLET, PAYMENT_CARD],
            disable_automatic_composite_refund=(
                disable_automatic_composite_refund
            ),
        )
        assert stq.is_empty
    with stq.flushing():
        operation_id = await _charge_wallet_and_card(
            eda_web_app_client, invoice_id,
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id

    # Charge wallet & card
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(
        payment_type='personal_wallet', status='hold_init', refunds=[],
    )
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.add_transaction(
            payment_type='card', status='hold_init', refunds=[],
        )
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[1].status = 'hold_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        mock_trust_check_basket(
            purchase_token='trust-basket-token',
            payment_status='not_authorized',
        )
        mock_trust_check_basket_full(
            purchase_token='trust-basket-token',
            payment_status='not_authorized',
        )
        state.transactions[1].status = 'hold_fail'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
    if disable_automatic_composite_refund:
        state.transactions[0].status = 'hold_success'
    else:
        state.transactions[0].status = 'hold_resize'
        with stq.flushing():
            await _run_task(eda_stq3_context, invoice_id)
            _assert_next_iter_planned(stq, invoice_id)
            await _check_state(eda_web_app_client, state)
            state.transactions[0].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[0].status = 'failed'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_drop_wallet(
        eda_stq3_context,
        mockserver,
        stq,
        now,
        db,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        trust_clear_init_success,
        trust_clear_pending_success,
        trust_create_refund_success,
        mock_trust_start_refund,
        mock_trust_resize,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
):
    fill_service_orders_success()
    mock_trust_create_basket('trust-basket-token')
    mock_trust_pay_basket('trust-basket-token', payment_status='started')
    mock_trust_check_basket(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    mock_trust_resize(
        purchase_token='trust-basket-token',
        service_order_id='some_service_order_id',
    )
    trust_clear_init_success()
    trust_create_refund_success()
    mock_trust_start_refund(status='success')
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    invoice_id = 'happy-composite'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client,
            invoice_id,
            payments=[PAYMENT_WALLET, PAYMENT_CARD],
        )
        assert stq.is_empty
    with stq.flushing():
        operation_id = await _charge_wallet_and_card(
            eda_web_app_client, invoice_id,
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id

    # Charge wallet & card
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(
        payment_type='personal_wallet', status='hold_init', refunds=[],
    )
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.add_transaction(
            payment_type='card', status='hold_init', refunds=[],
        )
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[1].status = 'hold_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[1].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[0].status = 'done'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.transactions_eda_events.times_called == 0
        await _check_state(eda_web_app_client, state)
    assert stq.is_empty

    # Drop wallet from payments and transfer its share of invoice sum to card
    # We expect wallet transaction to refund and then a card transaction to be
    # created
    state.add_operation(operation_id='drop-wallet', status='init')
    with stq.flushing():
        await _drop_wallet(eda_web_app_client, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[1].status = 'processing'
        state.transactions[0].status = 'hold_resize'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.add_transaction(
            payment_type='card', status='hold_init', refunds=[],
        )
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[2].status = 'hold_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[2].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[1].status = 'done'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.transactions_eda_events.times_called == 0
        await _check_state(eda_web_app_client, state)
    assert stq.is_empty


async def test_remove_item(eda_stq3_context, db, stq, now, eda_web_app_client):
    invoice_id = 'composite-ride-and-tips'
    operation_id = 'remove-tips'
    with stq.flushing():
        await _remove_tips(eda_web_app_client, invoice_id, operation_id)
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id

    expected_items_by_payment_type = [
        {
            'items': [
                {
                    'amount': '100',
                    'fiscal_receipt_info': {
                        'personal_tin_id': 'tin_pd_id',
                        'title': 'food delivery',
                        'vat': 'nds_20',
                        'cashregister_params': None,
                    },
                    'item_id': 'ride',
                    'product_id': 'eda_107819207_ride',
                    'region_id': 225,
                },
                {'amount': '0', 'item_id': 'tips'},
            ],
            'payment_type': 'personal_wallet',
        },
        {
            'items': [
                {
                    'amount': '100',
                    'fiscal_receipt_info': {
                        'personal_tin_id': 'tin_pd_id',
                        'title': 'food delivery',
                        'vat': 'nds_20',
                        'cashregister_params': None,
                    },
                    'item_id': 'food',
                    'product_id': 'eda_107819207_ride',
                    'region_id': 225,
                },
                {
                    'amount': '0',
                    'price': '25',
                    'quantity': '0',
                    'fiscal_receipt_info': {
                        'personal_tin_id': 'tin_pd_id',
                        'title': 'food delivery tips',
                        'vat': 'nds_20',
                        'cashregister_params': None,
                    },
                    'item_id': 'food_tips',
                    'product_id': 'eda_107819207_ride',
                    'region_id': 225,
                },
            ],
            'payment_type': 'card',
        },
    ]

    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        # Complete operation
        await _run_task(eda_stq3_context, invoice_id)
        invoice = await db.eda_invoices.find_one({'_id': invoice_id})
        # Expect the same sum to pay, but with zero tips (not absent tips!)
        _assert_items_by_payment_type_equal(
            invoice['payment_tech']['items_by_payment_type'],
            expected_items_by_payment_type,
        )
        _assert_all_operations_are_done(invoice)
        _assert_next_iter_planned(stq, invoice_id)


async def test_remove_all_items(
        eda_stq3_context, db, stq, now, eda_web_app_client,
):
    invoice_id = 'composite-ride-and-tips-not-holded'
    operation_id = 'remove-all-items'
    with stq.flushing():
        await _remove_all_items(eda_web_app_client, invoice_id, operation_id)
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id
    expected_items_by_payment_type = [
        {
            'items': [
                {'amount': '0', 'item_id': 'ride'},
                {'amount': '0', 'item_id': 'tips'},
            ],
            'payment_type': 'personal_wallet',
        },
        {
            'items': [
                {
                    'amount': '0',
                    'fiscal_receipt_info': {
                        'personal_tin_id': 'tin_pd_id',
                        'title': 'food delivery',
                        'vat': 'nds_20',
                        'cashregister_params': None,
                    },
                    'item_id': 'food',
                    'product_id': 'eda_107819207_ride',
                    'region_id': 225,
                },
                {
                    'amount': '0',
                    'fiscal_receipt_info': {
                        'personal_tin_id': 'tin_pd_id',
                        'title': 'food delivery tips',
                        'vat': 'nds_20',
                        'cashregister_params': None,
                    },
                    'item_id': 'food_tips',
                    'product_id': 'eda_107819207_ride',
                    'region_id': 225,
                },
            ],
            'payment_type': 'card',
        },
    ]

    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        # Complete operation
        await _run_task(eda_stq3_context, invoice_id)
        invoice = await db.eda_invoices.find_one({'_id': invoice_id})
        # Expect the same sum to pay, but with zero everything
        _assert_items_by_payment_type_equal(
            invoice['payment_tech']['items_by_payment_type'],
            expected_items_by_payment_type,
        )
        _assert_all_operations_are_done(invoice)
        _assert_next_iter_planned(stq, invoice_id)


async def test_api_version_downgrade(
        eda_stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        setup_basket_hold,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
):
    fill_service_orders_success()
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    invoice_id = 'api-version-downgrade'
    state = _state._ExpectedState.empty(invoice_id)
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty

    # Charge card
    setup_basket_hold('trust-basket-token-1')
    operation_id = 'charge_1'
    with stq.flushing():
        await _charge_card(
            client=eda_web_app_client,
            invoice_id=invoice_id,
            operation_id=operation_id,
            amount='900',
            api_version=2,
            omit_payment=False,
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id
    await _ensure_card_holds(
        stq_context=eda_stq3_context,
        stq=stq,
        web_client=eda_web_app_client,
        state=state,
        invoice_id=invoice_id,
        operation_id=operation_id,
    )

    setup_basket_hold('trust-basket-token-2')
    # Charge card again, but this time using API v1
    operation_id = 'charge_2'
    with stq.flushing():
        await _charge_card(
            client=eda_web_app_client,
            invoice_id=invoice_id,
            operation_id=operation_id,
            amount='1000',
            api_version=1,
            omit_payment=False,
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id
    await _ensure_card_holds(
        stq_context=eda_stq3_context,
        stq=stq,
        web_client=eda_web_app_client,
        state=state,
        invoice_id=invoice_id,
        operation_id=operation_id,
    )

    # Now try calling v1/update after v2/create and omit payment from update
    # request
    invoice_id = 'api-version-downgrade-from-create'
    state = _state._ExpectedState.empty(invoice_id)
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty

    # Charge card with API v1 and omit payment
    setup_basket_hold('trust-basket-token-3')
    operation_id = 'charge_1'
    with stq.flushing():
        await _charge_card(
            client=eda_web_app_client,
            invoice_id=invoice_id,
            operation_id=operation_id,
            amount='900',
            api_version=1,
            omit_payment=True,
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id
    state = _state._ExpectedState.empty(invoice_id)
    await _ensure_card_holds(
        stq_context=eda_stq3_context,
        stq=stq,
        web_client=eda_web_app_client,
        state=state,
        invoice_id=invoice_id,
        operation_id=operation_id,
    )


async def test_api_version_upgrade(
        eda_stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        setup_basket_hold,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
):
    fill_service_orders_success()
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    invoice_id = 'api-version-upgrade'
    state = _state._ExpectedState.empty(invoice_id)
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client,
            invoice_id,
            payments=[PAYMENT_CARD],
            api_version=1,
        )
        assert stq.is_empty

    # Charge card with API v2 and omit payment
    setup_basket_hold('trust-basket-token-1')
    operation_id = 'charge_1'
    with stq.flushing():
        await _charge_card(
            client=eda_web_app_client,
            invoice_id=invoice_id,
            operation_id=operation_id,
            amount='777',
            api_version=2,
            omit_payment=True,
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id
    state = _state._ExpectedState.empty(invoice_id)
    await _ensure_card_holds(
        stq_context=eda_stq3_context,
        stq=stq,
        web_client=eda_web_app_client,
        state=state,
        invoice_id=invoice_id,
        operation_id=operation_id,
    )


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_happy_path_sbp(
        eda_stq3_context,
        mockserver,
        stq,
        now,
        mock_get_pass_params,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        trust_clear_init_success,
        trust_clear_pending_success,
        trust_create_refund_success,
        mock_trust_start_refund,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
):
    fill_service_orders_success()
    mock_trust_create_basket('trust-basket-token')
    mock_trust_pay_basket('trust-basket-token', payment_status='started')
    mock_trust_check_basket(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    trust_clear_init_success()
    trust_create_refund_success()
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    mock_trust_start_refund(status='success')
    invoice_id = 'happy-composite-sbp'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client, invoice_id, payments=[PAYMENT_SBP],
        )
        assert stq.is_empty
    with stq.flushing():
        operation_id = await _charge_sbp(
            eda_web_app_client,
            invoice_id,
            transaction_payload={'some': 'payload'},
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id
    # Charge sbp
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(payment_type='sbp', status='hold_init', refunds=[])
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_pending'
        _assert_called_get_pass_params_sbp(
            mock_get_pass_params, eda_stq3_context,
        )
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[0].status = 'done'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.transactions_eda_events.times_called == 0
        await _check_state(eda_web_app_client, state)
    assert stq.is_empty

    # Clear invoice
    trust_clear_pending_success()
    with stq.flushing():
        await _clear_invoice(eda_web_app_client, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'clear_init'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'clear_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'clear_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)

    # Refund sbp.
    state.add_operation(operation_id='composite-refund-sbp', status='init')
    with stq.flushing():
        await _refund_sbp(eda_web_app_client, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[1].status = 'processing'
        state.transactions[0].status = 'refund_pending'
        state.transactions[0].add_refund(status='refund_pending')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_called_get_pass_params_sbp(
            mock_get_pass_params, eda_stq3_context,
        )
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'clear_success'
        state.transactions[0].refunds[0].status = 'refund_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[1].status = 'done'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_resize_sbp(
        eda_stq3_context,
        mockserver,
        stq,
        now,
        db,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        trust_clear_init_success,
        trust_clear_pending_success,
        trust_create_refund_success,
        mock_trust_start_refund,
        mock_trust_resize,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
):
    fill_service_orders_success()
    mock_trust_create_basket('trust-basket-token')
    mock_trust_pay_basket('trust-basket-token', payment_status='started')
    mock_trust_check_basket(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    mock_trust_resize(
        purchase_token='trust-basket-token',
        service_order_id='some_service_order_id',
    )
    trust_clear_init_success()
    trust_create_refund_success()
    mock_trust_start_refund(status='success')
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    invoice_id = 'happy-composite'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client, invoice_id, payments=[PAYMENT_SBP],
        )
        assert stq.is_empty
    with stq.flushing():
        operation_id = await _charge_sbp(eda_web_app_client, invoice_id)
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id

    # Charge sbp
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(payment_type='sbp', status='hold_init', refunds=[])
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[0].status = 'done'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.transactions_eda_events.times_called == 0
        await _check_state(eda_web_app_client, state)
    assert stq.is_empty

    # Drop wallet from payments and transfer its share of invoice sum to card
    # We expect wallet transaction to refund and then a card transaction to be
    # created
    state.add_operation(operation_id='composite-charge-sbp', status='init')
    with stq.flushing():
        await _charge_sbp(
            eda_web_app_client,
            invoice_id,
            amount='80',
            operation_id='composite-charge-sbp',
        )
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[1].status = 'processing'
        state.transactions[0].status = 'hold_resize'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_success'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[1].status = 'done'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.transactions_eda_events.times_called == 0
        await _check_state(eda_web_app_client, state)
    assert stq.is_empty


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.parametrize(
    'order_for_create, order_for_update', [(True, False), (False, True)],
)
@pytest.mark.parametrize(
    'desired_order, expected_order',
    [
        (['card', 'personal_wallet'], ['card', 'personal_wallet']),
        (None, ['personal_wallet', 'card']),
    ],
)
async def test_happy_path_desired_payment_types_order(
        eda_stq3_context,
        _check_transaction_pipeline,
        mockserver,
        stq,
        now,
        mock_get_pass_params,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        trust_clear_init_success,
        trust_clear_pending_success,
        trust_create_refund_success,
        mock_trust_start_refund,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
        order_for_create,
        order_for_update,
        desired_order,
        expected_order,
):
    fill_service_orders_success()
    mock_trust_create_basket('trust-basket-token')
    mock_trust_pay_basket('trust-basket-token', payment_status='started')
    mock_trust_check_basket(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    trust_clear_init_success()
    trust_create_refund_success()
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    mock_trust_start_refund(status='success')
    invoice_id = 'happy-composite'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client,
            invoice_id,
            payments=[PAYMENT_WALLET, PAYMENT_CARD],
            desired_payment_types_order=(
                desired_order if order_for_create else None
            ),
        )
        assert stq.is_empty
    with stq.flushing():
        operation_id = await _charge_wallet_and_card(
            eda_web_app_client,
            invoice_id,
            transaction_payload={'some': 'payload'},
            desired_payment_types_order=(
                desired_order if order_for_update else None
            ),
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id
    # Charge wallet & card
    state = _state._ExpectedState.empty(invoice_id)
    state.add_operation(operation_id=operation_id, status='processing')

    for index, payment_type in enumerate(expected_order):
        state.add_transaction(
            payment_type=payment_type, status='hold_init', refunds=[],
        )
        await _check_transaction_pipeline(invoice_id, state, index)

    state.operations[0].status = 'done'

    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.transactions_eda_events.times_called == 0
        await _check_state(eda_web_app_client, state)
    assert stq.is_empty


@pytest.fixture
def _check_transaction_pipeline(eda_stq3_context, stq, eda_web_app_client):
    async def _inner(invoice_id, state, transaction_index):
        with stq.flushing():
            await _run_task(eda_stq3_context, invoice_id)
            _assert_next_iter_planned(stq, invoice_id)
            await _check_state(eda_web_app_client, state)
            state.transactions[transaction_index].status = 'hold_pending'
        with stq.flushing():
            await _run_task(eda_stq3_context, invoice_id)
            _assert_next_iter_planned(stq, invoice_id)
            await _check_state(eda_web_app_client, state)
            state.transactions[transaction_index].status = 'hold_success'
        with stq.flushing():
            await _run_task(eda_stq3_context, invoice_id)
            _assert_next_iter_planned(stq, invoice_id)
            await _check_state(eda_web_app_client, state)

    return _inner


async def _charge_sbp(
        client,
        invoice_id,
        operation_id='composite-charge',
        transaction_payload=None,
        amount='100',
) -> str:
    await _update_invoice(
        client,
        invoice_id,
        operation_id=operation_id,
        payment_items=[
            {
                'payment_type': 'sbp',
                'items': [
                    {
                        'item_id': 'ride',
                        'amount': amount,
                        'product_id': 'eda_107819207_ride',
                        'region_id': 225,
                        'fiscal_receipt_info': FISCAL_RECEIPT_INFO,
                    },
                ],
            },
        ],
        transaction_payload=transaction_payload,
    )
    return operation_id


@pytest.fixture(name='setup_basket_hold')
def _setup_basket_hold(
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
):
    def _do_mock(purchase_token):
        mock_trust_create_basket(purchase_token)
        mock_trust_pay_basket(purchase_token, payment_status='started')
        mock_trust_check_basket(
            purchase_token=purchase_token, payment_status='authorized',
        )
        mock_trust_check_basket_full(
            purchase_token=purchase_token, payment_status='authorized',
        )

    return _do_mock


async def _ensure_card_holds(
        stq_context,
        stq,
        web_client,
        state: _state._ExpectedState,
        invoice_id: str,
        operation_id: str,
):
    transaction_index = len(state.transactions)
    operation_index = len(state.operations)
    state.add_transaction(payment_type='card', status='hold_init', refunds=[])
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(stq_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_client, state)
        state.transactions[transaction_index].status = 'hold_pending'
    with stq.flushing():
        await _run_task(stq_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_client, state)
        state.transactions[transaction_index].status = 'hold_success'
    with stq.flushing():
        await _run_task(stq_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_client, state)
        state.operations[operation_index].status = 'done'
    with stq.flushing():
        await _run_task(stq_context, invoice_id)
        assert stq.transactions_eda_events.times_called == 0
        await _check_state(web_client, state)
    assert stq.is_empty


def _assert_all_operations_are_done(invoice):
    operations = invoice['invoice_request']['operations']
    assert all(operation['status'] == 'done' for operation in operations)


def _assert_items_by_payment_type_equal(
        items_by_payment_type, expected_items_by_payment_type,
):
    _sort_sum_to_pay(items_by_payment_type)
    _sort_sum_to_pay(expected_items_by_payment_type)
    assert items_by_payment_type == expected_items_by_payment_type


def _sort_sum_to_pay(items_by_payment_type):
    items_by_payment_type.sort(
        key=lambda payment_items: payment_items['payment_type'],
    )
    for payment_items in items_by_payment_type:
        payment_items['items'].sort(key=lambda item: item['item_id'])


async def _check_state(eda_web_app_client, state: _state._ExpectedState):
    invoice = await _get_invoice(eda_web_app_client, state.invoice_id)
    state.check(invoice)


async def _check_is_handled(eda_stq3_context, state: _state._ExpectedState):
    invoice = await eda_stq3_context.transactions.invoices.find_one(
        {'_id': state.invoice_id},
    )
    state.check_db_is_handled(invoice)


async def _create_invoice(
        client,
        invoice_id,
        payments,
        disable_automatic_composite_refund=None,
        api_version=2,
        desired_payment_types_order=None,
):
    assert api_version in (1, 2)
    body = {
        'id': invoice_id,
        'invoice_due': '2019-05-01 03:00:00Z',
        'billing_service': 'food_payment',
        'currency': 'RUB',
        'yandex_uid': '123',
        'personal_phone_id': 'personal-id',
        'pass_params': {},
        'user_ip': '127.0.0.1',
    }
    if disable_automatic_composite_refund is not None:
        body[
            'disable_automatic_composite_refund'
        ] = disable_automatic_composite_refund
    if api_version == 2:
        path = '/v2/invoice/create'
        body['payments'] = payments
        body['desired_payment_types_order'] = desired_payment_types_order
    elif api_version == 1:
        path = '/invoice/create'
        assert len(payments) == 1
        body['payment'] = payments[0]
    response = await client.post(path, json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {}


async def _update_invoice(
        client,
        invoice_id,
        operation_id,
        payment_items,
        payments=None,
        api_version=2,
        transaction_payload=None,
        desired_payment_types_order=None,
):
    assert api_version in (1, 2)
    body = {
        'id': invoice_id,
        'operation_id': operation_id,
        'originator': 'processing',
        'yandex_uid': '123',
    }
    if api_version == 2:
        path = '/v2/invoice/update'
        body['items_by_payment_type'] = payment_items
        if payments is not None:
            body['payments'] = payments
        if transaction_payload is not None:
            body['transaction_payload'] = transaction_payload
        if desired_payment_types_order is not None:
            body['desired_payment_types_order'] = desired_payment_types_order
    elif api_version == 1:
        path = '/invoice/update'
        assert (len(payment_items)) == 1
        body['items'] = payment_items[0]['items']
        if payments is not None:
            assert len(payments) == 1
            body['payment'] = payments[0]
    response = await client.post(path, json=body)
    content = await response.json()
    assert content == {}
    assert response.status == 200


async def _clear_invoice(client, invoice_id):
    response = await client.post(
        '/invoice/clear',
        json={'id': invoice_id, 'clear_eta': '2018-01-01T00:00:00'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}


async def _get_invoice(client, invoice_id):
    body = {'id': invoice_id}
    response = await client.post('/v2/invoice/retrieve', json=body)
    assert response.status == 200
    content = await response.json()
    return content


async def _charge_wallet_and_card(
        client,
        invoice_id,
        transaction_payload=None,
        desired_payment_types_order=None,
) -> str:
    operation_id = 'composite-charge'
    await _update_invoice(
        client,
        invoice_id,
        operation_id=operation_id,
        payment_items=[
            {
                'payment_type': 'personal_wallet',
                'items': [
                    {
                        'item_id': 'ride',
                        'amount': '100',
                        'product_id': 'eda_107819207_ride',
                        'region_id': 225,
                        'fiscal_receipt_info': FISCAL_RECEIPT_INFO,
                    },
                ],
            },
            {
                'payment_type': 'card',
                'items': [
                    {
                        'item_id': 'food',
                        'amount': '900',
                        'product_id': 'eda_107819207_ride',
                        'region_id': 225,
                        'fiscal_receipt_info': FISCAL_RECEIPT_INFO,
                    },
                ],
            },
        ],
        transaction_payload=transaction_payload,
        desired_payment_types_order=desired_payment_types_order,
    )
    return operation_id


async def _charge_card(
        client,
        invoice_id: str,
        operation_id: str,
        amount: str,
        api_version: int,
        omit_payment: bool,
):
    await _update_invoice(
        client,
        invoice_id,
        operation_id=operation_id,
        payment_items=[
            {
                'payment_type': 'card',
                'items': [
                    {
                        'item_id': 'food',
                        'amount': amount,
                        'product_id': 'eda_107819207_ride',
                        'region_id': 225,
                        'fiscal_receipt_info': FISCAL_RECEIPT_INFO,
                    },
                ],
            },
        ],
        payments=(None if omit_payment else [PAYMENT_CARD]),
        api_version=api_version,
    )


async def _remove_tips(client, invoice_id, operation_id):
    await _update_invoice(
        client,
        invoice_id,
        operation_id=operation_id,
        payment_items=[
            {
                'payment_type': 'personal_wallet',
                'items': [
                    {
                        'item_id': 'ride',
                        'amount': '100',
                        'product_id': 'eda_107819207_ride',
                        'region_id': 225,
                        'fiscal_receipt_info': FISCAL_RECEIPT_INFO,
                    },
                ],
            },
            {
                'payment_type': 'card',
                'items': [
                    {
                        'item_id': 'food',
                        'amount': '100',
                        'product_id': 'eda_107819207_ride',
                        'region_id': 225,
                        'fiscal_receipt_info': FISCAL_RECEIPT_INFO,
                    },
                ],
            },
        ],
    )


async def _remove_all_items(client, invoice_id, operation_id):
    await _update_invoice(
        client, invoice_id, operation_id=operation_id, payment_items=[],
    )


async def _refund_wallet_and_card(client, invoice_id) -> str:
    operation_id = 'composite-refund'
    await _update_invoice(
        client, invoice_id, operation_id=operation_id, payment_items=[],
    )
    return operation_id


async def _refund_sbp(client, invoice_id) -> str:
    operation_id = 'composite-refund-sbp'
    await _update_invoice(
        client, invoice_id, operation_id=operation_id, payment_items=[],
    )
    return operation_id


async def _drop_wallet(client, invoice_id, payment_type='card') -> str:
    operation_id = 'drop-wallet'
    await _update_invoice(
        client,
        invoice_id,
        operation_id=operation_id,
        payments=[PAYMENT_CARD],
        payment_items=[
            {
                'payment_type': payment_type,
                'items': [
                    {
                        'item_id': 'food',
                        'amount': '1000',
                        'product_id': 'eda_107819207_ride',
                        'region_id': 225,
                        'fiscal_receipt_info': FISCAL_RECEIPT_INFO,
                    },
                ],
            },
        ],
    )
    return operation_id


def _assert_next_iter_planned(stq, invoice_id):
    assert stq.transactions_eda_events.times_called == 1
    task = stq.transactions_eda_events.next_call()
    assert task['id'] == invoice_id


def _assert_next_iter_not_planned(stq, invoice_id):
    assert stq.transactions_eda_events.times_called == 0


def _assert_called_get_pass_params(mock, context):
    call = mock.calls[-1]
    assert isinstance(call.pop('invoice'), wrappers.Invoice)
    assert call == {
        'payment_type': const.PaymentType.PERSONAL_WALLET,
        'trust_details': context.transactions.trust_details,
        'maybe_agglomerations_client': (
            context.transactions.maybe_agglomerations_client
        ),
        'billing_payments_service_id': (
            context.config.TRANSACTIONS_BILLING_SERVICE_TOKENS['food_payment'][
                'billing_payments_service_id'
            ]
        ),
        'transaction_payload': {'some': 'payload'},
    }


def _assert_called_get_pass_params_sbp(mock, context):
    call = mock.calls[-1]
    assert isinstance(call.pop('invoice'), wrappers.Invoice)
    assert call == {
        'payment_type': const.PaymentType.SBP,
        'trust_details': context.transactions.trust_details,
        'maybe_agglomerations_client': (
            context.transactions.maybe_agglomerations_client
        ),
        'billing_payments_service_id': (
            context.config.TRANSACTIONS_BILLING_SERVICE_TOKENS['food_payment'][
                'billing_payments_service_id'
            ]
        ),
        'transaction_payload': {'some': 'payload'},
    }


async def _run_task(stq_context, invoice_id):
    await events_handler.task(
        stq_context,
        helpers.create_task_info(queue='transactions_eda_events'),
        invoice_id,
    )


@pytest.fixture(name='mock_cardstorage_payment_methods')
def _mock_cardstorage_payment_methods(mock_cardstorage):
    @mock_cardstorage('/v1/payment_methods')
    def _payment_methods(request):
        return {
            'available_cards': [
                {
                    'card_id': '1324',
                    'psp_payment_method_id': 'some_psp_payment_method_id',
                    'billing_card_id': '1324',
                    'currency': 'RUB',
                    'permanent_card_id': '',
                    'expiration_month': 12,
                    'expiration_year': 2025,
                    'number': '123456****8911',
                    'owner': 'abc',
                    'possible_moneyless': False,
                    'region_id': '225',
                    'regions_checked': [],
                    'system': 'visa',
                    'valid': True,
                    'bound': True,
                    'unverified': False,
                    'busy': False,
                    'busy_with': [],
                    'from_db': False,
                },
            ],
        }
