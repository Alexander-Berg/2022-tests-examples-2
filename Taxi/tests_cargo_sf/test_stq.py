import uuid

import pytest

STQ_KWARGS = {
    'external_event_id': 'external_event_id',
    'details': {
        'company_name': 'company_name',
        'contact_last_name': 'contact_last_name',
        'contact_phone': 'contact_phone',
        'contact_mail': 'contact_mail',
        'contact_first_name': 'contact_first_name',
        'company_utm_source': 'smbr',
        'lead_potential': 9001,
        'company_tin': '123456789',
        'company_city': 'br_omsk',
        'company_country': 'rf',
        'company_industry': 'avtotovary',
        'lead_corp_client_id': 'lead_corp_client_id',
        'ticket_state': 'card_bound',
    },
}

LEAD_JSON = [
    {
        'id': 1686611,
        'name': 'company_name',
        'price': 9001,
        'status_id': 46580455,
        'pipeline_id': 18,
        'responsible_user_id': 8043349,
        'custom_fields_values': [
            {'field_id': 349763, 'values': [{'value': 'external_event_id'}]},
            {'field_id': 129711, 'values': [{'enum_id': 72443}]},
            {'field_id': 132297, 'values': [{'value': 'lead_corp_client_id'}]},
        ],
    },
]
COMPANY_JSON = [
    {
        'id': 2932069,
        'name': 'company_name',
        'responsible_user_id': 8043349,
        'custom_fields_values': [
            {'field_id': 134455, 'values': [{'value': '123456789'}]},
            {'field_id': 678915, 'values': [{'value': 'Омск'}]},
            {'field_id': 129393, 'values': [{'enum_id': 70669}]},
            {'field_id': 135005, 'values': [{'enum_id': 81379}]},
        ],
    },
]
CONTACT_JSON = [
    {
        'id': 2932071,
        'first_name': 'contact_first_name',
        'last_name': 'contact_last_name',
        'responsible_user_id': 8043349,
        'custom_fields_values': [
            {
                'field_id': 126277,
                'values': [{'enum_id': 68817, 'value': 'contact_phone'}],
            },
            {
                'field_id': 126279,
                'values': [{'enum_id': 68829, 'value': 'contact_mail'}],
            },
        ],
    },
]


@pytest.mark.parametrize(
    'amo_response_code,expected_method,company_contact_names_missing',
    ((200, 'PATCH', False), (204, 'POST', False), (204, 'POST', True)),
)
async def test_stq_cargo_sf(
        stq_runner,
        taxi_cargo_sf,
        mock_amo_leads,
        mock_amo_companies,
        mock_amo_contacts,
        mock_amo_lead_link,
        amo_response_code,
        expected_method,
        company_contact_names_missing,
):
    external_event_id = 'external_event_id'
    if amo_response_code == 204:
        external_event_id = f'external_event_id204'
    STQ_KWARGS['external_event_id'] = external_event_id
    if company_contact_names_missing:
        STQ_KWARGS['details']['company_name'] = None
        STQ_KWARGS['details']['contact_last_name'] = None
        LEAD_JSON[0]['name'] = 'Новая регистрация (Феникс)'
        COMPANY_JSON[0]['name'] = 'Новая регистрация (Феникс)'
        CONTACT_JSON[0]['last_name'] = 'Новый контакт (Феникс)'
    await stq_runner.cargo_sf_amo_lead_event.call(
        task_id=uuid.uuid4().hex, kwargs=STQ_KWARGS, expect_fail=False,
    )
    assert mock_amo_leads.times_called == 2
    assert mock_amo_companies.times_called == 1
    assert mock_amo_contacts.times_called == 1
    assert mock_amo_lead_link.times_called == 1

    # search call
    search_call = mock_amo_leads.next_call()
    assert search_call['request'].method == 'GET'

    # update calls
    for handle, expected_json in {
            mock_amo_leads: LEAD_JSON,
            mock_amo_companies: COMPANY_JSON,
            mock_amo_contacts: CONTACT_JSON,
    }.items():
        call = handle.next_call()
        assert call['request'].method == expected_method
        if amo_response_code == 204 and 'id' in expected_json[0]:
            expected_json[0].pop('id')
        for custom_value in expected_json[0]['custom_fields_values']:
            if custom_value['field_id'] == 349763:
                custom_value['values'][0]['value'] = external_event_id
                break
        assert call['request'].json == expected_json

    if amo_response_code == 204:
        assert mock_amo_lead_link.next_call()['request'].json == [
            {
                'entity_id': 1686611,
                'to_entity_id': 2857727,
                'to_entity_type': 'companies',
            },
            {
                'entity_id': 1686611,
                'to_entity_id': 2688359,
                'to_entity_type': 'contacts',
            },
        ]
    elif amo_response_code == 200:
        assert mock_amo_lead_link.next_call()['request'].json == [
            {
                'entity_id': 1686611,
                'to_entity_id': 2932069,
                'to_entity_type': 'companies',
            },
            {
                'entity_id': 1686611,
                'to_entity_id': 2932071,
                'to_entity_type': 'contacts',
            },
        ]
