# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access

import datetime
from unittest import mock

import pytest

from corp_notices.events import db as events_db
from corp_notices.events import models as events_models
from corp_notices.events.events import new_trial_client
from corp_notices.notices import db as notices_db
from corp_notices.notices import models as notices_models

NOW = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

pytestmark = [
    pytest.mark.now(NOW.isoformat()),
    pytest.mark.config(
        CORP_NOTICES_SETTINGS={
            'TrialFollowUpNotice': {
                'enabled': True,
                'minutes_offset': 30,
                'slugs': {'rus': 'AAAAAA'},
            },
        },
    ),
]


MOCK_CLIENT_REQUEST_DRAFT_RESPONSE = {
    'client_id': 'rus_client_id',
    'autofilled_fields': [],
    'references': {'gclid': '123456', 'yakassa': '1'},
    'legal_form': 'ОАО',
    'city': 'Москва',
    'company_name': '123',
    'contract_type': 'taxi',
    'contact_emails': ['osiei@yandex-team.ru'],
    'contact_name': 'тест235',
    'contact_phone': '+79263301676',
    'country': 'rus',
    'enterprise_name_short': 'ОАО "ВСПМК-3"',
    'enterprise_name_full': 'example',
    'legal_address_info': {
        'city': 'Владикавказ',
        'post_index': '362013',
        'street': 'ул П 6-я',
        'house': '5Б',
    },
    'mailing_address_info': {
        'city': 'Владикавказ',
        'post_index': '362013',
        'street': 'ул П 6-я',
        'house': '5Б',
    },
    'registration_number': '502901001',
    'offer_agreement': True,
    'processing_agreement': True,
    'company_tin': '1503009019',
    'yandex_login': 'osiei13',
    'signer_name': 'example',
    'signer_position': 'Генеральный директор',
    'signer_gender': 'male',
    'created': '2018-04-19T15:20:09.160000+03:00',
    'updated': '2018-04-20T15:20:09.160000+03:00',
}


@pytest.fixture
def lf_event_data():
    return {
        'client_id': 'rus_id',
        'yandex_login': 'osiei13',
        'contract_type': 'taxi',
        'encrypted_password': 'some_aes_string',
        'flow': 'client_trial',
    }


@pytest.fixture
def not_lf_event_data():
    return {
        'client_id': 'rus_id',
        'yandex_login': 'osiei13',
        'contract_type': 'taxi',
        'encrypted_password': 'another_aes_string',
        'flow': 'register_trial',
    }


async def test_registry(stq3_context):
    from corp_notices.events import registry
    assert registry.get('NewTrialClient')


async def test_trial_client_lf_notice_enqueue(
        stq3_context, mock_corp_requests, lf_event_data,
):
    mock_corp_requests.data.get_request_draft_response = (
        MOCK_CLIENT_REQUEST_DRAFT_RESPONSE
    )

    client_id = lf_event_data['client_id']

    with mock.patch.object(
            new_trial_client.NewTrialClientEventBroker,
            '_create_letter_id',
            return_value='1111',
    ) as _:
        broker = new_trial_client.NewTrialClientEventBroker.make(
            stq3_context, event_data=lf_event_data, client_id=client_id,
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
            event_data=lf_event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='NewTrialClientNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs={'yandex_login': 'osiei13', 'contract_type': 'taxi'},
        ),
        notices_models.Notice(
            id=2,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='TrialFollowUpNotice',
            client_id=client_id,
            send_at=NOW + datetime.timedelta(minutes=30),
            notice_kwargs={
                'letter_id': '1111',
                'client_id': 'rus_id',
                'locale': 'rus',
                'company_name': '123',
                'city': 'Москва',
                'yandex_login': 'osiei13',
                'contact_name': 'тест235',
                'contact_email': 'osiei@yandex-team.ru',
                'contact_phone': '+79263301676',
                'references': '<li>gclid – 123456</li><li>yakassa – 1</li>',
            },
        ),
    ]


async def test_trial_client_not_lf_notice_enqueue(
        stq3_context, mock_corp_requests, not_lf_event_data,
):
    mock_corp_requests.data.get_request_draft_response = (
        MOCK_CLIENT_REQUEST_DRAFT_RESPONSE
    )

    client_id = not_lf_event_data['client_id']

    with mock.patch.object(
            new_trial_client.NewTrialClientEventBroker,
            '_create_letter_id',
            return_value='1111',
    ) as _:
        broker = new_trial_client.NewTrialClientEventBroker.make(
            stq3_context, event_data=not_lf_event_data, client_id=client_id,
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
            event_data=not_lf_event_data,
        ),
    ]

    notices = await notices_db.fetch_client_notices(stq3_context, client_id)

    assert notices == [
        notices_models.Notice(
            id=1,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='NewTrialAutoRegisteredClientNotice',
            client_id=client_id,
            send_at=NOW,
            notice_kwargs={
                'yandex_login': 'osiei13',
                'encrypted_password': 'another_aes_string',
                'contract_type': 'taxi',
            },
        ),
        notices_models.Notice(
            id=2,
            event_id=events[0].id,
            status=notices_models.Status.pending,
            notice_name='TrialFollowUpNotice',
            client_id=client_id,
            send_at=NOW + datetime.timedelta(minutes=30),
            notice_kwargs={
                'letter_id': '1111',
                'client_id': 'rus_id',
                'locale': 'rus',
                'company_name': '123',
                'city': 'Москва',
                'yandex_login': 'osiei13',
                'contact_name': 'тест235',
                'contact_email': 'osiei@yandex-team.ru',
                'contact_phone': '+79263301676',
                'references': '<li>gclid – 123456</li><li>yakassa – 1</li>',
            },
        ),
    ]
