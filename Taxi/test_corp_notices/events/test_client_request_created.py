# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import datetime

import pytest

from corp_notices.events import db as events_db
from corp_notices.events import models as events_models
from corp_notices.events.events import client_request_created
from corp_notices.notices import db as notices_db
from corp_notices.notices import models as notices_models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = pytest.mark.now(NOW.isoformat())


MOCK_ISR_CLIENTREQUEST_RESPONSE = {
    'id': 'isr_id',
    'client_id': 'isr_client_id',
    'autofilled_fields': [],
    'references': {},
    'readonly_fields': [
        'company_tin',
        'country',
        'offer_agreement',
        'processing_agreement',
    ],
    'city': 'Тель Авив',
    'legal_form': 'isr-legal-form',
    'company_name': 'Isr company_name',
    'contract_type': 'taxi',
    'contact_emails': ['engineer@yandex-team.ru'],
    'contact_name': 'Василий',
    'contact_phone': '+79263452242',
    'country': 'isr',
    'enterprise_name_short': 'example_short',
    'enterprise_name_full': 'example',
    'legal_address_info': {
        'city': 'Tel Aviv',
        'house': '1',
        'post_index': '12345',
        'street': 'street1',
    },
    'mailing_address_info': {
        'city': 'Tel Aviv',
        'house': '1',
        'post_index': '12345',
        'street': 'street2',
    },
    'offer_agreement': True,
    'processing_agreement': True,
    'status': 'pending',
    'company_tin': '1503009017',
    'yandex_login': 'semeynik',
    'signer_name': 'signer_name_isr',
    'signer_position': 'signer_position_isr',
    'signer_gender': 'male',
    'created': '2019-11-12T11:49:33.368000+03:00',
    'updated': '2019-11-12T11:49:33.368000+03:00',
    'is_active': True,
    'last_error': None,
    'registration_number': '1234',
}


@pytest.fixture
def rus_event_data():
    return {'request_id': 'rus_id', 'client_id': 'rus_client_id'}


@pytest.fixture
def isr_event_data():
    return {'request_id': 'isr_id', 'client_id': 'isr_client_id'}


async def test_registry(stq3_context):
    from corp_notices.events import registry
    assert registry.get('ClientRequestCreated')


async def test_rus_client_request_created_notice_enqueue(
        stq3_context, mock_corp_requests, rus_event_data, load_json,
):
    client_request_response = load_json('client_request_response.json')

    mock_corp_requests.data.get_client_request_response = (
        client_request_response
    )
    client_id = client_request_response['client_id']

    broker = client_request_created.ClientRequestCreatedBroker.make(
        stq3_context, event_data=rus_event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='ClientRequestCreated',
            event_data=rus_event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='ClientRequestCreatedNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs={
                'letter_id': 'rus_id',
                'request_id': 'rus_id',
                'client_id': 'rus_client_id',
                'company_name': '123',
                'contact_name': 'тест235',
                'contact_phone': '+79263301676',
                'contact_email': 'osiei@yandex-team.ru',
                'city': 'Москва',
                'yandex_login': 'osiei13',
                'locale': 'rus',
                'full_corp_name': 'example',
                'short_corp_name': 'ОАО "ВСПМК-3"',
                'corp_form': 'ОАО',
                'registration_date': '2017-12-30, 03:00',
                'inn': '1503009019',
                'signer_name': 'example',
                'signer_position': 'Генеральный директор',
                'signer_sex': 'male',
                'offer': True,
                'references': '<li>gclid – 123456</li><li>yakassa – 1</li>',
                'contract_type': 'taxi',
                'ogrn': '1021500673050',
                'kpp': '151601001',
                'bik': '044525256',
                'account': '40802810087340000053',
            },
        ),
    ]


