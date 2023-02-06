# pylint: disable=invalid-name

import datetime

import pytest

from corp_notices.events import db as events_db
from corp_notices.events import models as events_models
from corp_notices.events.events import balance_changed
from corp_notices.notices import db as notices_db
from corp_notices.notices import models as notices_models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = [
    pytest.mark.now(NOW.isoformat()),
    pytest.mark.config(
        CORP_NOTICES_SETTINGS={
            'LimitIsOverRemindNotice': {
                'enabled': True,
                'days_offset': 3,
                'slugs': {'rus': 'AAAAAA'},
            },
        },
    ),
]


MOCK_CONTRACTS_RESPONSE = {
    'contracts': [
        {
            'balances': {},
            'contract_id': 10101,
            'external_id': '101/01',
            'billing_client_id': '12345',
            'billing_person_id': '54321',
            'payment_type': 'prepaid',
            'is_offer': False,
            'currency': 'RUB',
            'services': ['taxi'],
            'is_active': True,
            'settings': {
                'is_active': True,
                'low_balance_notification_enabled': True,
                'low_balance_threshold': '100',
                'prepaid_deactivate_threshold': '25',
            },
        },
    ],
}


@pytest.fixture(name='low_balance_event_data')
def _low_balance_event_data():
    return {
        'client_id': 'client_id_1',
        'contract_id': 10101,
        'old_balance': '150',
        'new_balance': '50',
    }


@pytest.fixture(name='block_event_data')
def _block_event_data():
    return {
        'client_id': 'client_id_1',
        'contract_id': 10101,
        'old_balance': '150',
        'new_balance': '5',
    }


@pytest.fixture(name='unblock_event_data')
def _unblock_event_data():
    return {
        'client_id': 'client_id_1',
        'contract_id': 10101,
        'old_balance': '5',
        'new_balance': '150',
    }


async def test_registry(stq3_context):
    from corp_notices.events import registry
    assert registry.get('BalanceChanged')


async def test_low_balance_notice_enqueue(
        stq3_context, mock_corp_clients, low_balance_event_data,
):

    mock_corp_clients.data.get_contracts_response = MOCK_CONTRACTS_RESPONSE

    client_id = low_balance_event_data['client_id']

    broker = balance_changed.BalanceChangedEventBroker.make(
        stq3_context, event_data=low_balance_event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='BalanceChanged',
            event_data=low_balance_event_data,
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
            notice_name='LowBalanceNotice',
            client_id='client_id_1',
            send_at=NOW,
            notice_kwargs={
                'contract_id': 10101,
                'external_id': '101/01',
                'old_balance': '150',
                'new_balance': '50',
            },
        ),
    ]


@pytest.mark.parametrize(
    'event_data',
    [
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 10101,
                'old_balance': '150',
                'new_balance': '150',
            },
            id='balance not changed',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 10101,
                'old_balance': '150',
                'new_balance': '120',
            },
            id='balance greater than threshold',
        ),
    ],
)
async def test_low_balance_notice_not_enqueue(
        stq3_context, mock_corp_clients, event_data,
):

    mock_corp_clients.data.get_contracts_response = MOCK_CONTRACTS_RESPONSE

    client_id = event_data['client_id']

    broker = balance_changed.BalanceChangedEventBroker.make(
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


async def test_limit_is_over_notice_enqueue(
        stq3_context, mock_corp_clients, block_event_data,
):

    mock_corp_clients.data.get_contracts_response = MOCK_CONTRACTS_RESPONSE
    client_id = block_event_data['client_id']

    broker = balance_changed.BalanceChangedEventBroker.make(
        stq3_context, event_data=block_event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='BalanceChanged',
            event_data=block_event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(
        stq3_context, 'client_id_1',
    )

    assert len(notices) == 2

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='LimitIsOverNotice',
            client_id='client_id_1',
            send_at=NOW,
            notice_kwargs={
                'contract_id': 10101,
                'external_id': '101/01',
                'old_balance': '150',
                'new_balance': '5',
            },
        ),
        notices_models.Notice(
            id=2,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='LimitIsOverRemindNotice',
            client_id='client_id_1',
            send_at=NOW + datetime.timedelta(days=3),
            notice_kwargs={
                'contract_id': 10101,
                'external_id': '101/01',
                'old_balance': '150',
                'new_balance': '5',
            },
        ),
    ]


async def test_financial_unblock_notice_enqueue(
        stq3_context, mock_corp_clients, unblock_event_data,
):

    mock_corp_clients.data.get_contracts_response = MOCK_CONTRACTS_RESPONSE
    client_id = unblock_event_data['client_id']

    await events_db.insert(
        stq3_context,
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='BalanceChanged',
            event_data={},
        ),
    )

    await notices_db.insert(
        stq3_context,
        notices_models.Notice(
            id=1,
            event_id=1,
            status=notices_models.Status.pending,
            notice_name='LimitIsOverRemindNotice',
            client_id='client_id_1',
            send_at=NOW + datetime.timedelta(days=3),
            notice_kwargs={
                'contract_id': 10101,
                'external_id': '101/01',
                'old_balance': '150',
                'new_balance': '5',
            },
        ),
    )

    broker = balance_changed.BalanceChangedEventBroker.make(
        stq3_context, event_data=unblock_event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='BalanceChanged',
            event_data={},
        ),
        events_models.Event(
            id=2,
            client_id=client_id,
            event_name='BalanceChanged',
            event_data=unblock_event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(
        stq3_context, 'client_id_1',
    )

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=1,
            status=notices_models.Status.dequeued,
            notice_name='LimitIsOverRemindNotice',
            client_id='client_id_1',
            send_at=NOW + datetime.timedelta(days=3),
            notice_kwargs={
                'contract_id': 10101,
                'external_id': '101/01',
                'old_balance': '150',
                'new_balance': '5',
            },
        ),
        notices_models.Notice(
            id=2,
            event_id=events[1].id,
            status=notices_models.Status.pending,
            notice_name='FinancialUnblockNotice',
            client_id='client_id_1',
            send_at=NOW,
            notice_kwargs={
                'contract_id': 10101,
                'external_id': '101/01',
                'old_balance': '5',
                'new_balance': '150',
            },
        ),
    ]
