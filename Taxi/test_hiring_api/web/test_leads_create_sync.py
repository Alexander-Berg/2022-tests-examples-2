import pytest

EXTERNAL_ID = '4552995ef815c9bba2dae61d5e0f643a'
FIELD_DATA = 'data'
FIELD_ENDPOINT = 'endpoint'
FIELD_STATUS_CODE = 'status_code'
REQUESTS_FILE = 'requests.json'
X_DELIVERY_ID = 'das3tji43tjgj3j9u484tj3fiewo'


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'salesforce',
    'stq_mock',
)
@pytest.mark.parametrize(
    'request_type, request_name, stq_calls',
    [
        ('valid', 'send_to_salesforce_only', 1),
        ('valid', 'send_to_either', 1),
        ('valid', 'phone_without_plus', 1),
        ('valid', 'trash_phone', 1),
        ('invalid', 'send_to_zendesk_only', 0),
        ('invalid', 'short_phone', 0),
        ('invalid', 'without_phone_code', 0),
        ('invalid', 'unknown_country_code', 0),
    ],
)
async def test_leads_create_send_to(
        request_leads_create_sync,
        load_json,
        hiring_rate_accounting_calculate_mockserver,
        hiring_rate_accounting_update_mockserver,
        request_type,
        request_name,
        stq_mock,
        stq_calls,
):
    response_calculate = load_json('response_calculate.json')[request_type]
    response_update = load_json('response_update.json')[request_type]
    hiring_rate_accounting_update_mockserver(response_update)
    hiring_rate_accounting_calculate_mockserver(response_calculate)

    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    response_body = await request_leads_create_sync(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )
    assert response_body
    assert stq_mock.times_called == stq_calls
    if request_type == 'valid':
        assert response_body['details']['external_ids']

    if request_type == 'valid':
        assert response_body['details']['lead_id']


@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'salesforce',
    'stq_mock',
)
@pytest.mark.parametrize('use_external_id', [True, False])
async def test_leads_create_check_id(
        request_leads_create_sync,
        hiring_rate_accounting_calculate_mockserver,
        hiring_rate_accounting_update_mockserver,
        load_json,
        use_external_id,
        taxi_config,
):
    taxi_config.set_values(
        {
            'HIRING_API_USE_EXTERNAL_ID_BY_ENDPOINTS': {
                '__default__': {'enabled': use_external_id},
                'endpoints': [],
            },
        },
    )
    response_calculate = load_json('response_calculate.json')['valid']
    response_update = load_json('response_update.json')['valid']
    hiring_rate_accounting_update_mockserver(response_update)
    hiring_rate_accounting_calculate_mockserver(response_calculate)

    request_data = load_json(REQUESTS_FILE)['valid']['send_to_either']
    response_body = await request_leads_create_sync(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )
    assert response_body
    external_id = response_body['details']['external_ids']
    assert external_id == [EXTERNAL_ID] if use_external_id else [X_DELIVERY_ID]
