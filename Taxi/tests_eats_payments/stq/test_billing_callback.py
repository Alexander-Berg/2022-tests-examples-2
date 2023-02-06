# pylint: disable=too-many-lines
import pytest

from tests_eats_payments import consts
from tests_eats_payments import db_order
from tests_eats_payments import helpers

CLEARED_DT = '2020-08-12T07:20:00+00:00'

EXTERNAL_PAYMENT_ID = '123456'
NOW = '2020-08-12T07:20:00+00:00'
OPERATION_INFO = {'originator': 'processing', 'priority': 1, 'version': 2}


def make_billing_experiment(send_enabled) -> dict:
    return {
        'name': 'eats_payments_billing_notifications',
        'consumers': ['eats-payments/billing-notifications'],
        'match': {'predicate': {'type': 'true'}, 'enabled': True},
        'clauses': [
            {
                'title': 'first clause',
                'predicate': {'type': 'true'},
                'value': {'send_billing_notifications_enabled': send_enabled},
            },
        ],
    }


@pytest.mark.parametrize(
    [
        'send_billing_notifications_enabled',
        'billing_callback_times_called',
        'testpoint_times_called',
    ],
    [(True, 1, 0), (False, 0, 2)],
)
@pytest.mark.parametrize(
    'operation_id',
    [
        'create:100500',
        'update:100500',
        'add_item:100500',
        'update:hold:test_order:100500',
    ],
)
async def test_experiment_resolving(
        testpoint,
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        insert_items,
        pgsql,
        experiments3,
        send_billing_notifications_enabled,
        billing_callback_times_called,
        testpoint_times_called,
        operation_id,
):
    experiments3.add_config(
        **make_billing_experiment(send_billing_notifications_enabled),
    )
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(
        id='test_order',
        currency='RUB',
        transactions=[_get_transaction(operation_id, payment_type='card')],
    )

    @testpoint('billing_notifications_disabled')
    def billing_notifications_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
        ],
        notification_type='transaction_clear',
    )
    check_billing_callback(
        task_id=f'test_order/{operation_id}/payment/123456',
        order_id='test_order',
        external_payment_id=EXTERNAL_PAYMENT_ID,
        transaction_type='payment',
        event_at=CLEARED_DT,
        payment_type='card',
        currency='RUB',
        terminal_id='456',
        items=[
            helpers.make_billing_item(
                item_id='big_mac',
                amount='2.00',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
        times_called=billing_callback_times_called,
    )
    assert billing_notifications_tp.times_called == testpoint_times_called


@pytest.mark.parametrize(
    'operation_id',
    ['create:100500', 'update:100500', 'update:hold:test_order:100500'],
)
async def test_payment_billing_notification_with_cashback(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        experiments3,
        pgsql,
        insert_items,
        operation_id,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )

    primary_external_payment_id = 'primary_external_payment_id'
    cashback_external_payment_id = 'cashback_external_payment_id'
    mock_transactions_invoice_retrieve(
        transactions=[
            _get_transaction(
                operation_id,
                payment_type=consts.PERSONAL_WALLET,
                external_payment_id=cashback_external_payment_id,
            ),
            _get_transaction(
                operation_id,
                payment_type='card',
                external_payment_id=primary_external_payment_id,
            ),
        ],
    )
    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=primary_external_payment_id,
            ),
        ],
        notification_type='transaction_clear',
    )
    task_id = (
        f'test_order/{operation_id}/payment/{primary_external_payment_id}'
    )
    check_billing_callback(
        task_id=task_id,
        order_id='test_order',
        external_payment_id=primary_external_payment_id,
        transaction_type='payment',
        event_at=CLEARED_DT,
        payment_type='card',
        currency='RUB',
        terminal_id='456',
        items=[
            helpers.make_billing_item(
                item_id='big_mac',
                amount='2.00',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )


@pytest.mark.parametrize(
    'operation_id',
    ['create:100500', 'update:100500', 'update:hold:test_order:100500'],
)
async def test_payment_billing_notification_disabled_by_originator(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        experiments3,
        pgsql,
        insert_items,
        operation_id,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        currency='RUB',
        service='eats',
        originator=consts.CORP_ORDER_ORIGINATOR,
    )
    order.upsert()
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )

    primary_external_payment_id = 'primary_external_payment_id'
    mock_transactions_invoice_retrieve(
        transactions=[
            _get_transaction(
                operation_id,
                payment_type='card',
                external_payment_id=primary_external_payment_id,
            ),
        ],
    )
    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=primary_external_payment_id,
            ),
        ],
        notification_type='transaction_clear',
    )
    check_billing_callback(times_called=0)


