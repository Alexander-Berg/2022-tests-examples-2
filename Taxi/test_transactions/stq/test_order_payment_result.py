import pytest

from transactions.stq import order_payment_result


async def test_on_clear(stq3_context, stq):
    with stq.flushing():
        await _call_task(stq3_context, 'clear')
        _assert_called_update_transactions(stq)


@pytest.mark.config(
    NOTIFY_UPDATE_TRANSACTIONS_OF_COMPLETE_OPERATION=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_on_operation_id_config_enabled(stq3_context, stq):
    with stq.flushing():
        await _call_task(stq3_context, 'some_operation_id')
        _assert_called_update_transactions(stq)


@pytest.mark.parametrize(
    ['notification_type', 'expected_has_calls'],
    [('operation_finish', False), ('transaction_clear', True)],
)
async def test_call_on_operation_id_notification_type(
        stq3_context, stq, notification_type, expected_has_calls,
):
    with stq.flushing():
        await _call_task(
            stq3_context,
            'some_operation_id',
            notification_type=notification_type,
        )
        assert stq.update_transactions.has_calls == expected_has_calls


async def _call_task(
        stq3_context,
        operation_id: str,
        notification_type: str = 'transaction_clear',
):
    await order_payment_result.task(
        stq3_context, 'some_order_id', operation_id, 'done', notification_type,
    )


def _assert_called_update_transactions(stq):
    assert stq.update_transactions.times_called == 1
    task = stq.update_transactions.next_call()
    assert task['id'] == 'some_order_id'
    assert task['args'] == ['some_order_id']
    assert task['kwargs'] == {'log_extra': None}
