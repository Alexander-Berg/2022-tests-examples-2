import pytest

from . import consts
from . import helpers
from . import models


INVOICE_ORIGINATORS = pytest.mark.parametrize(
    'originator',
    [models.InvoiceOriginator.grocery, models.InvoiceOriginator.tips],
)


@INVOICE_ORIGINATORS
@pytest.mark.parametrize(
    'notification_type, operation_status, errors',
    [
        (consts.OPERATION_FINISH, 'done', None),
        (
            consts.OPERATION_FINISH,
            'failed',
            [
                {
                    'payment_type': 'card',
                    'error_reason_code': 'not_enough_funds',
                },
            ],
        ),
    ],
)
async def test_hold(
        grocery_orders,
        processing,
        transactions,
        run_transactions_callback,
        originator,
        notification_type,
        operation_status,
        errors,
):
    processing_state = 'hold_money'
    operation_type = 'create'
    operation_id = f'{operation_type}:123'

    processing.create_event.check(
        order_id=consts.ORDER_ID,
        payload=_make_payload(operation_id, errors),
        reason='setstate',
        state=processing_state,
        headers={
            'X-Idempotency-Token': _idempotency_token(
                operation_id, processing_state,
            ),
        },
    )

    transactions.retrieve.mock_response(
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                payment_type='card',
                error_reason_code='not_enough_funds',
            ),
        ],
    )

    await run_transactions_callback(
        originator=originator,
        operation_id=operation_id,
        notification_type=notification_type,
        operation_status=operation_status,
    )

    assert grocery_orders.info_times_called() == 1
    assert transactions.retrieve.times_called
    assert processing.create_event.times_called == 1


@pytest.mark.parametrize('operation_status', ['failed', 'obsolete'])
async def test_failed_operation(
        grocery_orders,
        processing,
        transactions,
        run_transactions_callback,
        operation_status,
):
    operation_type = 'create'
    operation_id = f'{operation_type}:123'
    processing_state = 'hold_money'

    errors = [
        {'payment_type': 'card', 'error_reason_code': 'operation_failed'},
    ]

    processing.create_event.check(
        order_id=consts.ORDER_ID,
        payload=_make_payload(operation_id, errors),
        reason='setstate',
        state=processing_state,
        headers={
            'X-Idempotency-Token': _idempotency_token(
                operation_id, processing_state,
            ),
        },
    )

    # Тест-кейс, когда нет транзакций и неоткуда взять код ошибки, но сама
    # операция при этом зафейленная. В этом случае мы должны все равно
    # правильно нотифицировать цикл заказа.
    transactions.retrieve.mock_response(
        transactions=[],
        operations=[
            helpers.make_operation(id=operation_id, status=operation_status),
        ],
    )

    await run_transactions_callback(
        invoice_id=consts.ORDER_ID,
        operation_id=operation_id,
        notification_type=consts.OPERATION_FINISH,
        operation_status=operation_status,
    )

    assert processing.create_event.times_called == 1


@INVOICE_ORIGINATORS
@pytest.mark.parametrize('operation_type', ['remove', 'cancel'])
@pytest.mark.parametrize(
    'notification_type, operation_status, errors',
    [
        (consts.OPERATION_FINISH, 'done', None),
        (
            consts.OPERATION_FINISH,
            'failed',
            [{'error_reason_code': 'refund_failed'}],
        ),
    ],
)
async def test_refund(
        grocery_orders,
        processing,
        transactions,
        run_transactions_callback,
        originator,
        operation_type,
        notification_type,
        operation_status,
        errors,
):
    processing_state = 'refund_money'
    operation_revision = '123'
    operation_id = f'{operation_type}:{operation_revision}'

    processing.create_event.check(
        order_id=consts.ORDER_ID,
        payload=_make_payload(operation_id, errors),
        reason='setstate',
        state=processing_state,
        headers={
            'X-Idempotency-Token': _idempotency_token(
                operation_id, processing_state,
            ),
        },
    )

    items = [models.Item(item_id='444', quantity='1', price='300')]
    refund = helpers.make_refund(
        operation_id=operation_id,
        status='refund_success',
        sum=models.to_transaction_items(items),
    )

    transactions.retrieve.mock_response(
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                payment_type='card',
                refunds=[refund],
            ),
        ],
    )

    await run_transactions_callback(
        originator=originator,
        operation_id=operation_id,
        notification_type=notification_type,
        operation_status=operation_status,
    )

    assert grocery_orders.info_times_called() == 1
    assert transactions.retrieve.times_called
    assert processing.create_event.times_called == 1


@INVOICE_ORIGINATORS
@pytest.mark.parametrize(
    'notification_type, processing_state, clear_status, errors',
    [
        (consts.TRANSACTION_CLEAR, 'close_money', 'clear_success', None),
        (
            consts.TRANSACTION_CLEAR,
            'close_money',
            'clear_fail',
            [{'error_reason_code': 'clear_failed'}],
        ),
    ],
)
async def test_clear(
        grocery_orders,
        processing,
        transactions,
        run_transactions_callback,
        originator,
        notification_type,
        processing_state,
        clear_status,
        errors,
):
    operation_type = 'create'
    operation_id = f'{operation_type}:123'

    processing.create_event.check(
        order_id=consts.ORDER_ID,
        payload=_make_clear_payload(errors),
        reason='setstate',
        state=processing_state,
        headers={
            'X-Idempotency-Token': _idempotency_token(
                operation_id, processing_state,
            ),
        },
    )

    external_payment_id = 'external_payment_id-123'

    transactions.retrieve.mock_response(
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                payment_type='card',
                error_reason_code='not_enough_funds',
                external_payment_id=external_payment_id,
            ),
        ],
    )

    await run_transactions_callback(
        originator=originator,
        operation_id=operation_id,
        notification_type=notification_type,
        transactions=[
            {
                'external_payment_id': external_payment_id,
                'payment_type': 'card',
                'status': clear_status,
            },
        ],
    )

    assert grocery_orders.info_times_called() == 1
    assert transactions.retrieve.times_called
    assert processing.create_event.times_called == 1