@pytest.mark.parametrize(
    [
        'operation_id',
        'refund_status',
        'billing_callback_times_called',
        'testpoint_times_called',
    ],
    [
        pytest.param(
            'refund:100500',
            'refund_success',
            1,
            0,
            id='Direct refund success',
        ),
        pytest.param(
            'refund:100500', 'refund_fail', 0, 1, id='Direct refund fail',
        ),
        pytest.param(
            'update:100500',
            'refund_success',
            1,
            0,
            id='Indirect refund success (update)',
        ),
        pytest.param(
            'update:100500',
            'refund_fail',
            0,
            1,
            id='Indirect refund fail (update)',
        ),
        pytest.param(
            'add_item:100500',
            'refund_success',
            1,
            0,
            id='Indirect refund success (add_item)',
        ),
        pytest.param(
            'add_item:100500',
            'refund_fail',
            0,
            1,
            id='Indirect refund fail (add_item)',
        ),
    ],
)
async def test_refund_billing_notification(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        insert_items,
        testpoint,
        experiments3,
        pgsql,
        operation_id,
        refund_status,
        billing_callback_times_called,
        testpoint_times_called,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(
        transactions=[
            _get_transaction_with_refund(
                operation_id=operation_id, refund_status=refund_status,
            ),
        ],
    )

    @testpoint('billing_notification_unsuccessful_refund')
    def unsuccessful_refund_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id=operation_id,
        notification_type='operation_finish',
        transactions=[],
    )
    check_billing_callback(
        times_called=billing_callback_times_called,
        task_id=f'test_order/{operation_id}/refund/{EXTERNAL_PAYMENT_ID}',
        order_id='test_order',
        external_payment_id='123456',
        transaction_type='refund',
        event_at=CLEARED_DT,
        payment_type='card',
        currency='RUB',
        terminal_id='456',
        items=[
            helpers.make_billing_item(
                item_id='big_mac',
                amount='1.00',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    assert unsuccessful_refund_tp.times_called == testpoint_times_called


@pytest.mark.parametrize(
    [
        'billing_callback_times_called',
        'testpoint_times_called',
        'notification_type',
        'operation_status',
    ],
    [
        (1, 0, 'transaction_clear', 'done'),
        (0, 1, 'operation_finish', 'done'),
        (0, 1, 'transaction_clear', 'failed'),
        (0, 1, 'operation_finish', 'failed'),
    ],
)
async def test_corp_refund_billing_notification(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        mock_personal_retrieve_emails,
        mock_personal_retrieve_tins,
        insert_items,
        pgsql,
        testpoint,
        billing_callback_times_called,
        testpoint_times_called,
        notification_type,
        operation_status,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()
    insert_items(
        [
            helpers.make_db_row(item_id='big_mac_1'),
            helpers.make_db_row(item_id='big_mac_2'),
            helpers.make_db_row(item_id='big_mac_3'),
        ],
    )
    transactions_payment_items = (
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac_1',
                    amount='2.00',
                    fiscal_receipt_info={
                        'personal_tin_id': 'personal-tin-id',
                        'title': 'Big Mac Burger',
                        'vat': 'nds_20',
                    },
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_2',
                    amount='3.00',
                    fiscal_receipt_info={
                        'personal_tin_id': 'personal-tin-id',
                        'title': 'Big Mac Burger',
                        'vat': 'nds_20',
                    },
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_3',
                    amount='3.00',
                    fiscal_receipt_info={
                        'personal_tin_id': 'personal-tin-id',
                        'title': 'Big Mac Burger',
                        'vat': 'nds_20',
                    },
                ),
            ],
        ),
    )
    items_to_refund = [
        {'amount': '-2.00', 'item_id': 'big_mac_1'},
        {'amount': '-3.00', 'item_id': 'big_mac_3'},
    ]
    operation_id = 'refund:1111115'
    transaction1 = helpers.make_transaction(
        external_payment_id=EXTERNAL_PAYMENT_ID,
    )
    transaction2 = helpers.make_transaction(
        sum=items_to_refund,
        operation_id=operation_id,
        status='clear_success',
        payment_type='corp',
        external_payment_id=EXTERNAL_PAYMENT_ID,
    )
    mock_transactions_invoice_retrieve(
        status='cleared',
        cleared=transactions_payment_items,
        payment_types=['corp'],
        operations=[
            helpers.make_operation(sum_to_pay=transactions_payment_items),
        ],
        transactions=[transaction1, transaction2],
    )

    @testpoint('billing_notification_for_corp_payment_disabled')
    def billing_disabled_tp(data):
        pass

    mock_personal_retrieve_emails()
    mock_personal_retrieve_tins()
    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[transaction1, transaction2],
        notification_type=notification_type,
        operation_status=operation_status,
    )

    check_billing_callback(
        times_called=billing_callback_times_called,
        task_id=f'test_order/{operation_id}/refund/{EXTERNAL_PAYMENT_ID}',
        order_id='test_order',
        external_payment_id=EXTERNAL_PAYMENT_ID,
        transaction_type='refund',
        event_at='2020-08-14T14:39:50.265+00:00',
        payment_type='corp',
        currency='RUB',
        terminal_id='57000176',
        items=[
            helpers.make_billing_item(
                item_id='big_mac_1',
                amount='2.00',
                place_id='100500',
                balance_client_id='123456',
                item_type='product',
            ),
            helpers.make_billing_item(
                item_id='big_mac_3',
                amount='3.00',
                place_id='100500',
                balance_client_id='123456',
                item_type='product',
            ),
        ],
    )
    assert billing_disabled_tp.times_called == testpoint_times_called


