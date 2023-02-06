# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import datetime

import pytest

from corp_notices.events import db as events_db
from corp_notices.events import models as events_models
from corp_notices.events.events import duplicate_trial_client
from corp_notices.notices import db as notices_db
from corp_notices.notices import models as notices_models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = pytest.mark.now(NOW.isoformat())


MOCK_ATTENDANCE_RESPONSE = {
    'attendances': [
        {'yandex_uid': '1234', 'first_seen': None, 'last_seen': None},
    ],
}

MOCK_ATTENDANCE_EMPTY_RESPONSE: dict = {'attendances': []}


@pytest.fixture
def event_data():
    return {
        'client_id': '1234',
        'yandex_login': 'some_login',
        'contract_type': 'taxi',
    }


async def test_registry(stq3_context):
    from corp_notices.events import registry
    assert registry.get('DuplicateTrialClient')


async def test_duplicate_permpass_notice_enqueue(
        stq3_context, mock_corp_clients, event_data,
):

    mock_corp_clients.data.client_attendance_response = (
        MOCK_ATTENDANCE_RESPONSE
    )

    client_id = event_data['client_id']

    broker = duplicate_trial_client.DuplicateTrialClientEventBroker.make(
        stq3_context, event_data=event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='DuplicateTrialClient',
            event_data=event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='DuplicateTrialClientPermPassNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs={
                'yandex_login': 'some_login',
                'contract_type': 'taxi',
            },
        ),
    ]


async def test_duplicate_tmppass_notice_enqueue(
        stq3_context, mock_corp_clients, event_data,
):

    mock_corp_clients.data.client_attendance_response = (
        MOCK_ATTENDANCE_EMPTY_RESPONSE
    )

    client_id = event_data['client_id']

    broker = duplicate_trial_client.DuplicateTrialClientEventBroker.make(
        stq3_context, event_data=event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='DuplicateTrialClient',
            event_data=event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='DuplicateTrialClientTmpPassNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs={
                'yandex_login': 'some_login',
                'contract_type': 'taxi',
            },
        ),
    ]
