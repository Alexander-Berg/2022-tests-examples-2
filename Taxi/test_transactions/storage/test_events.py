import dataclasses
import datetime
from typing import Optional

import bson
import pytest

from transactions.storage import events as events_storage
from transactions.usecases import store_error


_CREATED_AT = datetime.datetime(2021, 2, 7, 18, 27)
_FINISHED_AT = datetime.datetime(2021, 2, 7, 19, 12)
_EXISTING_CREATED_AT = datetime.datetime(2021, 2, 7, 19, 21)
_EXISTING_FINISHED_AT = datetime.datetime(2021, 2, 7, 19, 23)
_WILL_BE_UPDATED_IN_TEST = None


def _event_stub(
        topic: Optional[str] = None,
        idempotency_token: Optional[str] = None,
        event_id: Optional[bson.ObjectId] = None,
        finished_at: Optional[datetime.datetime] = None,
) -> store_error.Event:
    return store_error.Event(
        topic=topic or 'topic',
        idempotency_token=idempotency_token or 'fresh-idempotency-token',
        kind='kind',
        created_at=_CREATED_AT,
        data={'foo': 'bar'},
        event_id=event_id or None,
        finished_at=finished_at or None,
    )


@pytest.mark.parametrize(
    'to_insert, expected_event',
    [
        # without optional fields set
        (_event_stub(), _event_stub(event_id=_WILL_BE_UPDATED_IN_TEST)),
        # with optional fields set
        (
            _event_stub(finished_at=_FINISHED_AT),
            _event_stub(
                event_id=_WILL_BE_UPDATED_IN_TEST, finished_at=_FINISHED_AT,
            ),
        ),
        # event already inserted, expect existing event
        (
            _event_stub(
                topic='existing-topic',
                idempotency_token='existing-idempotency-token',
            ),
            store_error.Event(
                topic='existing-topic',
                idempotency_token='existing-idempotency-token',
                kind='existing-kind',
                created_at=_EXISTING_CREATED_AT,
                data={'baz': 'xyzzy'},
                event_id=bson.ObjectId('000000000000000000000001'),
                finished_at=_EXISTING_FINISHED_AT,
            ),
        ),
    ],
)
@pytest.mark.filldb(taxi_invoice_events='for_test_insert')
async def test_insert(stq3_context, to_insert, expected_event):
    # pylint: disable=protected-access
    repo = events_storage.EventsRepository(stq3_context)
    inserted_event = await repo.insert(event=to_insert)
    assert inserted_event.event_id is not None
    actual_event = dataclasses.replace(
        inserted_event,
        event_id=(
            _WILL_BE_UPDATED_IN_TEST
            if expected_event.event_id == _WILL_BE_UPDATED_IN_TEST
            else inserted_event.event_id
        ),
    )
    assert actual_event == expected_event
