# pylint: disable=redefined-outer-name,unused-variable

import datetime as dt

import pytest

from taxi.stq import async_worker_ng as async_worker

from transactions.models import invoice_operations
from transactions.stq import compensation_events_handler
from transactions.stq import events_handler
from . import _assertions

_NOW_DATETIME = dt.datetime(2019, 6, 3, 12, 0)
_NOW = _NOW_DATETIME.isoformat()


@pytest.mark.parametrize(
    'queue',
    [
        'transactions_events',
        'transactions_events_hold',
        'transactions_compensation_events',
    ],
)
@pytest.mark.nofilldb
@pytest.mark.now(_NOW)
async def test_soft_race_condition(
        stq3_context,
        stq,
        iteration_raises_race_condition,
        compensation_raises_race_condition,
        stq_reschedule,
        patch_random,
        queue,
):
    with stq.flushing():
        task_info = _build_task_info(queue)
        await _call_queue_task(stq3_context, queue, task_info)
        _assertions.assert_rescheduled_at(
            stq_reschedule,
            dt.datetime(2019, 6, 3, 12, 0, 0, 500000),
            _NOW_DATETIME,
        )


@pytest.mark.config(
    TRANSACTIONS_SOFT_RACE_CONDITIONS={
        'num_soft_reschedules': 0,
        'min_delay': 1,
        'max_delay': 1,
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.parametrize(
    'queue',
    [
        'transactions_events',
        'transactions_events_hold',
        'transactions_compensation_events',
    ],
)
@pytest.mark.nofilldb
@pytest.mark.now(_NOW)
async def test_hard_race_condition(
        stq3_context,
        stq,
        iteration_raises_race_condition,
        compensation_raises_race_condition,
        stq_reschedule,
        patch_random,
        queue,
):
    with stq.flushing():
        task_info = _build_task_info(queue)
        with pytest.raises(invoice_operations.RaceCondition):
            await _call_queue_task(stq3_context, queue, task_info)


def _build_task_info(queue) -> async_worker.TaskInfo:
    return async_worker.TaskInfo(
        id='some_invoice_id', exec_tries=0, reschedule_counter=0, queue=queue,
    )


@pytest.fixture
def iteration_raises_race_condition(patch):
    iteration = 'transactions.stq.events_handler.invoice_processing_iteration'

    @patch(iteration)
    async def invoice_processing_iteration(
            context, task_info, invoice_id, log_extra=None,
    ):
        raise invoice_operations.RaceCondition


@pytest.fixture
def compensation_raises_race_condition(patch):
    # pylint: disable=invalid-name
    iteration = (
        'transactions.stq.compensation_events_handler.'
        'compensation_processing_iteration'
    )

    @patch(iteration)
    async def compensation_processing_iteration(
            context, invoice_id, log_extra=None,
    ):
        raise invoice_operations.RaceCondition


async def _call_queue_task(stq3_context, queue, task_info):

    if queue in ['transactions_events', 'transactions_events_hold']:
        function = events_handler.task
    elif queue == 'transactions_compensation_events':
        function = compensation_events_handler.task
    else:
        raise RuntimeError(f'unknown queue: {queue}')
    await function(
        context=stq3_context,
        task_info=task_info,
        invoice_id='some_invoice_id',
        log_extra=None,
    )


@pytest.fixture
def patch_random(patch):
    @patch('random.random')
    def random():
        return 0