@pytest.mark.parametrize('terminal_id', ['123', None])
async def test_terminal_id(
        check_transactions_callback_task,
        check_billing_callback,
        experiments3,
        pgsql,
        mock_transactions_invoice_retrieve,
        insert_items,
        terminal_id,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()
    operation_id = 'create:100500'
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                external_payment_id=EXTERNAL_PAYMENT_ID,
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id=terminal_id,
                cleared=CLEARED_DT,
                sum=[
                    helpers.make_transactions_item(
                        item_id='big_mac', amount='2.00',
                    ),
                ],
            ),
        ],
    )
    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
        ],
        notification_type='transaction_clear',
    )
    kwargs = {
        'order_id': 'test_order',
        'external_payment_id': EXTERNAL_PAYMENT_ID,
        'transaction_type': 'payment',
        'event_at': CLEARED_DT,
        'payment_type': 'card',
        'currency': 'RUB',
        'items': [
            helpers.make_billing_item(
                item_id='big_mac',
                amount='2.00',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    }
    if terminal_id is not None:
        kwargs['terminal_id'] = terminal_id
    check_billing_callback(
        task_id=f'test_order/{operation_id}/payment/123456', **kwargs,
    )


async def test_do_not_send_zero_amount_items(
        check_transactions_callback_task,
        check_billing_callback,
        experiments3,
        pgsql,
        mock_transactions_invoice_retrieve,
        insert_items,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()
    operation_id = 'create:100500'
    # deliberately not inserting zero amount item
    # as it appears when update deletes an item
    # inserted in create previously
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                external_payment_id=EXTERNAL_PAYMENT_ID,
                status='clear_success',
                operation_id=operation_id,
                payment_type='card',
                terminal_id='456',
                cleared=CLEARED_DT,
                sum=[
                    helpers.make_transactions_item(
                        item_id='big_mac', amount='2.00',
                    ),
                    helpers.make_transactions_item(
                        item_id='zero_amount_item', amount='0.00',
                    ),
                ],
            ),
        ],
    )
    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
        ],
        notification_type='transaction_clear',
    )
    check_billing_callback(
        task_id=f'test_order/{operation_id}/payment/123456',
        order_id='test_order',
        external_payment_id=EXTERNAL_PAYMENT_ID,
        transaction_type='payment',
        event_at=CLEARED_DT,
        payment_type='card',
        currency='RUB',
        terminal_id='456',
        items=[
            helpers.make_billing_item(
                item_id='big_mac',
                amount='2.00',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )


@pytest.mark.parametrize(
    'payment_type, times_called', [('card', 1), (consts.PERSONAL_WALLET, 0)],
)
async def test_ignore_personal_wallet_in_transactions(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        insert_items,
        experiments3,
        payment_type,
        pgsql,
        times_called,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()

    operation_id = 'create:100500'

    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                external_payment_id=EXTERNAL_PAYMENT_ID,
                status='clear_success',
                operation_id=operation_id,
                payment_type=payment_type,
                terminal_id='456',
                cleared=CLEARED_DT,
                sum=[
                    helpers.make_transactions_item(
                        item_id='big_mac', amount='2.00',
                    ),
                ],
            ),
        ],
    )

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
        ],
        notification_type='transaction_clear',
    )

    check_billing_callback(
        task_id=f'test_order/{operation_id}/payment/123456',
        times_called=times_called,
    )


