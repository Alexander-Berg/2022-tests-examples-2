import typing

import pytest

from tests_eats_payments import consts
from tests_eats_payments import db_order
from tests_eats_payments import helpers

EXTERNAL_PAYMENT_ID = '123456'


@pytest.mark.parametrize(
    [
        'billing_callback_times_called',
        'transaction_type_1',
        'transaction_type_2',
        'items_1',
        'items_2',
        'stq_items_1',
        'stq_items_2',
        'expect_fail',
    ],
    [
        pytest.param(
            1,
            'refund',
            None,
            [
                helpers.make_transactions_item(
                    item_id='big_mac', amount='-2.00',
                ),
                helpers.make_transactions_item(
                    item_id='french_fries', amount='-3.00',
                ),
            ],
            None,
            [
                helpers.make_billing_item(
                    item_id='big_mac',
                    amount='2.00',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
                helpers.make_billing_item(
                    item_id='french_fries',
                    amount='3.00',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
            ],
            None,
            False,
            id='Corporate resize down',
        ),
        pytest.param(
            1,
            'payment',
            None,
            [
                helpers.make_transactions_item(
                    item_id='big_mac', amount='2.00',
                ),
                helpers.make_transactions_item(
                    item_id='french_fries', amount='3.00',
                ),
            ],
            None,
            [
                helpers.make_billing_item(
                    item_id='big_mac',
                    amount='2.00',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
                helpers.make_billing_item(
                    item_id='french_fries',
                    amount='3.00',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
            ],
            None,
            False,
            id='Corporate resize up',
        ),
        pytest.param(
            0,
            None,
            None,
            [
                helpers.make_transactions_item(
                    item_id='big_mac', amount='-2.00',
                ),
                helpers.make_transactions_item(
                    item_id='french_fries', amount='3.00',
                ),
            ],
            None,
            None,
            None,
            True,
            id='Fail on having both positive and negative amounts',
        ),
        pytest.param(
            2,
            'refund',
            'payment',
            [
                helpers.make_transactions_item(
                    item_id='big_mac', amount='-2.00',
                ),
            ],
            [
                helpers.make_transactions_item(
                    item_id='french_fries', amount='3.00',
                ),
            ],
            [
                helpers.make_billing_item(
                    item_id='big_mac',
                    amount='2.00',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
            ],
            [
                helpers.make_billing_item(
                    item_id='french_fries',
                    amount='3.00',
                    place_id='some_place_id',
                    balance_client_id='some_id',
                    item_type='product',
                ),
            ],
            False,
            id='Two transactions with the same id',
        ),
    ],
)
async def test_corporate_payment_resize(
        experiments3,
        pgsql,
        insert_items,
        mock_transactions_invoice_retrieve,
        check_transactions_callback_task,
        stq,
        billing_callback_times_called,
        transaction_type_1,
        transaction_type_2,
        items_1,
        items_2,
        stq_items_1,
        stq_items_2,
        expect_fail,
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
            helpers.make_db_row(
                item_id='french_fries',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )

    transactions = [_get_transaction_with_corporate_resize(items_1)]

    if items_2 is not None:
        transactions.append(_get_transaction_with_corporate_resize(items_2))

    mock_transactions_invoice_retrieve(
        payment_types=['corp'], transactions=transactions,
    )

    await check_transactions_callback_task(
        operation_id='update:123456',
        notification_type='transaction_clear',
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
        ],
        expect_fail=expect_fail,
    )

    assert (
        stq.eats_payments_billing_proxy_callback.times_called
        == billing_callback_times_called
    )

    if billing_callback_times_called == 0:
        return

    task_info = stq.eats_payments_billing_proxy_callback.next_call()
    assert (
        task_info['id'] == f'test_order/update:123456/'
        f'{transaction_type_1}/{EXTERNAL_PAYMENT_ID}'
    )
    task_kwargs = task_info['kwargs']
    task_kwargs.pop('log_extra')

    assert task_kwargs == {
        'order_id': 'test_order',
        'external_payment_id': '123456',
        'transaction_type': transaction_type_1,
        'event_at': '2020-08-14T14:39:50.265+00:00',
        'payment_type': 'corp',
        'currency': 'RUB',
        'terminal_id': '456',
        'items': stq_items_1,
    }

    if billing_callback_times_called > 1:
        task_info = stq.eats_payments_billing_proxy_callback.next_call()
        assert (
            task_info['id'] == f'test_order/update:123456/'
            f'{transaction_type_2}/{EXTERNAL_PAYMENT_ID}'
        )
        task_kwargs = task_info['kwargs']
        task_kwargs.pop('log_extra')
        assert task_kwargs == {
            'order_id': 'test_order',
            'external_payment_id': '123456',
            'transaction_type': transaction_type_2,
            'event_at': '2020-08-14T14:39:50.265+00:00',
            'payment_type': 'corp',
            'currency': 'RUB',
            'terminal_id': '456',
            'items': stq_items_2,
        }


@pytest.mark.parametrize(
    [
        'billing_callback_times_called',
        'notification_type',
        'transaction_type',
        'refunds',
    ],
    [
        pytest.param(
            1,
            'transaction_clear',
            'payment',
            [],
            id='Badge refund with transaction_clear',
        ),
        pytest.param(
            1,
            'operation_finish',
            'refund',
            [
                helpers.make_refund(
                    refund_sum=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='2.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='french_fries', amount='3.00',
                        ),
                    ],
                    operation_id='refund:123456',
                    updated='2020-08-14T14:39:50.265+00:00',
                    status='refund_success',
                ),
            ],
            id='Badge refund with operation_finish',
        ),
        pytest.param(
            0,
            'operation_finish',
            '',
            [],
            id='Badge refund with operation_finish ' 'and empty refund list',
        ),
    ],
)
async def test_badge_refund(
        experiments3,
        pgsql,
        insert_items,
        mock_transactions_invoice_retrieve,
        check_transactions_callback_task,
        check_billing_callback,
        billing_callback_times_called,
        notification_type,
        transaction_type,
        refunds,
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
            helpers.make_db_row(
                item_id='french_fries',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(
        payment_types=['badge'],
        status='cleared',
        transactions=[
            _get_transaction_with_badge_payment_type(refunds=refunds),
        ],
    )
    await check_transactions_callback_task(
        operation_id='refund:123456',
        notification_type=notification_type,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
        ],
    )
    check_billing_callback(
        times_called=billing_callback_times_called,
        task_id=f'test_order/refund:123456/'
        f'{transaction_type}/{EXTERNAL_PAYMENT_ID}',
        order_id='test_order',
        external_payment_id='123456',
        transaction_type=transaction_type,
        event_at='2020-08-14T14:39:50.265+00:00',
        payment_type='badge',
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
            helpers.make_billing_item(
                item_id='french_fries',
                amount='3.00',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )


def _get_transaction_with_sbp_payment_type(refunds: typing.List[dict] = None):
    return helpers.make_transaction(
        status='clear_success',
        external_payment_id=EXTERNAL_PAYMENT_ID,
        operation_id='cancel:123456',
        payment_type='sbp',
        terminal_id='456',
        sum=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
            helpers.make_transactions_item(
                item_id='french_fries', amount='3.00',
            ),
        ],
        refunds=refunds,
    )


@pytest.mark.parametrize(
    [
        'billing_callback_times_called',
        'notification_type',
        'transaction_type',
        'refunds',
    ],
    [
        pytest.param(
            0,
            'transaction_clear',
            'payment',
            [],
            id='SBP refund with transaction_clear',
        ),
        pytest.param(
            1,
            'operation_finish',
            'refund',
            [
                helpers.make_refund(
                    refund_sum=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='2.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='french_fries', amount='3.00',
                        ),
                    ],
                    operation_id='cancel:123456',
                    updated='2020-08-14T14:39:50.265+00:00',
                    status='refund_success',
                ),
            ],
            id='SBP refund with operation_finish',
        ),
    ],
)
async def test_sbp_refund(
        experiments3,
        pgsql,
        insert_items,
        mock_transactions_invoice_retrieve,
        check_transactions_callback_task,
        check_billing_callback,
        billing_callback_times_called,
        notification_type,
        transaction_type,
        refunds,
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
            helpers.make_db_row(
                item_id='french_fries',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(
        payment_types=['sbp'],
        status='cleared',
        transactions=[_get_transaction_with_sbp_payment_type(refunds=refunds)],
    )
    await check_transactions_callback_task(
        operation_id='cancel:123456',
        notification_type=notification_type,
        transactions=[],
    )
    check_billing_callback(
        times_called=billing_callback_times_called,
        task_id=f'test_order/cancel:123456/'
        f'{transaction_type}/{EXTERNAL_PAYMENT_ID}',
        order_id='test_order',
        external_payment_id='123456',
        transaction_type=transaction_type,
        event_at='2020-08-14T14:39:50.265+00:00',
        payment_type='sbp',
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
            helpers.make_billing_item(
                item_id='french_fries',
                amount='3.00',
                place_id='some_place_id',
                balance_client_id='some_id',
                item_type='product',
            ),
        ],
    )


def _get_transaction_with_corporate_resize(items):
    return helpers.make_transaction(
        status='clear_success',
        external_payment_id=EXTERNAL_PAYMENT_ID,
        operation_id='update:123456',
        payment_type='corp',
        terminal_id='456',
        sum=items,
    )


def _get_transaction_with_badge_payment_type(
        refunds: typing.List[dict] = None,
):
    return helpers.make_transaction(
        status='clear_success',
        external_payment_id=EXTERNAL_PAYMENT_ID,
        operation_id='refund:123456',
        payment_type='badge',
        terminal_id='456',
        sum=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
            helpers.make_transactions_item(
                item_id='french_fries', amount='3.00',
            ),
        ],
        refunds=refunds,
    )


@pytest.mark.parametrize('operation_id', ['create:100500', 'update:100500'])
async def test_cashback_billing_notification_without_billing_info(
        testpoint,
        check_transactions_callback_task,
        mock_transactions_invoice_retrieve,
        experiments3,
        pgsql,
        operation_id,
):
    experiments3.add_config(**helpers.make_billing_experiment(True))
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()

    primary_external_payment_id = 'primary_external_payment_id'
    cashback_external_payment_id = 'cashback_external_payment_id'
    mock_transactions_invoice_retrieve(
        items=[
            helpers.make_transactions_payment_items(
                payment_type='card',
                items=[
                    helpers.make_transactions_item(
                        item_id='retail_product', amount='100',
                    ),
                ],
            ),
            helpers.make_transactions_payment_items(
                payment_type='personal_wallet',
                items=[
                    helpers.make_transactions_item(
                        item_id='retail_product', amount='200',
                    ),
                ],
            ),
        ],
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                external_payment_id=cashback_external_payment_id,
                operation_id=operation_id,
                payment_type=consts.PERSONAL_WALLET,
            ),
            helpers.make_transaction(
                status='clear_success',
                external_payment_id=primary_external_payment_id,
                operation_id=operation_id,
                payment_type='card',
            ),
        ],
        operations=[
            helpers.make_operation(id=operation_id),
            helpers.make_operation(id='cancel:123'),
        ],
    )

    @testpoint('cashback_billing_notification_canceled')
    def cashback_notifications_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=primary_external_payment_id,
            ),
        ],
        notification_type='operation_finish',
    )
    assert cashback_notifications_tp.times_called == 1


