# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import datetime

import pytest

from corp_notices.events import db as events_db
from corp_notices.events import models as events_models
from corp_notices.events.events import (
    client_request_status_changed as request_changed,
)
from corp_notices.notices import db as notices_db
from corp_notices.notices import models as notices_models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = pytest.mark.now(NOW.isoformat())


@pytest.fixture
def ok_event_data():
    return {
        'request_id': 'rus_id',
        'old': {'status': 'pending'},
        'new': {'status': 'accepted'},
    }


@pytest.fixture
def reject_event_data():
    return {
        'request_id': 'isr_id',
        'old': {'status': 'pending'},
        'new': {'status': 'rejected', 'reject_reason': 'some reason'},
    }


async def test_registry(stq3_context):
    from corp_notices.events import registry
    assert registry.get('ClientRequestStatusChanged')


async def test_ok_client_status_changed_notice_enqueue(
        stq3_context, mock_corp_requests, ok_event_data, load_json,
):
    client_request_response = load_json('client_request_response.json')

    mock_corp_requests.data.get_client_request_response = (
        client_request_response
    )
    client_id = client_request_response['client_id']

    broker = request_changed.ClientRequestStatusChangedEventBroker.make(
        stq3_context, event_data=ok_event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='ClientRequestStatusChanged',
            event_data=ok_event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='ClientRequestAcceptedNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs={'contract_type': 'taxi'},
        ),
        notices_models.Notice(
            id=2,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='OfferScoringNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs={
                'contract_type': 'taxi',
                'client_id': 'rus_client_id',
                'request_id': 'rus_id',
                'inn': '1503009019',
                'yandex_login': 'osiei13',
            },
        ),
    ]


async def test_rejected_client_status_changed_notice_enqueue(
        stq3_context, mock_corp_requests, reject_event_data, load_json,
):
    client_request_response = load_json('client_request_response.json')

    mock_corp_requests.data.get_client_request_response = (
        client_request_response
    )
    client_id = client_request_response['client_id']

    broker = request_changed.ClientRequestStatusChangedEventBroker.make(
        stq3_context, event_data=reject_event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='ClientRequestStatusChanged',
            event_data=reject_event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='ClientRequestRejectedNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs={
                'contract_type': 'taxi',
                'reject_reason': 'some reason',
                'locale': 'rus',
            },
        ),
    ]
