# pylint: disable=protected-access
from typing import Any
from typing import Dict

import pytest

from test_transactions import helpers
from transactions.internal import payment_handler
from transactions.stq import events_handler
from . import _state


PAYMENT_CARD = {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'}
FISCAL_RECEIPT_INFO = {
    'personal_tin_id': 'tin_pd_id',
    'vat': 'nds_20',
    'title': 'food delivery',
}
INVOICE_ID = 'invoice'
NO_OPERATION = '--no-operation--'
OMITTED_BASKET: Dict[str, Any] = {}


@pytest.mark.config(
    TRANSACTIONS_SERVICES_WITH_MANDATORY_QUANTITIES=['food_payment'],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_hold(
        now,
        setup_invoice,
        wait_for_state,
        setup_basket_hold,
        setup_basket_clear,
):
    await setup_invoice()
    state = _state._ExpectedState.empty(INVOICE_ID)
    operation_id = await setup_basket_hold(
        operation_id='charge',
        basket={
            'baton': {'quantity': '2', 'price': '40'},
            'kofe': {'quantity': '1', 'price': '150'},
        },
    )
    state.add_transaction(
        payment_type='card',
        status='hold_success',
        refunds=[],
        transaction_sum=payment_handler.Sum({'baton': '80', 'kofe': '150'}),
    )
    state.add_operation(operation_id=operation_id, status='done')
    await wait_for_state(state)
    # Clear invoice
    await setup_basket_clear()
    state.transactions[-1].status = 'clear_success'
    await wait_for_state(state)


@pytest.mark.parametrize(
    'basket, expected_resize, expected_transaction_sum',
    [
        pytest.param(
            {
                'baton': {'quantity': '0', 'price': '40'},
                'kofe': {'quantity': '0', 'price': '150'},
            },
            {
                'baton': {'quantity': '0', 'amount': '0'},
                'kofe': {'quantity': '0', 'amount': '0'},
            },
            {'baton': '0', 'kofe': '0'},
            id='full_unhold',
        ),
        pytest.param(
            {},
            {
                'baton': {'quantity': '0', 'amount': '0'},
                'kofe': {'quantity': '0', 'amount': '0'},
            },
            {'baton': '0', 'kofe': '0'},
            id='full_unhold_with_omitted_items',
        ),
        pytest.param(
            {
                'baton': {'quantity': '1', 'price': '40'},
                'kofe': {'quantity': '1', 'price': '150'},
            },
            {
                'baton': {'quantity': '1', 'amount': '40'},
                'kofe': {'quantity': '1', 'amount': '150'},
            },
            {'baton': '40', 'kofe': '150'},
            id='partial_unhold',
        ),
    ],
)
@pytest.mark.config(
    TRANSACTIONS_SERVICES_WITH_MANDATORY_QUANTITIES=['food_payment'],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_unhold(
        now,
        wait_for_state,
        setup_invoice,
        setup_basket_hold,
        setup_basket_resize,
        setup_basket_clear,
        basket,
        expected_resize,
        expected_transaction_sum,
):
    await setup_invoice()
    state = _state._ExpectedState.empty(INVOICE_ID)
    # Charge for basket
    operation_id = await setup_basket_hold(
        operation_id='charge',
        basket={
            'baton': {'quantity': '2', 'price': '40'},
            'kofe': {'quantity': '1', 'price': '150'},
        },
    )
    state.add_transaction(
        payment_type='card', status='hold_success', refunds=[],
    )
    state.add_operation(operation_id=operation_id, status='done')
    await wait_for_state(state)
    # Unhold basket
    operation_id = await setup_basket_resize(
        operation_id='unhold', basket=basket, resize=expected_resize,
    )
    state.transactions[-1].transaction_sum = payment_handler.Sum(
        expected_transaction_sum,
    )
    state.add_operation(operation_id=operation_id, status='done')
    await wait_for_state(state)
    # Clear invoice
    await setup_basket_clear()
    state.transactions[-1].status = 'clear_success'
    await wait_for_state(state)


@pytest.mark.parametrize(
    'basket, expected_refund, expected_refund_sum',
    [
        pytest.param(
            {
                'baton': {'quantity': '0', 'price': '40'},
                'kofe': {'quantity': '0', 'price': '150'},
            },
            {
                'baton': {'quantity': '2', 'amount': '80'},
                'kofe': {'quantity': '1', 'amount': '150'},
            },
            {'baton': '80', 'kofe': '150'},
            id='full_refund',
        ),
        pytest.param(
            {},
            {
                'baton': {'quantity': '2', 'amount': '80'},
                'kofe': {'quantity': '1', 'amount': '150'},
            },
            {'baton': '80', 'kofe': '150'},
            id='full_refund_with_omitted_items',
        ),
        pytest.param(
            {
                'baton': {'quantity': '1', 'price': '40'},
                'kofe': {'quantity': '1', 'price': '150'},
            },
            {'baton': {'quantity': '1', 'amount': '40'}},
            {'baton': '40'},
            id='partial_refund',
        ),
    ],
)
@pytest.mark.config(
    TRANSACTIONS_SERVICES_WITH_MANDATORY_QUANTITIES=['food_payment'],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_refund(
        now,
        setup_invoice,
        wait_for_state,
        setup_basket_hold,
        setup_basket_clear,
        setup_basket_refund,
        basket,
        expected_refund,
        expected_refund_sum,
):
    await setup_invoice()
    state = _state._ExpectedState.empty(INVOICE_ID)
    # Charge for basket
    operation_id = await setup_basket_hold(
        operation_id='charge',
        basket={
            'baton': {'quantity': '2', 'price': '40'},
            'kofe': {'quantity': '1', 'price': '150'},
        },
    )
    state.add_transaction(
        payment_type='card', status='hold_success', refunds=[],
    )
    state.add_operation(operation_id=operation_id, status='done')
    await wait_for_state(state)
    # Clear invoice
    await setup_basket_clear()
    state.transactions[-1].status = 'clear_success'
    await wait_for_state(state)
    # Refund basket
    operation_id = await setup_basket_refund(
        operation_id='refund', basket=basket, refund=expected_refund,
    )
    state.transactions[-1].add_refund(
        status='refund_success',
        refund_sum=payment_handler.Sum(expected_refund_sum),
    )
    state.add_operation(operation_id=operation_id, status='done')
    await wait_for_state(state)


@pytest.mark.parametrize(
    'basket',
    [
        pytest.param(
            {
                'baton': {'quantity': '0', 'price': '40'},
                'kofe': {'quantity': '1', 'price': '150'},
                'bulochka': {'quantity': '2', 'price': '60'},
            },
            id='with_old_item_zeroed_out',
        ),
        pytest.param(
            {
                'kofe': {'quantity': '1', 'price': '150'},
                'bulochka': {'quantity': '2', 'price': '60'},
            },
            id='with_old_item_omitted',
        ),
    ],
)
@pytest.mark.config(
    TRANSACTIONS_SERVICES_WITH_MANDATORY_QUANTITIES=['food_payment'],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_swap_after_hold(
        now,
        wait_for_state,
        setup_invoice,
        setup_basket_hold,
        setup_basket_resize,
        setup_invoice_update,
        setup_basket_clear,
        basket,
):
    await setup_invoice()
    state = _state._ExpectedState.empty(INVOICE_ID)
    # Charge for basket
    hold_op_id = await setup_basket_hold(
        operation_id='charge',
        basket={
            'baton': {'quantity': '2', 'price': '40'},
            'kofe': {'quantity': '1', 'price': '150'},
        },
    )
    state.add_transaction(
        payment_type='card', status='hold_success', refunds=[],
    )
    state.add_operation(operation_id=hold_op_id, status='done')
    await wait_for_state(state)
    # Unhold `baton` and hold `bulochka` instead
    await setup_basket_resize(
        operation_id=NO_OPERATION,
        basket=OMITTED_BASKET,
        resize={
            'baton': {'quantity': '0', 'amount': '0'},
            'kofe': {'quantity': '1', 'amount': '150'},
        },
    )
    await setup_basket_hold(
        operation_id=NO_OPERATION,
        basket={'bulochka': {'quantity': '2', 'price': '60'}},
    )
    swap_op_id = await setup_invoice_update(
        operation_id='swap-after-hold', basket=basket,
    )
    state.transactions[0].transaction_sum = payment_handler.Sum(
        {'baton': '0', 'kofe': '150'},
    )
    state.add_transaction(
        payment_type='card',
        status='hold_success',
        refunds=[],
        transaction_sum=payment_handler.Sum({'bulochka': '120'}),
    )
    state.add_operation(operation_id=swap_op_id, status='done')
    await wait_for_state(state)
    # Clear invoice
    await setup_basket_clear()
    state.transactions[0].status = 'clear_success'
    state.transactions[1].status = 'clear_success'
    await wait_for_state(state)


@pytest.mark.parametrize(
    'basket',
    [
        pytest.param(
            {
                'baton': {'quantity': '0', 'price': '40'},
                'kofe': {'quantity': '1', 'price': '150'},
                'bulochka': {'quantity': '2', 'price': '60'},
            },
            id='with_old_item_zeroed_out',
        ),
        pytest.param(
            {
                'kofe': {'quantity': '1', 'price': '150'},
                'bulochka': {'quantity': '2', 'price': '60'},
            },
            id='with_old_item_omitted',
        ),
    ],
)
@pytest.mark.config(
    TRANSACTIONS_SERVICES_WITH_MANDATORY_QUANTITIES=['food_payment'],
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_swap_after_clear(
        now,
        wait_for_state,
        setup_invoice,
        setup_basket_hold,
        setup_basket_refund,
        setup_invoice_update,
        setup_basket_clear,
        basket,
):
    await setup_invoice()
    state = _state._ExpectedState.empty(INVOICE_ID)
    # Charge for basket
    hold_op_id = await setup_basket_hold(
        operation_id='charge',
        basket={
            'baton': {'quantity': '2', 'price': '40'},
            'kofe': {'quantity': '1', 'price': '150'},
        },
    )
    state.add_transaction(
        payment_type='card', status='hold_success', refunds=[],
    )
    state.add_operation(operation_id=hold_op_id, status='done')
    await wait_for_state(state)
    # Clear invoice
    await setup_basket_clear()
    state.transactions[0].status = 'clear_success'
    await wait_for_state(state)
    # Refund `baton` and hold `bulochka` instead
    await setup_basket_refund(
        operation_id=NO_OPERATION,
        basket=OMITTED_BASKET,
        refund={'baton': {'quantity': '2', 'amount': '80'}},
    )
    await setup_basket_hold(
        operation_id=NO_OPERATION,
        basket={'bulochka': {'quantity': '2', 'price': '60'}},
    )
    swap_op_id = await setup_invoice_update(
        operation_id='swap-after-clear', basket=basket,
    )
    state.transactions[0].add_refund(
        status='refund_success',
        refund_sum=payment_handler.Sum({'baton': '80'}),
    )
    state.add_transaction(
        payment_type='card',
        status='clear_pending',
        refunds=[],
        transaction_sum=payment_handler.Sum({'bulochka': '120'}),
    )
    state.add_operation(operation_id=swap_op_id, status='done')
    await wait_for_state(state)
    # Clear new basket
    await setup_basket_clear()
    state.transactions[1].status = 'clear_success'
    await wait_for_state(state)


async def _wait_for_completion(context, stq, client, expected_state):
    max_iterations = 10
    for _ in range(max_iterations):
        with stq.flushing():
            await _run_task(context)
            if stq.transactions_eda_events.times_called == 0:
                break
            _assert_next_iter_planned(stq)
    assert stq.is_empty
    await _check_state(client, expected_state)


async def _charge(client, operation_id, basket) -> str:
    await _update_invoice(
        client,
        operation_id=operation_id,
        payment_items=[
            {
                'payment_type': 'card',
                'items': [
                    {
                        'item_id': item_id,
                        'price': item['price'],
                        'quantity': item['quantity'],
                        'product_id': 'eda_107819207_ride',
                        'fiscal_receipt_info': {
                            'personal_tin_id': 'tin_pd_id',
                            'vat': 'nds_none',
                            'title': item_id,
                        },
                    }
                    for item_id, item in basket.items()
                ],
            },
        ],
    )
    return operation_id


async def _update_invoice(client, operation_id, payment_items, payments=None):
    body = {
        'id': INVOICE_ID,
        'operation_id': operation_id,
        'originator': 'processing',
        'yandex_uid': '123',
        'items_by_payment_type': payment_items,
    }
    if payments is not None:
        body['payments'] = payments
    response = await client.post('/v2/invoice/update', json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {}


async def _create_invoice(client, payments):
    body = {
        'id': INVOICE_ID,
        'invoice_due': '2019-05-01 03:00:00Z',
        'billing_service': 'food_payment',
        'currency': 'RUB',
        'yandex_uid': '123',
        'personal_phone_id': 'personal-id',
        'pass_params': {},
        'user_ip': '127.0.0.1',
        'payments': payments,
    }
    response = await client.post('/v2/invoice/create', json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {}


async def _run_task(stq_context):
    await events_handler.task(
        stq_context,
        helpers.create_task_info(queue='transactions_eda_events'),
        INVOICE_ID,
    )


def _assert_next_iter_planned(stq):
    assert stq.transactions_eda_events.times_called == 1
    task = stq.transactions_eda_events.next_call()
    assert task['id'] == INVOICE_ID


async def _get_invoice(client):
    body = {'id': INVOICE_ID}
    response = await client.post('/v2/invoice/retrieve', json=body)
    assert response.status == 200
    content = await response.json()
    return content


async def _check_state(eda_web_app_client, state: _state._ExpectedState):
    invoice = await _get_invoice(eda_web_app_client)
    state.check(invoice)


async def _clear_invoice(client):
    response = await client.post(
        '/invoice/clear',
        json={'id': INVOICE_ID, 'clear_eta': '2018-01-01T00:00:00'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}


@pytest.fixture(name='setup_basket_hold')
def _setup_basket_hold(
        mock_experiments3,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        trust_clear_init_success,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
        setup_invoice_update,
):
    async def do_setup(operation_id, basket):
        fill_service_orders_success(return_input_order_id=True)
        mock_trust_create_basket(
            'trust-basket-token', expected_orders=_basket_to_orders(basket),
        )
        mock_trust_pay_basket('trust-basket-token', payment_status='started')
        mock_trust_check_basket(
            purchase_token='trust-basket-token', payment_status='authorized',
        )
        mock_trust_check_basket_full(
            purchase_token='trust-basket-token', payment_status='authorized',
        )
        trust_clear_init_success()
        personal_phones_retrieve()
        personal_tins_bulk_retrieve()
        if operation_id == NO_OPERATION:
            return operation_id
        return await setup_invoice_update(
            operation_id=operation_id, basket=basket,
        )

    return do_setup


@pytest.fixture(name='setup_basket_resize')
def _setup_basket_resize(
        mock_experiments3,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        mock_trust_resize,
        setup_invoice_update,
):
    async def do_setup(operation_id, basket, resize):
        mock_trust_check_basket(
            purchase_token='trust-basket-token', payment_status='authorized',
        )
        mock_trust_check_basket_full(
            purchase_token='trust-basket-token', payment_status='authorized',
        )
        for item_id, item in resize.items():
            mock_trust_resize(
                purchase_token='trust-basket-token',
                service_order_id=_make_service_order_id(item_id),
                expected_body={
                    'amount': item['amount'],
                    'qty': item['quantity'],
                },
            )
        if operation_id == NO_OPERATION:
            return operation_id
        return await setup_invoice_update(
            operation_id=operation_id, basket=basket,
        )

    return do_setup


@pytest.fixture(name='setup_basket_refund')
def _setup_basket_refund(
        trust_create_refund_success,
        mock_trust_start_refund,
        setup_invoice_update,
):
    async def do_setup(operation_id, basket, refund):
        trust_create_refund_success(
            expect_body={
                'orders': [
                    {
                        'order_id': _make_service_order_id(item_id),
                        'delta_amount': item['amount'],
                        'delta_qty': item['quantity'],
                    }
                    for item_id, item in refund.items()
                ],
            },
        )
        mock_trust_start_refund(status='success')
        if operation_id == NO_OPERATION:
            return operation_id
        return await setup_invoice_update(
            operation_id=operation_id, basket=basket,
        )

    return do_setup


@pytest.fixture(name='setup_basket_clear')
def _setup_basket_clear(stq, eda_web_app_client, trust_clear_pending_success):
    async def do_setup():
        trust_clear_pending_success()
        with stq.flushing():
            await _clear_invoice(eda_web_app_client)
            _assert_next_iter_planned(stq)

    return do_setup


@pytest.fixture(name='wait_for_state')
def _wait_for_state(eda_stq3_context, stq, eda_web_app_client):
    async def do_wait(state):
        await _wait_for_completion(
            context=eda_stq3_context,
            stq=stq,
            client=eda_web_app_client,
            expected_state=state,
        )

    return do_wait


@pytest.fixture(name='setup_invoice')
def _setup_invoice(stq, eda_web_app_client):
    async def do_setup():
        with stq.flushing():
            await _create_invoice(eda_web_app_client, payments=[PAYMENT_CARD])
            assert stq.is_empty

    return do_setup


@pytest.fixture(name='setup_invoice_update')
def _setup_invoice_update(stq, eda_web_app_client):
    async def do_setup(operation_id, basket):
        with stq.flushing():
            operation_id = await _charge(
                eda_web_app_client, operation_id, basket=basket,
            )
            _assert_next_iter_planned(stq)
        return operation_id

    return do_setup


def _basket_to_orders(basket):
    return [
        {
            'fiscal_inn': '0',
            'fiscal_nds': 'nds_none',
            'fiscal_title': item_id,
            'order_id': _make_service_order_id(item_id),
            'price': item['price'],
            'qty': item['quantity'],
        }
        for item_id, item in basket.items()
    ]


def _make_service_order_id(item_id):
    return f'invoice_{item_id}'
