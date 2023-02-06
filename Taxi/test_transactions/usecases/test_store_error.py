# pylint: disable=no-member
import dataclasses
import datetime
from typing import Optional
import unittest.mock

import asynctest
import bson
import dateutil
import pytest

from transactions.models import termination
from transactions.usecases import store_error


_ID = bson.ObjectId('000000000000000000000000')
_UTC_TIMEZONE = dateutil.tz.gettz('UTC')
_MSK_TIMEZONE = dateutil.tz.gettz('Europe/Moscow')
_NOW = datetime.datetime(2021, 2, 6, 6, 34)
_AWARE_NOW = _NOW.replace(tzinfo=_UTC_TIMEZONE).astimezone(_MSK_TIMEZONE)
_AWARE_START_OF_DAY = datetime.datetime(2021, 2, 6, tzinfo=_MSK_TIMEZONE)
_AWARE_END_OF_DAY = datetime.datetime(2021, 2, 7, tzinfo=_MSK_TIMEZONE)
_DELAY = datetime.timedelta(seconds=300)


def _error_stub(
        operation_id: Optional[str] = 'operation-id',
        refund_id: Optional[str] = 'refund_id',
        action_type: Optional[str] = 'clear',
) -> store_error.Error:
    return store_error.Error(
        error_id='error-id',
        operation_id=operation_id,
        terminated_at=_NOW,
        termination_context=termination.TerminationContext(
            transactions_scope='taxi',
            invoice_id='invoice-id',
            action_type=action_type,
            error_kind='hanging_transaction',
            gateway_name='trust',
            service='taxi',
            transaction_id='transaction-id',
            refund_id=refund_id,
            gateway_response={'foo': 'bar'},
        ),
    )


def _error_event_stub(
        topic: Optional[str] = None,
        operation_id: Optional[str] = 'operation-id',
        refund_id: Optional[str] = 'refund_id',
        action_type: Optional[str] = 'clear',
) -> store_error.Event:
    termination_context = {
        'transactions_scope': 'taxi',
        'invoice_id': 'invoice-id',
        'error_kind': 'hanging_transaction',
        'gateway_name': 'trust',
        'transaction_id': 'transaction-id',
        'gateway_response': {'foo': 'bar'},
        'service': 'taxi',
    }
    data = {
        'scope': 'taxi',
        'invoice_id': 'invoice-id',
        'error_id': 'error-id',
        'kind': 'hanging_transaction',
        'terminated_at': _NOW,
        'timezone': 'Europe/Moscow',
        'termination_context': termination_context,
    }
    if operation_id is not None:
        data['operation_id'] = operation_id
    if refund_id is not None:
        termination_context['refund_id'] = refund_id
    if action_type is not None:
        termination_context['action_type'] = action_type
    return store_error.Event(
        topic=topic or 'errors/taxi/hanging_transaction/error-id',
        idempotency_token='error-id',
        kind='error',
        created_at=_AWARE_NOW,
        data=data,
        event_id=None,
        finished_at=None,
    )


def _notification_stub(
        error_topic: Optional[str] = None,
        aggregation_period: Optional[store_error.AggregationPeriod] = None,
        eta: Optional[datetime.datetime] = None,
) -> store_error.Notification:
    return store_error.Notification(
        error_kind='hanging_transaction',
        error_scope='taxi',
        error_topic=error_topic or 'errors/taxi/hanging_transaction/error-id',
        timezone='Europe/Moscow',
        aggregation_period=aggregation_period,
        batch_number=1,
        eta=eta or (_AWARE_NOW + _DELAY),
    )


@pytest.mark.nofilldb()
@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'error, period_kind, expected_error_event, expected_notification',
    [
        (
            _error_stub(),
            store_error.PeriodKind.NONE,
            _error_event_stub(),
            _notification_stub(),
        ),
        (
            _error_stub(),
            store_error.PeriodKind.DAILY,
            _error_event_stub(
                topic='errors/taxi/hanging_transaction/2021-02-06',
            ),
            _notification_stub(
                error_topic='errors/taxi/hanging_transaction/2021-02-06',
                aggregation_period=store_error.AggregationPeriod(
                    kind=store_error.PeriodKind.DAILY,
                    key='2021-02-06',
                    start=_AWARE_START_OF_DAY,
                    end=_AWARE_END_OF_DAY,
                ),
                eta=_AWARE_END_OF_DAY + _DELAY,
            ),
        ),
        (
            _error_stub(operation_id=None, refund_id=None, action_type=None),
            store_error.PeriodKind.DAILY,
            _error_event_stub(
                topic='errors/taxi/hanging_transaction/2021-02-06',
                operation_id=None,
                refund_id=None,
                action_type=None,
            ),
            _notification_stub(
                error_topic='errors/taxi/hanging_transaction/2021-02-06',
                aggregation_period=store_error.AggregationPeriod(
                    kind=store_error.PeriodKind.DAILY,
                    key='2021-02-06',
                    start=_AWARE_START_OF_DAY,
                    end=_AWARE_END_OF_DAY,
                ),
                eta=_AWARE_END_OF_DAY + _DELAY,
            ),
        ),
    ],
)
async def test_store_error_happy_path(
        error, period_kind, expected_error_event, expected_notification,
):
    events_repo = asynctest.Mock(spec=store_error.EventsRepository)
    events_repo.insert.side_effect = lambda event: dataclasses.replace(
        event, event_id=_ID,
    )
    scheduler = asynctest.Mock(spec=store_error.Scheduler)
    config = asynctest.Mock(spec=store_error.Config)
    config.get_aggregation_period_kind.return_value = period_kind
    config.get_error_notification_delay.return_value = _DELAY
    usecase = store_error.StoreErrorUseCase(
        events_repo=events_repo, scheduler=scheduler, config=config,
    )
    await usecase(error=error)

    # Check that we inserted error into storage
    assert events_repo.insert.call_count == 1
    assert events_repo.insert.call_args == unittest.mock.call(
        event=expected_error_event,
    )

    # Check that we consulted config
    assert config.get_aggregation_period_kind.call_count == 1
    assert config.get_error_notification_delay.call_count == 1

    # Check that correct notification is scheduled
    assert scheduler.schedule_error_notification.call_count == 1
    assert (
        scheduler.schedule_error_notification.call_args
        == unittest.mock.call(notification=expected_notification)
    )
