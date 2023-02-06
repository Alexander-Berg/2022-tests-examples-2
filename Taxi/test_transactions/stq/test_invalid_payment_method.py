# pylint: disable=protected-access
import pytest

from test_transactions import helpers
from transactions.stq import events_handler
from . import _state


PAYMENT_CARD = {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'}


async def test_invalid_payment_method_on_check(
        db,
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
        add_charge_operation,
):
    fill_service_orders_success()
    mock_trust_create_basket('trust-basket-token')
    mock_trust_pay_basket(
        'trust-basket-token',
        payment_status='started',
        status='error',
        status_code='invalid_payment_method',
    )
    invoice_id = 'invalid-payment-method'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty
    state = _state._ExpectedState.empty(invoice_id)
    await add_charge_operation(state, invoice_id, operation_id='charge:1')
    state.operations[-1].status = 'processing'
    state.add_transaction(payment_type='card', status='hold_init', refunds=[])
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[-1].status = 'hold_fail'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[-1].status = 'failed'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.payments_eda_callback.has_calls
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
    assert stq.is_empty
    await _check_billing_response(db, invoice_id)


async def test_invalid_payment_method_on_create(
        db,
        eda_stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        add_charge_operation,
):
    fill_service_orders_success()
    mock_trust_create_basket(
        purchase_token='trust-basket-token',
        status='error',
        status_code='invalid_payment_method',
    )
    invoice_id = 'invalid-payment-method'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty
    state = _state._ExpectedState.empty(invoice_id)
    await add_charge_operation(state, invoice_id, operation_id='charge:1')
    # Queue another op to check that it will be picked up after
    # processing invalid_payment_method
    await add_charge_operation(state, invoice_id, operation_id='charge:2')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.payments_eda_callback.has_calls
        _assert_next_iter_planned(stq, invoice_id)
        state.operations[0].status = 'failed'
        await _check_state(eda_web_app_client, state)
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.payments_eda_callback.has_calls
        _assert_next_iter_not_planned(stq, invoice_id)
        state.operations[1].status = 'failed'
        await _check_state(eda_web_app_client, state)
    assert stq.is_empty
    await _check_payment_tech_flag(db, invoice_id)


async def _check_billing_response(db, invoice_id: str):
    invoice = await db.eda_invoices.find_one({'_id': invoice_id})
    assert len(invoice['billing_tech']['transactions']) == 1
    assert invoice['billing_tech']['transactions'][0]['billing_response'] == {
        'status': 'error',
        'status_code': 'invalid_payment_method',
    }


async def _check_payment_tech_flag(db, invoice_id: str):
    invoice = await db.eda_invoices.find_one({'_id': invoice_id})
    flag = invoice['payment_tech']['created_basket_with_unbound_card']
    assert flag


async def _check_state(eda_web_app_client, state: _state._ExpectedState):
    invoice = await _get_invoice(eda_web_app_client, state.invoice_id)
    state.check(invoice)


async def _create_invoice(client, invoice_id, payments):
    body = {
        'id': invoice_id,
        'invoice_due': '2019-05-01 03:00:00Z',
        'billing_service': 'food_payment',
        'currency': 'RUB',
        'yandex_uid': '123',
        'pass_params': {},
        'user_ip': '127.0.0.1',
        'payments': payments,
    }
    response = await client.post('/v2/invoice/create', json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {}


async def _get_invoice(client, invoice_id):
    body = {'id': invoice_id}
    response = await client.post('/v2/invoice/retrieve', json=body)
    assert response.status == 200
    content = await response.json()
    return content


async def _charge_card(
        client, invoice_id: str, operation_id: str, amount: str,
):
    body = {
        'id': invoice_id,
        'operation_id': operation_id,
        'originator': 'processing',
        'yandex_uid': '123',
        'items_by_payment_type': [
            {
                'payment_type': 'card',
                'items': [
                    {
                        'item_id': 'food',
                        'amount': amount,
                        'product_id': 'eda_107819207_ride',
                        'region_id': 225,
                    },
                ],
            },
        ],
    }
    response = await client.post('/v2/invoice/update', json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {}


def _assert_next_iter_planned(stq, invoice_id):
    assert stq.transactions_eda_events.times_called == 1
    task = stq.transactions_eda_events.next_call()
    assert task['id'] == invoice_id


def _assert_next_iter_not_planned(stq, invoice_id):
    assert stq.transactions_eda_events.times_called == 0


@pytest.fixture(name='add_charge_operation')
async def _add_charge_operation(stq, eda_web_app_client):
    async def add(
            state: _state._ExpectedState, invoice_id: str, operation_id: str,
    ):
        with stq.flushing():
            await _charge_card(
                client=eda_web_app_client,
                invoice_id=invoice_id,
                operation_id=operation_id,
                amount='100',
            )
            assert stq.transactions_eda_events.times_called == 1
            task = stq.transactions_eda_events.next_call()
            assert task['id'] == invoice_id
        state.add_operation(operation_id=operation_id, status='init')
        await _check_state(eda_web_app_client, state)

    return add


async def _run_task(stq_context, invoice_id):
    await events_handler.task(
        stq_context,
        helpers.create_task_info(queue='transactions_eda_events'),
        invoice_id,
    )
