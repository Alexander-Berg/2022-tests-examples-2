# pylint: disable=too-many-lines
import pytest

from test_transactions import helpers
from transactions.generated.stq3 import stq_context
from transactions.stq import plan_operation

_NOW = '2020-01-01T00:00:00'


@pytest.mark.parametrize(
    'operations_kind, queue_name',
    [
        ('operations', 'transactions_events'),
        ('cashback_operations', 'transactions_cashback_events'),
        ('compensation_operations', 'transactions_compensation_events'),
    ],
)
@pytest.mark.parametrize(
    'data_path',
    [
        'invoice_not_found.json',
        'old_task.json',
        'operation_found.json',
        'operation_not_found_yet.json',
    ],
)
@pytest.mark.config(
    TRANSACTIONS_OPERATION_START_WAIT_INTERVAL=60,
    TRANSACTIONS_PLAN_OPERATION_BACKOFF={'min': 2, 'max': 300},
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now(_NOW)
async def test_invoice_not_found(
        stq3_context: stq_context.Context,
        mockserver,
        load_py_json,
        stq,
        data_path,
        operations_kind,
        queue_name,
):
    @mockserver.json_handler('/stq-agent/queues/api/reschedule')
    def _patch_stq_agent_reschedule(request):
        return {}

    data = load_py_json(data_path)
    future = plan_operation.task(
        stq3_context,
        task_info=helpers.create_task_info(
            queue='some-queue', reschedule_counter=data['reschedule_counter'],
        ),
        invoice_id=data['invoice_id'],
        operation_id=data['operation_id'],
        operations_kind=operations_kind,
        created=data['created'],
    )
    if data['expected_is_failed']:
        with pytest.raises(RuntimeError):
            await future
    else:
        await future
    plan_calls = _get_calls(stq, 'transactions_plan_operation')
    processing_calls = _get_calls(stq, queue_name)
    assert plan_calls == data['expected_plan_calls']
    assert processing_calls == data['expected_processing_calls']


def _get_calls(stq, queue_name):
    queue = getattr(stq, queue_name)
    calls = []
    while queue.has_calls:
        call = queue.next_call()
        assert call['queue'] == queue_name
        del call['queue']
        calls.append(call)
    return calls
