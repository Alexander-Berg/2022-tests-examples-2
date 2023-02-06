# pylint: disable=import-error
# pylint: disable=too-many-lines

import pytest

NOW = '2022-05-05T12:00:00+00:00'


@pytest.mark.now(NOW)
@pytest.mark.parametrize(
    'order_update_time, invoice_retrieve_times_called',
    [
        pytest.param('2022-05-05T11:59:00+00:00', 0, id='wait'),
        pytest.param('2022-05-05T11:50:00+00:00', 1, id='cancel'),
    ],
)
async def test_create_operation(
        stq_runner,
        upsert_order_payment,
        update_payment_time,
        insert_operation,
        order_update_time,
        invoice_retrieve_times_called,
        mock_transactions_invoice_retrieve,
        upsert_order,
):
    upsert_order('test_order')
    upsert_order_payment(
        order_id='test_order',
        payment_id='test_payment_id',
        payment_type='card',
        currency='RUB',
    )

    update_payment_time('test_order', order_update_time)

    insert_operation(
        'test_order', '123456', '123456', 'create', 'in_progress', 0,
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        status='cleared',
        operations=[],
        service='eda',
        cleared=[],
        transactions=[],
        personal_email_id='personal-email-id',
    )

    kwargs = {'order_id': 'test_order'}
    await stq_runner.eats_payments_check_cancel.call(
        task_id=f'test_order', kwargs=kwargs, exec_tries=0,
    )

    assert invoice_retrieve_mock.times_called == invoice_retrieve_times_called