@pytest.mark.parametrize(
    'operation_id, payment_type, times_called',
    [
        pytest.param('refund:100500', 'card', 1, id='Direct refund with card'),
        pytest.param(
            'refund:100500',
            consts.PERSONAL_WALLET,
            0,
            id='Direct refund with personal_wallet',
        ),
        pytest.param(
            'update:100500',
            'badge',
            1,
            id='Indirect refund with badge (update)',
        ),
        pytest.param(
            'update:100500',
            consts.PERSONAL_WALLET,
            0,
            id='Indirect refund with personal_wallet (update)',
        ),
        pytest.param(
            'add_item:100500',
            'applepay',
            1,
            id='Indirect refund with applepay (add_item)',
        ),
        pytest.param(
            'add_item:100500',
            consts.PERSONAL_WALLET,
            0,
            id='Indirect refund with personal_wallet (add_item)',
        ),
    ],
)
async def test_ignore_personal_wallet_in_refunds(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        experiments3,
        pgsql,
        insert_items,
        operation_id,
        payment_type,
        times_called,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(
        transactions=[
            _get_transaction_with_refund(
                operation_id=operation_id, payment_type=payment_type,
            ),
        ],
    )

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
        ],
        notification_type='operation_finish',
    )

    check_billing_callback(
        task_id=f'test_order/{operation_id}/refund/123456',
        times_called=times_called,
    )


async def test_canceled_invoice_no_call(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        insert_items,
        testpoint,
        upsert_order,
):
    upsert_order('test_order')
    insert_items([helpers.make_db_row(item_id='big_mac')])
    mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                operation_id='create:100500', status='clear_success',
            ),
            helpers.make_transaction(
                operation_id='cancel:100500', status='clear_success',
            ),
        ],
        operations=[
            helpers.make_operation(id='create:100500'),
            helpers.make_operation(id='cancel:100500'),
        ],
    )

    @testpoint('billing_notification_canceled_invoice')
    def canceled_invoice_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id='create:100500',
        transactions=[
            helpers.make_callback_transaction(
                operation_id='create:100500', status='clear_success',
            ),
            helpers.make_callback_transaction(
                operation_id='cancel:100500', status='clear_success',
            ),
        ],
        notification_type='transaction_clear',
    )
    check_billing_callback(times_called=0)
    assert canceled_invoice_tp.times_called == 1


async def test_cancel_operation_no_call(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        testpoint,
        upsert_order,
):
    upsert_order('test_order')
    operation_id = 'cancel:100500'
    mock_transactions_invoice_retrieve()

    @testpoint('billing_notification_cancel_operation')
    def cancel_operation_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id=operation_id, notification_type='operation_finish',
    )
    check_billing_callback(times_called=0)
    assert cancel_operation_tp.times_called == 1


@pytest.mark.parametrize('operation_id', ['create:100500', 'update:100500'])
async def test_operation_finish_no_call(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        testpoint,
        operation_id,
        upsert_order,
):
    upsert_order('test_order')
    mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id, status='hold_success',
            ),
        ],
    )

    @testpoint('billing_notification_no_transaction_type')
    def no_transaction_type_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='operation_finish',
    )
    check_billing_callback(times_called=0)
    assert no_transaction_type_tp.times_called == 1


