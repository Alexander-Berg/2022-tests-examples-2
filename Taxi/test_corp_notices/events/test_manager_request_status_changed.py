# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import datetime

import pytest

from corp_notices.events import db as events_db
from corp_notices.events import models as events_models
from corp_notices.events.events import (
    manager_request_status_changed as manager_broker,
)
from corp_notices.notices import db as notices_db
from corp_notices.notices import models as notices_models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = pytest.mark.now(NOW.isoformat())


MOCK_STAFF_RESPONSE = {
    'result': [
        {
            'name': {
                'middle': '',
                'has_namesake': False,
                'first': {'ru': 'Иван', 'en': 'Ivan'},
                'last': {'ru': 'Иванов', 'en': 'Ivanov'},
                'hidden_middle': True,
            },
        },
    ],
    'extra': {},
}


@pytest.fixture
def accepted_event_data():
    return {
        'request_id': 'request_id_1',
        'old': {'status': 'pending'},
        'new': {'status': 'accepted'},
    }


@pytest.fixture
def rejected_event_data():
    return {
        'request_id': 'request_id_1',
        'old': {'status': 'pending'},
        'new': {'status': 'rejected', 'reason': 'потому что'},
    }


async def test_registry(stq3_context):
    from corp_notices.events import registry
    assert registry.get('ManagerRequestStatusChanged')


@pytest.mark.parametrize(
    ('service_name', 'expected_notice_name'),
    [
        pytest.param('cargo', 'CargoManagerRequestAcceptedNotice', id='cargo'),
        pytest.param('taxi', 'TaxiManagerRequestAcceptedNotice', id='taxi'),
    ],
)
async def test_manager_request_accepted_notice_enqueue(
        stq3_context,
        mock_corp_requests,
        mock_staff,
        accepted_event_data,
        load_json,
        service_name,
        expected_notice_name,
):
    manager_request_response = load_json('manager_request_response.json')
    manager_request_response['service'] = service_name

    mock_corp_requests.data.get_manager_request_response = (
        manager_request_response
    )
    mock_staff.data.get_persons_response = MOCK_STAFF_RESPONSE

    broker = manager_broker.ManagerRequestStatusChangedEventBroker.make(
        stq3_context, event_data=accepted_event_data,
    )

    await broker.process()

    events = await events_db.fetch_named_events(
        stq3_context, name='ManagerRequestStatusChanged',
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=None,
            event_name='ManagerRequestStatusChanged',
            event_data=accepted_event_data,
        ),
    ]

    notices = await notices_db.fetch_named_notices(
        stq3_context, name=expected_notice_name,
    )

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name=expected_notice_name,
            client_id=None,
            send_at=NOW,
            notice_kwargs={
                'manager_login': manager_request_response['manager_login'],
                'status': manager_request_response['status'],
                'manager_name': 'Иван Иванов @r1_manager_login',
                'country': manager_request_response['country'],
                'service': service_name,
                'enterprise_name_short': manager_request_response[
                    'enterprise_name_short'
                ],
                'enterprise_name_full': manager_request_response[
                    'enterprise_name_full'
                ],
                'contract_type': manager_request_response['contract_type'],
                'company_tin': manager_request_response['company_tin'],
                'company_cio': manager_request_response['company_cio'],
                'kbe': manager_request_response['kbe'],
                'city': '',
                'legal_address': manager_request_response['legal_address'],
                'mailing_address': manager_request_response['mailing_address'],
                'contacts': manager_request_response['contacts'],
                'bank_account_number': manager_request_response[
                    'bank_account_number'
                ],
                'bank_name': '',
                'bank_bic': manager_request_response['bank_bic'],
                'signer_name': manager_request_response['signer_name'],
                'signer_position': manager_request_response['signer_position'],
                'signer_duly_authorized': manager_request_response[
                    'signer_duly_authorized'
                ],
                'attachments': manager_request_response['attachments'],
                'crm_link': manager_request_response.get('crm_link', ''),
                'st_link': manager_request_response['st_link'],
                'client_login': manager_request_response['client_login'],
                'billing_external_id': manager_request_response[
                    'billing_external_id'
                ],
                'billing_client_id': manager_request_response[
                    'billing_client_id'
                ],
                'billing_person_id': manager_request_response[
                    'billing_person_id'
                ],
                'billing_contract_id': manager_request_response[
                    'billing_contract_id'
                ],
                'additional_information': manager_request_response[
                    'additional_information'
                ],
            },
        ),
    ]

    await broker.process()