async def test_isr_client_request_created_notice_enqueue(
        stq3_context, mock_corp_requests, isr_event_data,
):

    mock_corp_requests.data.get_client_request_response = (
        MOCK_ISR_CLIENTREQUEST_RESPONSE
    )

    client_id = isr_event_data['client_id']

    broker = client_request_created.ClientRequestCreatedBroker.make(
        stq3_context, event_data=isr_event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='ClientRequestCreated',
            event_data=isr_event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='ClientRequestCreatedNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs={
                'letter_id': 'isr_id',
                'request_id': 'isr_id',
                'client_id': 'isr_client_id',
                'company_name': 'Isr company_name',
                'contact_name': 'Василий',
                'contact_phone': '+79263452242',
                'contact_email': 'engineer@yandex-team.ru',
                'city': 'Тель Авив',
                'yandex_login': 'semeynik',
                'locale': 'isr',
                'full_corp_name': 'example',
                'short_corp_name': 'example_short',
                'corp_form': 'isr-legal-form',
                'inn': '1503009017',
                'signer_name': 'signer_name_isr',
                'signer_position': 'signer_position_isr',
                'signer_sex': 'male',
                'offer': True,
                'references': '',
                'contract_type': 'taxi',
                'business_entity_number': '1234',
            },
        ),
    ]


async def test_dequeue_follow_up_notice_enqueue(
        stq3_context, mock_corp_requests, rus_event_data, load_json,
):
    client_request_response = load_json('client_request_response.json')

    mock_corp_requests.data.get_client_request_response = (
        client_request_response
    )
    client_id = client_request_response['client_id']

    await events_db.insert(
        stq3_context,
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='NewTrialClient',
            event_data={},
        ),
    )

    await notices_db.insert(
        stq3_context,
        notices_models.Notice(
            id=1,
            event_id=1,
            status=notices_models.Status.pending,
            notice_name='TrialFollowUpNotice',
            client_id=client_id,
            send_at=NOW + datetime.timedelta(minutes=30),
            notice_kwargs={},
        ),
    )

    broker = client_request_created.ClientRequestCreatedBroker.make(
        stq3_context, event_data=rus_event_data, client_id=client_id,
    )

    await broker.process()

    events = await events_db.fetch_client_events(
        stq3_context, client_id=client_id,
    )
    assert events == [
        events_models.Event(
            id=1,
            client_id=client_id,
            event_name='NewTrialClient',
            event_data={},
        ),
        events_models.Event(
            id=2,
            client_id=client_id,
            event_name='ClientRequestCreated',
            event_data=rus_event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.dequeued,
            notice_name='TrialFollowUpNotice',
            client_id=client_id,
            send_at=NOW + datetime.timedelta(minutes=30),
            notice_kwargs={},
        ),
        notices_models.Notice(
            id=2,
            event_id=events[1].id,
            status=notices_models.Status.pending,
            notice_name='ClientRequestCreatedNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs={
                'letter_id': 'rus_id',
                'request_id': 'rus_id',
                'client_id': 'rus_client_id',
                'company_name': '123',
                'contact_name': 'тест235',
                'contact_phone': '+79263301676',
                'contact_email': 'osiei@yandex-team.ru',
                'city': 'Москва',
                'yandex_login': 'osiei13',
                'locale': 'rus',
                'full_corp_name': 'example',
                'short_corp_name': 'ОАО "ВСПМК-3"',
                'corp_form': 'ОАО',
                'registration_date': '2017-12-30, 03:00',
                'inn': '1503009019',
                'signer_name': 'example',
                'signer_position': 'Генеральный директор',
                'signer_sex': 'male',
                'offer': True,
                'references': '<li>gclid – 123456</li><li>yakassa – 1</li>',
                'contract_type': 'taxi',
                'ogrn': '1021500673050',
                'kpp': '151601001',
                'bik': '044525256',
                'account': '40802810087340000053',
            },
        ),
    ]


async def test_request_not_found(
        stq3_context, mock_corp_requests, rus_event_data, load_json,
):
    client_id = rus_event_data['client_id']

    broker = client_request_created.ClientRequestCreatedBroker.make(
        stq3_context, event_data=rus_event_data, client_id=client_id,
    )

    await broker.process()

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)
    assert notices == []
