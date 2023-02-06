import pytest

from tests_eats_payments import consts
from tests_eats_payments import db_order
from tests_eats_payments import helpers


@pytest.mark.parametrize('service', ['grocery', 'eats'])
@pytest.mark.parametrize(
    ['notification_type', 'operation_status', 'operation_id', 'times_called'],
    [
        ('transaction_clear', 'done', 'create:123456', 1),
        ('transaction_clear', 'failed', 'create:123456', 0),
        ('transaction_clear', 'done', 'update:hold:test_order:123456', 1),
        ('transaction_clear', 'failed', 'update:hold:test_order:123456', 0),
        ('operation_finish', 'done', 'create:123456', 0),
        ('operation_finish', 'failed', 'create:123456', 0),
        ('operation_finish', 'done', 'refund:123456', 1),
        ('operation_finish', 'failed', 'refund:123456', 0),
    ],
)
async def test_cashback_callback(
        check_transactions_callback_task,
        check_cashback_callback,
        mock_transactions_invoice_retrieve,
        insert_items,
        experiments3,
        pgsql,
        service,
        notification_type,
        operation_status,
        operation_id,
        times_called,
):
    # Use corp originator with disabled debt setting
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id='test_order',
        currency='RUB',
        service='eats',
        originator=consts.CORP_ORDER_ORIGINATOR,
    )
    order.upsert()
    insert_items([helpers.make_db_row(item_id='big_mac')])
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(service=service)
    await check_transactions_callback_task(
        notification_type=notification_type,
        operation_status=operation_status,
        operation_id=operation_id,
    )
    check_cashback_callback(
        order_id='test_order', service=service, times_called=times_called,
    )
    assert invoice_retrieve_mock.times_called == 1
