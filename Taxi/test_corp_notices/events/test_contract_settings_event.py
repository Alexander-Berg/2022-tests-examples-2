# pylint: disable=invalid-name

import datetime

import pytest

from corp_notices.events import db as events_db
from corp_notices.events import models as events_models
from corp_notices.events.events import contract_settings_changed
from corp_notices.notices import db as notices_db
from corp_notices.notices import models as notices_models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

MOCK_CONTRACTS_RESPONSE = {
    'contracts': [
        {
            'balances': {},
            'contract_id': 101,
            'external_id': '101/12',
            'billing_client_id': '12345',
            'billing_person_id': '54321',
            'payment_type': 'prepaid',
            'is_offer': False,
            'currency': 'RUB',
            'services': ['taxi'],
            'is_active': True,
            'settings': {'is_active': True},
        },
    ],
}
NOTICE_KWARGS = {'reason': 'notify', 'external_contract_id': '101/12'}

pytestmark = pytest.mark.now(NOW.isoformat())


async def test_registry(stq3_context):
    from corp_notices.events import registry
    assert registry.get('ContractSettingsChanged')


@pytest.mark.parametrize(
    ('event_data', 'service'),
    [
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 101,
                'reason': 'debt',
                'old': {'is_active': True},
                'new': {'is_active': False},
            },
            'Cargo',
            id='cargo debt',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 101,
                'reason': 'notify',
                'old': {'is_active': False},
                'new': {'is_active': True},
            },
            'Taxi',
            id='taxi notify',
        ),
    ],
)
async def test_contract_settings_notice_enqueue(
        stq3_context, mock_corp_clients, event_data, service,
):
    # mock corp_clients 'contracts_get'
    contracts_response = MOCK_CONTRACTS_RESPONSE.copy()
    contracts_response['contracts'][0]['settings']['is_active'] = event_data[
        'old'
    ]['is_active']
    contracts_response['contracts'][0]['services'] = [service.lower()]
    mock_corp_clients.data.get_contracts_response = contracts_response

    # test
    client_id = event_data['client_id']

    broker = contract_settings_changed.ContractSettingsChangedBroker.make(
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
            event_name='ContractSettingsChanged',
            event_data=event_data,
        ),
    ]

    expected_notice_kwargs = NOTICE_KWARGS.copy()
    expected_notice_kwargs.update(reason=event_data['reason'])

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)
    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name=f'{service}ContractActivateNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs=expected_notice_kwargs,
        ),
    ]
