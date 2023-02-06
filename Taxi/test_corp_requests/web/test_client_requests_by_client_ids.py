# pylint: disable=redefined-outer-name

import pytest


@pytest.mark.parametrize(
    ['client_ids', 'expected_result', 'status_code'],
    [
        pytest.param(
            ['isr_client_id', 'non_existing_client_id'],
            [
                {
                    'id': '95b3c932435f4f008a635faccb6454f6',
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
                    'signer_gender': 'female',
                    'created': '2019-11-12T11:49:33.368000+03:00',
                    'updated': '2019-11-12T11:49:33.368000+03:00',
                    'is_active': True,
                    'last_error': None,
                },
            ],
            200,
            id='One existing, one non-existing',
        ),
    ],
)
@pytest.mark.config(TVM_RULES=[{'dst': 'personal', 'src': 'corp-requests'}])
async def test_client_requests_bulk_retrieve(
        mock_personal,
        mock_mds,
        taxi_corp_requests_web,
        client_ids,
        expected_result,
        status_code,
):
    json = {'client_ids': client_ids}
    response = await taxi_corp_requests_web.post(
        '/v1/client-requests/by-client-ids', json=json,
    )
    response_json = await response.json()

    assert response.status == status_code
    assert response_json['client_requests'] == expected_result
