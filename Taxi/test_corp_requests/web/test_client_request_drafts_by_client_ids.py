# pylint: disable=redefined-outer-name
import pytest

EXPECTED_DRAFTS = [
    {
        'client_id': 'bzdrial',
        'contract_type': 'taxi',
        'created': '2018-04-19T15:20:09.160000+03:00',
        'updated': '2018-04-20T15:20:09.160000+03:00',
        'yandex_login': 'trial_login',
        'country': 'rus',
        'company_name': 'trial_company',
        'contact_name': 'trial_name',
        'contact_phone': '+79011111111',
        'contact_emails': ['lol@yandex.ru'],
        'references': {},
        'autofilled_fields': [],
        'bank_account_number': '',
        'bank_bic': '',
        'bank_name': '',
        'city': '',
        'company_cio': '',
        'company_tin': '',
        'enterprise_name': '',
        'enterprise_name_full': '',
        'enterprise_name_short': '',
        'legal_address': '',
        'legal_form': '',
        'mailing_address': '',
        'promo_id': '',
        'proxy_scan': '',
        'services_to_show': ['taxi'],
        'signer_position': '',
        'signer_name': '',
        'without_vat_contract': False,
    },
    {
        'client_id': 'full_isr_draft',
        'contract_type': 'taxi',
        'created': '2019-11-12T11:49:33.368000+03:00',
        'updated': '2019-11-12T11:49:33.368000+03:00',
        'yandex_login': 'full_isr_draft',
        'country': 'isr',
        'company_name': 'Isr company_name',
        'contact_name': 'Василий',
        'contact_phone': '+79263452242',
        'contact_emails': ['engineer@yandex-team.ru'],
        'references': {},
        'city': 'Тель Авив',
        'legal_form': 'isr-legal-form',
        'enterprise_name_full': 'example',
        'enterprise_name_short': 'example_short',
        'company_tin': '559017555',
        'registration_number': '502901001',
        'legal_address_info': {
            'city': 'Tel Aviv',
            'street': 'street1',
            'house': '1',
            'post_index': '12345',
        },
        'mailing_address_info': {
            'city': 'Tel Aviv',
            'street': 'street2',
            'house': '1',
            'post_index': '12345',
        },
        'services_to_show': ['taxi'],
        'signer_position': 'signer_position_isr',
        'signer_name': 'signer_name_isr',
        'signer_gender': 'female',
        'offer_agreement': True,
        'processing_agreement': True,
        'autofilled_fields': [],
        'draft_status': 'filled',
        'services': ['taxi'],
    },
]


@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_client_requests_bulk_retrieve(
        taxi_corp_requests_web, mock_personal,
):
    json = {'client_ids': ['bzdrial', 'full_isr_draft']}
    response = await taxi_corp_requests_web.post(
        '/v1/client-request-drafts/by-client-ids', json=json,
    )

    assert response.status == 200
    response_json = await response.json()

    assert EXPECTED_DRAFTS == response_json['client_request_drafts']
