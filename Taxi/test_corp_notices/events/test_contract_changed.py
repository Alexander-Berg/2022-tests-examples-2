# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import datetime

import pytest

from corp_notices.events import db as events_db
from corp_notices.events import models as events_models
from corp_notices.events.events import contract_changed
from corp_notices.notices import db as notices_db
from corp_notices.notices import models as notices_models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = pytest.mark.now(NOW.isoformat())


async def test_registry(stq3_context):
    from corp_notices.events import registry
    assert registry.get('ContractChanged')


@pytest.mark.parametrize(
    ('event_data', 'expected_notices', 'service_name'),
    [
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': False,
                    'is_offer': False,
                    'is_active': False,
                    'payment_type': 'prepaid',
                },
                'new': {
                    'offer_accepted_common': False,
                    'is_offer': False,
                    'is_active': True,
                    'payment_type': 'prepaid',
                },
            },
            [
                {
                    'CargoContractActivatedFromManagerNotice': {
                        'request_id': 'request_id_1',
                        'login': 'test_login',
                        'encrypted_password': 'some_aes_string',
                        'offer_contract_type': 'postpaid',
                        'contract_service': 'cargo',
                    },
                },
            ],
            'cargo',
            id='cargo activated',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': False,
                    'is_offer': False,
                    'is_active': False,
                    'payment_type': 'prepaid',
                },
                'new': {
                    'offer_accepted_common': False,
                    'is_offer': False,
                    'is_active': True,
                    'payment_type': 'prepaid',
                },
            },
            [
                {
                    'TaxiContractActivatedFromManagerNotice': {
                        'request_id': 'request_id_1',
                        'login': 'test_login',
                        'encrypted_password': 'some_aes_string',
                        'offer_contract_type': 'postpaid',
                        'contract_service': 'taxi',
                    },
                },
            ],
            'taxi',
            id='taxi activated',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': False,
                    'is_offer': True,
                    'is_active': False,
                    'payment_type': 'prepaid',
                },
                'new': {
                    'offer_accepted_common': True,
                    'is_offer': True,
                    'is_active': False,
                    'payment_type': 'prepaid',
                },
            },
            [
                {'PrepaidFirstTakeARideNotice': None},
                {'PrepaidSecondTakeARideNotice': None},
            ],
            'taxi',
            id='offer accepted',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': None,
                    'is_offer': None,
                    'is_active': None,
                    'payment_type': None,
                },
                'new': {
                    'offer_accepted_common': False,
                    'is_offer': False,
                    'is_active': False,
                    'payment_type': 'prepaid',
                },
            },
            [
                {'FirstRemindPrepaidNotice': None},
                {'SecondRemindPrepaidNotice': None},
                {'ThirdRemindPrepaidNotice': None},
            ],
            'taxi',
            id='new_contract',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': None,
                    'is_offer': None,
                    'is_active': None,
                    'payment_type': None,
                },
                'new': {
                    'offer_accepted_common': False,
                    'is_offer': True,
                    'is_active': False,
                    'payment_type': 'prepaid',
                },
            },
            [
                {'FirstRemindPrepaidNotice': None},
                {'SecondRemindPrepaidNotice': None},
                {'ThirdRemindOfferNotice': None},
            ],
            'taxi',
            id='new_contract (is_offer)',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': None,
                    'is_offer': None,
                    'is_active': None,
                    'payment_type': None,
                },
                'new': {
                    'offer_accepted_common': True,
                    'is_offer': True,
                    'is_active': False,
                    'payment_type': 'prepaid',
                },
            },
            [
                {'PrepaidFirstTakeARideNotice': None},
                {'PrepaidSecondTakeARideNotice': None},
            ],
            'taxi',
            id='new_contract (offer_accepted)',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': None,
                    'is_offer': None,
                    'is_active': None,
                    'payment_type': None,
                },
                'new': {
                    'offer_accepted_common': False,
                    'is_offer': False,
                    'is_active': True,
                    'payment_type': 'prepaid',
                },
            },
            [
                {'FirstRemindPrepaidNotice': None},
                {'SecondRemindPrepaidNotice': None},
                {'ThirdRemindPrepaidNotice': None},
                {
                    'TaxiContractActivatedFromManagerNotice': {
                        'request_id': 'request_id_1',
                        'login': 'test_login',
                        'encrypted_password': 'some_aes_string',
                        'offer_contract_type': 'postpaid',
                        'contract_service': 'taxi',
                    },
                },
            ],
            'taxi',
            id='new_contract (manager_request_accepted)',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': None,
                    'is_offer': None,
                    'is_active': None,
                    'payment_type': None,
                },
                'new': {
                    'offer_accepted_common': True,
                    'is_offer': True,
                    'is_active': True,
                    'payment_type': 'prepaid',
                },
            },
            [
                {'PrepaidFirstTakeARideNotice': None},
                {'PrepaidSecondTakeARideNotice': None},
                {
                    'TaxiContractActivatedFromManagerNotice': {
                        'request_id': 'request_id_1',
                        'login': 'test_login',
                        'encrypted_password': 'some_aes_string',
                        'offer_contract_type': 'postpaid',
                        'contract_service': 'taxi',
                    },
                },
            ],
            'taxi',
            id='new_contract (all)',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': None,
                    'is_offer': None,
                    'is_active': None,
                    'payment_type': None,
                },
                'new': {
                    'offer_accepted_common': False,
                    'is_offer': False,
                    'is_active': False,
                    'payment_type': 'postpaid',
                },
            },
            [],
            'taxi',
            id='new_contract (postpaid)',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': False,
                    'is_offer': False,
                    'is_active': False,
                    'payment_type': 'postpaid',
                },
                'new': {
                    'offer_accepted_common': False,
                    'is_offer': False,
                    'is_active': False,
                    'payment_type': 'postpaid',
                },
            },
            [],
            'taxi',
            id='nothing happened',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': True,
                    'is_offer': True,
                    'is_active': True,
                    'payment_type': 'prepaid',
                },
                'new': {
                    'offer_accepted_common': True,
                    'is_offer': True,
                    'is_active': False,
                    'payment_type': 'prepaid',
                },
            },
            [],
            'taxi',
            id='nothing happened (to_inactive)',
        ),
        pytest.param(
            {
                'client_id': 'client_id_1',
                'contract_id': 12345,
                'old': {
                    'offer_accepted_common': True,
                    'is_offer': True,
                    'is_active': True,
                    'payment_type': 'prepaid',
                },
                'new': {
                    'offer_accepted_common': True,
                    'is_offer': True,
                    'is_active': False,
                    'payment_type': 'prepaid',
                },
            },
            [],
            'taxi',
            id='nothing happened (to_inactive)',
        ),
    ],
)
async def test_contract_changed(
        stq3_context,
        mock_corp_requests,
        mock_corp_clients,
        load_json,
        event_data,
        expected_notices,
        service_name,
):
    manager_request_response = load_json('manager_request_response.json')
    manager_request_response['service'] = service_name
    contracts_response = load_json('contracts_response.json')

    mock_corp_requests.data.man_requests_byclientids = [
        manager_request_response,
    ]
    mock_corp_clients.data.get_contracts_response = contracts_response

    client_id = event_data['client_id']

    broker = contract_changed.ContractChangedEventBroker.make(
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
            event_name='ContractChanged',
            event_data=event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)
    assert len(notices) == len(expected_notices)

    for i, notice in enumerate(notices):
        expected_notice = None
        for notice_name in expected_notices:
            if notice.notice_name == list(notice_name.keys()).pop():
                expected_notice = list(notice_name.items()).pop()

        assert expected_notice is not None
        assert notice == notices_models.Notice(
            id=i + 1,
            event_id=1,
            status=notices_models.Status.pending,
            notice_name=expected_notice[0],
            client_id=client_id,
            send_at=NOW,
            notice_kwargs=expected_notice[1],
        )