@pytest.mark.parametrize(
    ('service_name', 'expected_notice_name'),
    [
        pytest.param('cargo', 'CargoManagerRequestRejectedNotice', id='cargo'),
        pytest.param('taxi', 'TaxiManagerRequestRejectedNotice', id='taxi'),
    ],
)
async def test_manager_request_rejected_notice_enqueue(
        stq3_context,
        mock_corp_requests,
        mock_staff,
        rejected_event_data,
        load_json,
        service_name,
        expected_notice_name,
):
    manager_request_response = load_json('manager_request_response.json')
    manager_request_response['service'] = service_name

    mock_corp_requests.data.get_manager_request_response = (
        manager_request_response
    )
    mock_staff.data.get_persons_response = MOCK_STAFF_RESPONSE

    broker = manager_broker.ManagerRequestStatusChangedEventBroker.make(
        stq3_context, event_data=rejected_event_data,
    )

    await broker.process()

    events = await events_db.fetch_named_events(
        stq3_context, name='ManagerRequestStatusChanged',
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=None,
            event_name='ManagerRequestStatusChanged',
            event_data=rejected_event_data,
        ),
    ]

    notices = await notices_db.fetch_named_notices(
        stq3_context, name=expected_notice_name,
    )

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name=expected_notice_name,
            client_id=None,
            send_at=NOW,
            notice_kwargs={
                'manager_login': manager_request_response['manager_login'],
                'status': manager_request_response['status'],
                'reason': rejected_event_data['new']['reason'],
                'country': manager_request_response['country'],
                'service': service_name,
                'enterprise_name_short': manager_request_response[
                    'enterprise_name_short'
                ],
                'enterprise_name_full': manager_request_response[
                    'enterprise_name_full'
                ],
                'contract_type': manager_request_response['contract_type'],
                'company_tin': manager_request_response['company_tin'],
                'company_cio': manager_request_response['company_cio'],
                'kbe': manager_request_response['kbe'],
                'city': '',
                'legal_address': manager_request_response['legal_address'],
                'mailing_address': manager_request_response['mailing_address'],
                'contacts': manager_request_response['contacts'],
                'bank_account_number': manager_request_response[
                    'bank_account_number'
                ],
                'bank_name': '',
                'bank_bic': manager_request_response['bank_bic'],
                'signer_name': manager_request_response['signer_name'],
                'signer_position': manager_request_response['signer_position'],
                'signer_duly_authorized': manager_request_response[
                    'signer_duly_authorized'
                ],
                'attachments': manager_request_response['attachments'],
                'crm_link': manager_request_response.get('crm_link', ''),
                'st_link': manager_request_response['st_link'],
                'client_login': manager_request_response['client_login'],
                'billing_external_id': manager_request_response[
                    'billing_external_id'
                ],
                'billing_client_id': manager_request_response[
                    'billing_client_id'
                ],
                'billing_person_id': manager_request_response[
                    'billing_person_id'
                ],
                'billing_contract_id': manager_request_response[
                    'billing_contract_id'
                ],
            },
        ),
    ]

    await broker.process()


@pytest.mark.parametrize(
    ('service_name', 'expected_notice_name'),
    [
        pytest.param('cargo', 'CargoManagerRequestRejectedNotice', id='cargo'),
        pytest.param('taxi', 'TaxiManagerRequestRejectedNotice', id='taxi'),
    ],
)
async def test_manager_request_already_accepted(
        stq3_context,
        mock_corp_requests,
        mock_staff,
        accepted_event_data,
        load_json,
        service_name,
        expected_notice_name,
):
    manager_request_response = load_json('manager_request_response.json')
    manager_request_response['service'] = service_name
    manager_request_response['activation_email_sent'] = True

    mock_corp_requests.data.get_manager_request_response = (
        manager_request_response
    )
    mock_staff.data.get_persons_response = MOCK_STAFF_RESPONSE

    broker = manager_broker.ManagerRequestStatusChangedEventBroker.make(
        stq3_context, event_data=accepted_event_data,
    )

    await broker.process()

    events = await events_db.fetch_named_events(
        stq3_context, name='ManagerRequestStatusChanged',
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=None,
            event_name='ManagerRequestStatusChanged',
            event_data=accepted_event_data,
        ),
    ]

    notices = await notices_db.fetch_named_notices(
        stq3_context, name=expected_notice_name,
    )

    assert notices == []

    await broker.process()