async def test_no_cleared_transaction_no_call(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        experiments3,
        pgsql,
        testpoint,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()
    operation_id = 'create:100500'
    mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id, status='clear_fail',
            ),
        ],
    )

    @testpoint('billing_notification_no_transaction_type')
    def no_transaction_type_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[helpers.make_callback_transaction(status='clear_fail')],
        notification_type='transaction_clear',
    )
    check_billing_callback(times_called=0)
    assert no_transaction_type_tp.times_called == 1


@pytest.mark.parametrize(
    'transaction_extra',
    [
        pytest.param(
            {'payment_type': None}, id='no payment_type in transaction',
        ),
        pytest.param(
            {
                'sum': [
                    helpers.make_transactions_item(
                        item_id='foo', amount='2.00',
                    ),
                ],
            },
            id='no billing info for item',
        ),
    ],
)
async def test_invalid_transaction_fail(
        check_transactions_callback_task,
        mock_transactions_invoice_retrieve,
        insert_items,
        transaction_extra,
        upsert_order,
):
    upsert_order('test_order')
    insert_items([helpers.make_db_row(item_id='big_mac')])
    operation_id = 'create:100500'
    mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                status='clear_success',
                **transaction_extra,
            ),
        ],
    )
    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(status='clear_success'),
        ],
        notification_type='transaction_clear',
        expect_fail=True,
    )


@pytest.mark.now(NOW)
@pytest.mark.parametrize('amount', ['10.00', '0.00'])
async def test_cashback_billing_notification(
        check_transactions_callback_task,
        check_billing_callback,
        mock_transactions_invoice_retrieve,
        insert_items,
        amount,
        upsert_order,
):
    upsert_order('test_order')
    operation_id = 'create:1234'

    order_id = 'test_order'
    item_id = 'shef_burger'
    place_id = 'some_place_id'
    balance_client_id = 'balance_client_id-123'

    insert_items(
        [
            helpers.make_db_row(
                item_id=item_id,
                place_id=place_id,
                balance_client_id=balance_client_id,
                item_type='product',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(
        operation_info=OPERATION_INFO,
        items=[
            {
                'payment_type': consts.PERSONAL_WALLET,
                'items': [{'item_id': item_id, 'amount': amount}],
            },
        ],
    )

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[],
        notification_type='operation_finish',
    )

    invoice_version = OPERATION_INFO['version']
    check_billing_callback(
        task_id=f'{order_id}/{operation_id}/{invoice_version}',
        order_id=order_id,
        transaction_type='total',
        event_at=NOW,
        payment_type=consts.PERSONAL_WALLET,
        currency='RUB',
        items=[
            helpers.make_billing_item(
                item_id=item_id,
                amount=amount,
                place_id=place_id,
                balance_client_id=balance_client_id,
                item_type='product',
            ),
        ],
    )


def _get_transaction(
        operation_id: str,
        payment_type: str = 'card',
        external_payment_id: str = EXTERNAL_PAYMENT_ID,
):
    return helpers.make_transaction(
        external_payment_id=external_payment_id,
        status='clear_success',
        operation_id=operation_id,
        payment_type=payment_type,
        terminal_id='456',
        cleared=CLEARED_DT,
        sum=[helpers.make_transactions_item(item_id='big_mac', amount='2.00')],
    )


def _get_transaction_with_refund(
        operation_id: str,
        payment_type: str = 'card',
        refund_status: str = 'refund_success',
):
    return helpers.make_transaction(
        status='clear_success',
        external_payment_id=EXTERNAL_PAYMENT_ID,
        operation_id='create:123456',
        payment_type=payment_type,
        terminal_id='456',
        sum=[helpers.make_transactions_item(item_id='big_mac', amount='2.00')],
        refunds=[
            helpers.make_refund(
                refund_sum=[
                    helpers.make_transactions_item(
                        item_id='big_mac',
                        amount='1.00',
                        fiscal_receipt_info={
                            'personal_tin_id': 'personal-tin-id',
                            'title': 'Big Mac Burger',
                            'vat': 'nds_20',
                        },
                    ),
                ],
                operation_id=operation_id,
                updated=CLEARED_DT,
                status=refund_status,
            ),
        ],
    )