@pytest.mark.parametrize(
    'payment_type, operation_status, times_called',
    [('card', 'done', 1), ('personal_wallet', 'processing', 0)],
)
async def test_ignore_personal_wallet_clear(
        grocery_orders,
        processing,
        transactions,
        run_transactions_callback,
        payment_type,
        operation_status,
        times_called,
):
    operation_id = 'create:1'
    external_payment_id = 'external_payment_id-123'

    transactions.retrieve.mock_response(
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                payment_type='personal_wallet',
                external_payment_id=f'{external_payment_id}-personal_wallet',
            ),
            helpers.make_transaction(
                operation_id=operation_id,
                payment_type='card',
                external_payment_id=f'{external_payment_id}-card',
            ),
        ],
    )

    await run_transactions_callback(
        invoice_id=consts.ORDER_ID,
        operation_id=operation_id,
        operation_status=operation_status,
        notification_type=consts.TRANSACTION_CLEAR,
        transactions=[
            {
                'external_payment_id': f'{external_payment_id}-{payment_type}',
                'payment_type': payment_type,
                'status': 'clear_success',
            },
        ],
    )

    assert grocery_orders.info_times_called() == 1
    assert transactions.retrieve.times_called
    assert processing.create_event.times_called == times_called


@pytest.mark.parametrize(
    'operation_id, errors',
    [
        (
            'create:123',
            [
                {
                    'payment_type': 'card',
                    'error_reason_code': 'not_enough_funds',
                },
                {
                    'payment_type': 'personal_wallet',
                    'error_reason_code': 'not_enough_funds',
                },
            ],
        ),
        (
            'update:123',
            [
                {
                    'payment_type': 'card',
                    'error_reason_code': 'not_enough_funds',
                },
                {
                    'payment_type': 'applepay',
                    'error_reason_code': 'processing_error',
                },
            ],
        ),
    ],
)
async def test_with_fail_transaction(
        grocery_orders,
        processing,
        transactions,
        run_transactions_callback,
        operation_id,
        errors,
):
    processing.create_event.check(
        order_id=consts.ORDER_ID,
        payload=_make_payload(operation_id, errors),
        reason='setstate',
        state='hold_money',
    )

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(id='create:123'),
            helpers.make_operation(id='update:456'),
            helpers.make_operation(
                id='update:123',
                sum_to_pay=[
                    {'items': [], 'payment_type': 'card'},
                    {'items': [], 'payment_type': 'applepay'},
                ],
            ),
        ],
        transactions=[
            helpers.make_transaction(
                operation_id='create:123',
                payment_type='card',
                error_reason_code='not_enough_funds',
            ),
            helpers.make_transaction(
                operation_id='create:123',
                payment_type='personal_wallet',
                error_reason_code='not_enough_funds',
            ),
            helpers.make_transaction(
                operation_id='create:456',
                payment_type='personal_wallet',
                error_reason_code='processing_error',
            ),
            helpers.make_transaction(
                operation_id='create:456',
                payment_type='applepay',
                error_reason_code='processing_error',
            ),
        ],
    )

    await run_transactions_callback(
        invoice_id=consts.ORDER_ID,
        operation_id=operation_id,
        notification_type=consts.OPERATION_FINISH,
        operation_status='failed',
    )

    assert grocery_orders.info_times_called() == 1
    assert processing.create_event.times_called == 1


@pytest.mark.parametrize('debt_operation_status', ['done', 'failed'])
async def test_operation_debt_no_order_cycle_notification(
        grocery_orders,
        processing,
        transactions,
        run_transactions_callback,
        debt_operation_status,
):
    notification_type = consts.OPERATION_FINISH
    create_operation_id = 'create:123'
    debt_operation_id = f'{consts.DEBT_PREFIX}/1/2'

    transactions.retrieve.mock_response(
        transactions=[
            helpers.make_transaction(
                operation_id=create_operation_id,
                payment_type='card',
                error_reason_code='not_enough_funds',
                status='hold_fail',
            ),
            helpers.make_transaction(
                operation_id=debt_operation_id,
                payment_type='card',
                status='hold_success',
            ),
        ],
        operations=[
            helpers.make_operation(id=create_operation_id, status='failed'),
            helpers.make_operation(
                id=debt_operation_id, status=debt_operation_status,
            ),
        ],
    )

    await run_transactions_callback(
        originator=models.InvoiceOriginator.grocery,
        operation_id=debt_operation_id,
        notification_type=notification_type,
        operation_status=debt_operation_status,
    )

    assert processing.create_event.times_called == 0


def _make_payload(operation_id_full, errors=None):
    operation_type, operation_id = operation_id_full.split(':')
    ret = {'operation_id': operation_id, 'operation_type': operation_type}
    if errors:
        ret['errors'] = errors
    return ret


def _idempotency_token(operation_id_full, processing_state):
    operation_type, operation_id = operation_id_full.split(':')
    return (
        f'{consts.ORDER_ID}-{processing_state}-{operation_id}-{operation_type}'
    )


def _make_clear_payload(errors=None):
    operation_clear = 'clear'
    ret = {'operation_id': operation_clear, 'operation_type': operation_clear}
    if errors:
        ret['errors'] = errors
    return ret
