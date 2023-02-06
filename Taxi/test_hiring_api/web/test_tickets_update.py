import uuid

import pytest

FIELD_DATA = 'data'
FIELD_ENDPOINT = 'endpoint'
FIELD_STATUS_CODE = 'status_code'
REQUESTS_FILE = 'requests.json'
SOLOMON_SENSOR_STATUS_CHANGE = 'salesforce.lead.status_change'
SALESFORCE_UPDATE_QUEUE_NAME = 'hiring_send_update_to_salesforce'


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.parametrize('use_external_id', [True, False])
@pytest.mark.parametrize(
    'request_name', ['no_markup', 'do_not_send_to_infranaim'],
)
async def test_tickets_update_simple_requests(
        request_tickets_update,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        stq_mock,
        load_json,
        taxi_config,
        use_external_id,
        request_name,
):
    # arrange
    taxi_config.set_values(
        {
            'HIRING_API_USE_EXTERNAL_ID_BY_ENDPOINTS': {
                '__default__': {'enabled': use_external_id},
                'endpoints': [],
            },
        },
    )
    request_data = load_json(REQUESTS_FILE)['valid'][request_name]

    # act
    response_body = await request_tickets_update(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    response_body['details']['accepted_fields'].sort()
    assert response_body == load_json(f'responses/{request_name}.json')

    assert stq_mock.times_called == 1
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == SALESFORCE_UPDATE_QUEUE_NAME
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json(
        'stq_requests/salesforce_with_external_id.json',
    )


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.now('2022-04-29T16:00:00.0')
@pytest.mark.parametrize('use_external_id', [True, False])
async def test_tickets_update_simple_invalid_requests(
        request_tickets_update,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        stq_mock,
        load_json,
        use_external_id,
        taxi_config,
):
    # arrange
    taxi_config.set_values(
        {
            'HIRING_API_USE_EXTERNAL_ID_BY_ENDPOINTS': {
                '__default__': {'enabled': use_external_id},
                'endpoints': [],
            },
        },
    )
    request_data = load_json(REQUESTS_FILE)['invalid']['no_lead_id']

    # act
    response_body = await request_tickets_update(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )

    # assert
    assert response_body == load_json('responses/missing_id.json')
    assert stq_mock.times_called == 0


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'stq_mock',
)
@pytest.mark.parametrize(
    'request_type, request_name',
    [
        ('valid', 'send_to_salesforce_only'),
        ('valid', 'send_to_zendesk_only'),
        ('valid', 'send_to_either'),
        ('invalid', 'send_to_neither'),
    ],
)
async def test_tickets_update_send_to(
        request_tickets_update,
        load_json,
        hiring_rate_accounting_calculate_mockserver,
        hiring_rate_accounting_update_mockserver,
        request_type,
        request_name,
        stq_mock,
):
    response_calculate = load_json('response_calculate.json')[request_type]
    response_update = load_json('response_update.json')[request_type]
    hiring_rate_accounting_update_mockserver(response_update)
    hiring_rate_accounting_calculate_mockserver(response_calculate)

    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    response_body = await request_tickets_update(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )
    assert response_body

    if request_name == 'send_to_either':
        assert stq_mock.times_called == 2
    elif request_name == 'send_to_neither':
        assert stq_mock.times_called == 0
    else:
        assert stq_mock.times_called == 1


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'stq_mock',
    'timeout_hiring_rate_calculate',
    'timeout_hiring_rate_update',
)
@pytest.mark.parametrize(
    'request_type, request_name', [('valid', 'service_unreachable')],
)
async def test_tickets_rate_limits_unreachable(
        request_tickets_update, load_json, request_type, request_name,
):
    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    response_body = await request_tickets_update(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )
    assert response_body


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'stq_mock',
)
@pytest.mark.parametrize(
    'request_type, request_name',
    [
        ('invalid', 'limit_exceed'),
        ('invalid', 'default_limit_exceed'),
        ('invalid', 'limit_exceed_during_update'),
        ('invalid', 'no_endpoint_in_ratelimit'),
        ('invalid', 'disabled'),
        ('valid', 'inside_limits'),
        ('valid', 'unlimited'),
    ],
)
async def test_tickets_rate_limits(
        request_tickets_update,
        load_json,
        hiring_rate_accounting_calculate_mockserver,
        hiring_rate_accounting_update_mockserver,
        request_type,
        request_name,
):
    response_calculate = load_json('response_calculate.json')[request_type]
    response_update = load_json('response_update.json')[request_type]
    hiring_rate_accounting_update_mockserver(response_update)
    hiring_rate_accounting_calculate_mockserver(response_calculate)

    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    response_body = await request_tickets_update(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )
    assert response_body


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
@pytest.mark.parametrize(
    'request_type, request_name, save_metrics',
    [
        ('valid', 'send_to_salesforce_only', True),
        ('valid', 'send_to_salesforce_only_no_status_field', True),
        ('valid', 'send_to_zendesk_only', False),
        ('valid', 'send_to_either', True),
        ('invalid', 'send_to_neither', True),
    ],
)
async def test_tickets_update_should_save_metrics(
        request_type,
        request_name,
        save_metrics,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        load_json,
        get_single_stat_by_label_values,
        web_app,
        web_app_client,
):
    request_data = load_json(REQUESTS_FILE)[request_type][request_name]

    response = await web_app_client.post(
        '/v1/tickets/update',
        json=request_data[FIELD_DATA],
        params={'endpoint': request_data[FIELD_ENDPOINT]},
        headers={'X-Delivery-Id': uuid.uuid4().hex},
    )
    assert response.status == request_data[FIELD_STATUS_CODE]
    assert await response.json()

    actual_stats = get_single_stat_by_label_values(
        web_app['context'], {'sensor': SOLOMON_SENSOR_STATUS_CHANGE},
    )
    if not save_metrics:
        assert actual_stats is None
        return

    status = ''
    for field in request_data[FIELD_DATA]['fields']:
        if field['name'] == 'Status':
            status = field['value']
    expected_stats = {
        'kind': 'IGAUGE',
        'labels': {
            'code': str(request_data[FIELD_STATUS_CODE]),
            'endpoint': request_data[FIELD_ENDPOINT],
            'sensor': SOLOMON_SENSOR_STATUS_CHANGE,
            'status': status,
            'source': 'hiring-api',
        },
        'timestamp': None,
        'value': 1,
    }
    assert actual_stats == expected_stats
