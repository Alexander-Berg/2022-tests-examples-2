# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

import pytest

from corp_notices.notices.notices import client_request_created_notice

pytestmark = [
    pytest.mark.config(
        CORP_NOTICES_SETTINGS={
            'ClientRequestCreatedNotice': {
                'enabled': True,
                'moderator_emails': {
                    'isr': ['isrmanager@yandex-team.ru', 'someman@yandex.ru'],
                },
                'slugs': {'isr': 'AAAAAA'},
            },
        },
    ),
]

MOCK_CLIENT_RESPONSE = {
    'id': 'client_id_1',
    'name': 'Test client',
    'billing_name': 'None',
    'country': 'isr',
    'yandex_login': 'test-client',
    'description': 'Test',
    'is_trial': False,
    'email': 'test@email.com',
    'features': [],
    'billing_id': '101',
    'created': '2020-01-01T03:00:00+03:00',
}


@pytest.fixture
def broker(cron_context, mock_corp_clients):
    mock_corp_clients.data.get_client_response = MOCK_CLIENT_RESPONSE
    return client_request_created_notice.ClientRequestCreatedNoticeBroker.make(
        cron_context,
        client_id='client_id_1',
        notice_kwargs={
            'letter_id': 'isr_id',
            'request_id': 'isr_id',
            'client_id': 'isr_client_id',
            'company_name': 'Isr company_name',
            'contact_name': 'Василий',
            'contact_phone': '+79263452242',
            'contact_email': 'engineer@yandex-team.ru',
            'city': 'Тель Авив',
            'passport_login': 'semeynik',
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
    )


async def test_template_kwargs(broker):
    assert await broker.get_emails() == [
        'isrmanager@yandex-team.ru',
        'someman@yandex.ru',
    ]


async def test_registry(stq3_context):
    from corp_notices.notices import registry
    assert registry.get('ClientRequestCreatedNotice')