async def test_retail_cashback_notification_without_billing_info(
        testpoint,
        check_transactions_callback_task,
        mock_transactions_invoice_retrieve,
        experiments3,
        pgsql,
):
    operation_id = 'create:100500'
    experiments3.add_config(**helpers.make_billing_experiment(True))
    order = db_order.DBOrder(
        pgsql=pgsql, order_id='test_order', currency='RUB', service='eats',
    )
    order.upsert()

    primary_external_payment_id = 'primary_external_payment_id'
    cashback_external_payment_id = 'cashback_external_payment_id'
    mock_transactions_invoice_retrieve(
        items=[
            helpers.make_transactions_payment_items(
                payment_type='card',
                items=[
                    helpers.make_transactions_item(
                        item_id='retail_product', amount='100',
                    ),
                ],
            ),
            helpers.make_transactions_payment_items(
                payment_type='personal_wallet',
                items=[
                    helpers.make_transactions_item(
                        item_id='retail_product', amount='200',
                    ),
                ],
            ),
        ],
        transactions=[
            helpers.make_transaction(
                status='clear_success',
                external_payment_id=cashback_external_payment_id,
                operation_id=operation_id,
                payment_type=consts.PERSONAL_WALLET,
            ),
            helpers.make_transaction(
                status='clear_success',
                external_payment_id=primary_external_payment_id,
                operation_id=operation_id,
                payment_type='card',
            ),
        ],
        operations=[helpers.make_operation(id=operation_id)],
    )

    @testpoint('cashback_notification_canceled_by_operation_type')
    def cashback_notifications_tp(data):
        pass

    await check_transactions_callback_task(
        operation_id=operation_id,
        transactions=[
            helpers.make_callback_transaction(
                status='clear_success',
                external_payment_id=primary_external_payment_id,
            ),
        ],
        notification_type='operation_finish',
    )
    assert cashback_notifications_tp.times_called == 1
