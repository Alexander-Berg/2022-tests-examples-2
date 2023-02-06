import datetime
from typing import Optional

import dateutil
import pytest

from test_transactions import helpers
from transactions.generated.stq3 import stq_context
from transactions.stq import store_error


_UTC_TIMEZONE = dateutil.tz.gettz('UTC')
_MSK_TIMEZONE = dateutil.tz.gettz('Europe/Moscow')
_NOW = datetime.datetime(2021, 1, 1, 21, 0)
_AWARE_NOW = _NOW.replace(tzinfo=_UTC_TIMEZONE).astimezone(_MSK_TIMEZONE)
_AWARE_START_OF_DAY = datetime.datetime(2021, 1, 2, tzinfo=_MSK_TIMEZONE)
_AWARE_END_OF_DAY = datetime.datetime(2021, 1, 3, tzinfo=_MSK_TIMEZONE)
_DELAY = datetime.timedelta(seconds=300)


def _error_data_stub(
        operation_id: Optional[str] = None,
        action_type: Optional[str] = None,
        refund_id: Optional[str] = None,
):
    termination_context = {
        'transactions_scope': 'taxi',
        'invoice_id': 'invoice-id',
        'error_kind': 'hanging_transaction',
        'gateway_name': 'trust',
        'service': 'taxi',
        'transaction_id': 'transaction-id',
        'gateway_response': {'foo': 'bar'},
    }
    data = {
        'id': 'error-2',
        'terminated_at': _NOW,
        'termination_context': termination_context,
    }
    if operation_id is not None:
        data['operation_id'] = operation_id
    if action_type is not None:
        termination_context['action_type'] = action_type
    if refund_id is not None:
        termination_context['refund_id'] = refund_id
    return data


def _error_event_stub(
        operation_id: Optional[str] = None,
        action_type: Optional[str] = None,
        refund_id: Optional[str] = None,
):
    termination_context = {
        'error_kind': 'hanging_transaction',
        'gateway_name': 'trust',
        'gateway_response': {'foo': 'bar'},
        'invoice_id': 'invoice-id',
        'service': 'taxi',
        'transaction_id': 'transaction-id',
        'transactions_scope': 'taxi',
    }
    data = {
        'error_id': 'error-2',
        'invoice_id': 'invoice-id',
        'kind': 'hanging_transaction',
        'scope': 'taxi',
        'terminated_at': _NOW,
        'termination_context': termination_context,
        'timezone': 'Europe/Moscow',
    }
    if operation_id is not None:
        data['operation_id'] = operation_id
    if action_type is not None:
        termination_context['action_type'] = action_type
    if refund_id is not None:
        termination_context['refund_id'] = refund_id
    return {
        'created_at': _NOW,
        'data': data,
        'idempotency_token': 'error-2',
        'kind': 'error',
        'topic': 'errors/taxi/hanging_transaction/2021-01-02',
    }


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'error_data, expected_error_event',
    [
        (
            _error_data_stub(
                operation_id='op-id-2',
                action_type='clear',
                refund_id='refund-id',
            ),
            _error_event_stub(
                operation_id='op-id-2',
                action_type='clear',
                refund_id='refund-id',
            ),
        ),
        (_error_data_stub(), _error_event_stub()),
    ],
)
async def test_store_error(
        stq3_context: stq_context.Context,
        stq,
        error_data,
        expected_error_event,
):
    await _run_task(stq3_context, error_data=error_data)
    cursor = stq3_context.transactions.invoice_events.find()
    events = await cursor.to_list(None)
    assert len(events) == 1
    event = events[0]
    event.pop('_id')
    event.pop('updated_at')
    assert event == expected_error_event


async def _run_task(context, error_data):
    await store_error.task(
        context,
        helpers.create_task_info(queue='transactions_store_error'),
        error_data,
        log_extra=None,
    )