async def test_contract_changed_dequeue_remind(
        stq3_context, mock_corp_requests, mock_corp_clients, load_json,
):
    client_id = 'client_id_1'

    await events_db.insert(
        stq3_context,
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='ContractCreated',
            event_data={},
        ),
    )

    await notices_db.insert(
        stq3_context,
        notices_models.Notice(
            id=1,
            event_id=1,
            status=notices_models.Status.pending,
            notice_name='FirstRemindPrepaidNotice',
            client_id=client_id,
            send_at=NOW + datetime.timedelta(days=3),
            notice_kwargs=None,
        ),
    )

    manager_request_response = load_json('manager_request_response.json')
    contracts_response = load_json('contracts_response.json')

    mock_corp_requests.data.man_requests_byclientids = [
        manager_request_response,
    ]
    mock_corp_clients.data.get_contracts_response = contracts_response

    event_data = {
        'client_id': 'client_id_1',
        'contract_id': 12345,
        'old': {
            'offer_accepted_common': False,
            'is_offer': True,
            'is_active': False,
            'payment_type': 'prepaid',
        },
        'new': {
            'offer_accepted_common': True,
            'is_offer': True,
            'is_active': False,
            'payment_type': 'prepaid',
        },
    }

    broker = contract_changed.ContractChangedEventBroker.make(
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
            event_name='ContractCreated',
            event_data={},
        ),
        events_models.Event(
            id=2,
            client_id=client_id,
            event_name='ContractChanged',
            event_data=event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=1,
            status=notices_models.Status.dequeued,
            notice_name='FirstRemindPrepaidNotice',
            client_id='client_id_1',
            send_at=NOW + datetime.timedelta(days=3),
            notice_kwargs=None,
        ),
        notices_models.Notice(
            id=2,
            event_id=events[1].id,
            status=notices_models.Status.pending,
            notice_name='PrepaidFirstTakeARideNotice',
            client_id='client_id_1',
            send_at=NOW,
            notice_kwargs=None,
        ),
        notices_models.Notice(
            id=3,
            event_id=events[1].id,
            status=notices_models.Status.pending,
            notice_name='PrepaidSecondTakeARideNotice',
            client_id='client_id_1',
            send_at=NOW,
            notice_kwargs=None,
        ),
    ]
