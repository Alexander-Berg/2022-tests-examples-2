# pylint: disable=invalid-name

import datetime

import pytest

from corp_notices.events import db as events_db
from corp_notices.events import models as events_models
from corp_notices.events.events import contract_threshold_updated
from corp_notices.notices import db as notices_db
from corp_notices.notices import models as notices_models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = pytest.mark.now(NOW.isoformat())


async def test_registry(stq3_context):
    from corp_notices.events import registry
    assert registry.get('ContractThresholdUpdated')


async def test_big_quasi_notice_enqueue(stq3_context):

    client_id = 'client_id_1'
    event_data = {
        'client_id': client_id,
        'contract_id': 10101,
        'old': {'threshold': '500', 'threshold_type': 'standart'},
        'new': {'threshold': '-50', 'threshold_type': 'big_quasi'},
    }

    broker = contract_threshold_updated.ContractThresholdUpdatedBroker.make(
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
            event_name='ContractThresholdUpdated',
            event_data=event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(
        stq3_context, 'client_id_1',
    )

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='BigQuasiNotice',
            client_id='client_id_1',
            send_at=NOW,
            notice_kwargs=None,
        ),
    ]


@pytest.mark.parametrize(
    'event_data',
    [
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 10101,
                'old': {'threshold': '500', 'threshold_type': 'standart'},
                'new': {'threshold': '-50', 'threshold_type': 'quasi'},
            },
            id='threshold type not big quasi',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 10101,
                'old': {'threshold': '500', 'threshold_type': 'big_quasi'},
                'new': {'threshold': '-50', 'threshold_type': 'big_quasi'},
            },
            id='threshold type not changed',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 10101,
                'old': {'threshold': None, 'threshold_type': None},
                'new': {'threshold': None, 'threshold_type': None},
            },
            id='threshold type not exists',
        ),
    ],
)
async def test_big_quasi_notice_not_enqueue(
        stq3_context, mock_corp_clients, event_data,
):
    client_id = event_data['client_id']

    broker = contract_threshold_updated.ContractThresholdUpdatedBroker.make(
        stq3_context, event_data=event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert len(events) == 1

    notices = await notices_db.fetch_client_notices(
        stq3_context, 'client_id_1',
    )
    assert not notices
