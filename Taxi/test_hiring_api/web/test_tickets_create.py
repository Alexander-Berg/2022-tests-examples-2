import pytest

EXPECTED_STATS_FILE = 'expected_stats.json'
EXTERNAL_ID = '4552995ef815c9bba2dae61d5e0f643a'
FIELD_DATA = 'data'
FIELD_ENDPOINT = 'endpoint'
FIELD_STATUS_CODE = 'status_code'
REQUESTS_FILE = 'requests.json'
ROUTE = '/v1/tickets/create'
X_DELIVERY_ID = 'das3tji43tjgj3j9u484tj3fiewo'


@pytest.mark.parametrize(
    'request_type, request_name',
    [
        ('valid', 'send_to_infranaim_success'),
        ('valid', 'send_to_infranaim_error'),
        ('valid', 'do_not_send_to_infranaim'),
        ('valid', 'phone_without_plus'),
        ('valid', 'trash_phone'),
        ('invalid', 'phone_empty'),
        ('invalid', 'phone_invalid'),
        ('invalid', 'short_phone'),
        ('invalid', 'without_phone_code'),
        ('invalid', 'unknown_country_code'),
    ],
)
async def test_tickets_create_simple_requests(
        request_tickets_create,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        stq_mock,
        load_json,
        request_type,
        request_name,
):
    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    response_body = await request_tickets_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )
    assert response_body
    if request_type == 'valid':
        if request_name != 'do_not_send_to_infranaim':
            assert stq_mock.times_called == 3
        else:
            assert stq_mock.times_called == 2


@pytest.mark.parametrize('use_external_id', [True, False])
async def test_tickets_create_check_id(
        request_tickets_create,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
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
    request_data = load_json(REQUESTS_FILE)['valid']['send_to_either']
    response_body = await request_tickets_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )
    assert response_body
    external_id = response_body['details']['external_ids']
    assert external_id == [EXTERNAL_ID] if use_external_id else [X_DELIVERY_ID]


@pytest.mark.parametrize(
    'request_type, request_name', [('invalid', 'no_markup')],
)
async def test_tickets_create_no_markup(
        request_tickets_create,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        load_json,
        request_type,
        request_name,
):
    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    response_body = await request_tickets_create(
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
        request_tickets_create,
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
    response_body = await request_tickets_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )
    assert response_body
    if request_type == 'valid':
        assert response_body['details']['external_ids']


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
        request_tickets_create, load_json, request_type, request_name,
):
    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    response_body = await request_tickets_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )
    assert response_body
    if request_type == 'valid':
        assert response_body['details']['external_ids']


@pytest.mark.config(HIRING_API_ENABLE_REQUEST_LIMIT=True)
@pytest.mark.usefixtures(
    'mock_personal_api',
    'mock_territories_api',
    'mock_hiring_data_markup',
    'stq_mock',
)
@pytest.mark.parametrize(
    'request_type, request_name', [('invalid', 'update_id_unique_violation')],
)
async def test_tickets_rate_limits_update_id_unique_violation(
        request_tickets_create,
        load_json,
        request_type,
        request_name,
        hiring_rate_accounting_calculate_mockserver,
        hiring_rate_accounting_update_mockserver,
):
    response_calculate = load_json('response_calculate.json')[request_type]
    response_update = load_json('response_update.json')['update_id_violation']
    hiring_rate_accounting_update_mockserver(response_update)
    hiring_rate_accounting_calculate_mockserver(response_calculate)
    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    response_body = await request_tickets_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )

    expected_error = {
        'code': 'UpdateIdUniqueViolation',
        'message': 'Update ID is not unique',
    }

    assert response_body
    assert expected_error in response_body['details']['errors']


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
    ],
)
async def test_tickets_create_send_to(
        request_tickets_create,
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
    response_body = await request_tickets_create(
        request_data[FIELD_DATA],
        request_data[FIELD_ENDPOINT],
        request_data[FIELD_STATUS_CODE],
    )
    assert response_body
    if request_type == 'valid':
        assert response_body['details']['external_ids']

    if request_name == 'send_to_either':
        assert stq_mock.times_called == 3
    elif request_name == 'send_to_salesforce_only':
        assert stq_mock.times_called == 2
    else:
        assert stq_mock.times_called == 1


@pytest.mark.parametrize(
    ('request_type', 'request_name'),
    [
        ('valid', 'send_to_infranaim_success'),
        ('valid', 'send_to_infranaim_error'),
    ],
)
@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.config(HIRING_API_PROCESSING_FLOW_MARKUP_ENABLED=True)
@pytest.mark.config(HIRING_API_DEFAULT_REGION_ID=100)
async def test_v1_tickets_create_with_send_to_both_stq(
        request_tickets_create,
        mock_hiring_candidates_region,
        mock_hiring_data_markup_by_flow,
        mock_personal_api,
        mock_territories_api,
        stq_mock,
        load_json,
        web_app_client,
        web_app,
        get_stats_by_label_values,
        request_type,
        request_name,
):
    # arrange
    hiring_data_markup_mock = mock_hiring_data_markup_by_flow(
        responses_by_flows={
            None: load_json('response_data_markup.json')['valid'],
            'hiring_data_markup_new_lead_check_processing_flow': (
                load_json('hiring_data_markup_responses/processing_flow.json')
            ),
        },
    )

    hiring_candidates_region_mock = mock_hiring_candidates_region(
        response=load_json('hiring_candidates_region_responses/normal.json'),
    )
    headers = {'X-Delivery-Id': 'x delivery id'}
    expected_stats = load_json(EXPECTED_STATS_FILE)

    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    data = request_data[FIELD_DATA]
    params = request_data[FIELD_ENDPOINT]

    # act
    await web_app_client.post(
        ROUTE, json=data, headers=headers, params={'endpoint': params},
    )

    # assert
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'salesforce.lead.creation'},
    )
    assert stats == [expected_stats[request_name]]

    assert hiring_data_markup_mock.times_called == 2

    # check that we sent all stq messages
    assert stq_mock.times_called == 3
    # compare what we send to salesforce
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_send_to_salesforce'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json(
        'stq_requests/to_salesforce_with_flow_markup.json',
    )

    # compare what we send to candidates
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_candidates_create_lead'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/to_candidates.json')

    # compare what we send to infranaim
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_send_to_infranaim_api'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json(
        'stq_requests/to_infranaim_with_flow_markup.json',
    )

    assert hiring_candidates_region_mock.times_called == 1
    hiring_candidates_call = hiring_candidates_region_mock.next_call()
    assert dict(hiring_candidates_call['request'].query) == {
        'phone': '+79998887766',
    }


@pytest.mark.parametrize(
    ('request_type', 'request_name'), [('valid', 'eats_channel')],
)
@pytest.mark.config(HIRING_API_PROCESSING_FLOW_MARKUP_ENABLED=True)
async def test_v1_tickets_create_eats_channel(
        request_tickets_create,
        mock_hiring_data_markup_by_flow,
        mock_hiring_candidates_eda_channel,
        mock_personal_api,
        mock_territories_api,
        stq_mock,
        load_json,
        web_app_client,
        request_type,
        request_name,
):
    # arrange
    mocked_eda_channel = mock_hiring_candidates_eda_channel(
        load_json('eda_channel_request.json'),
    )
    mock_hiring_data_markup_by_flow(
        responses_by_flows={
            None: load_json('response_data_markup_eats.json'),
            'hiring_data_markup_new_lead_check_processing_flow': (
                load_json('hiring_data_markup_responses/processing_flow.json')
            ),
        },
    )

    headers = {'X-Delivery-Id': 'x delivery id'}
    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    data = request_data[FIELD_DATA]
    params = {'endpoint': request_data[FIELD_ENDPOINT]}

    # act
    await web_app_client.post(ROUTE, json=data, headers=headers, params=params)

    # assert
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_send_to_salesforce'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/eats_channel.json'), stq_args

    assert mocked_eda_channel.times_called == 1
    eda_channel_call = mocked_eda_channel.next_call()['request'].json
    assert eda_channel_call == load_json('eda_channel_response.json')


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
async def test_v1_tickets_create_do_not_send_to_infranaim(
        request_tickets_create,
        mock_hiring_candidates_region,
        mock_hiring_data_markup,
        mock_personal_api,
        mock_territories_api,
        stq_mock,
        load_json,
        web_app_client,
        web_app,
        get_stats_by_label_values,
):
    # arrange
    hiring_candidates_region_mock = mock_hiring_candidates_region(
        response=load_json('hiring_candidates_region_responses/normal.json'),
    )
    headers = {'X-Delivery-Id': 'x delivery id'}
    expected_stats = load_json(EXPECTED_STATS_FILE)

    request_data = load_json(REQUESTS_FILE)['valid'][
        'do_not_send_to_infranaim'
    ]
    data = request_data[FIELD_DATA]
    params = request_data[FIELD_ENDPOINT]

    # act
    await web_app_client.post(
        ROUTE, json=data, headers=headers, params={'endpoint': params},
    )

    # assert
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'salesforce.lead.creation'},
    )
    assert stats == [expected_stats['do_not_send_to_infranaim']]

    assert stq_mock.times_called == 2
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_send_to_salesforce'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/only_to_salesforce.json')

    # compare what we send to candidates
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_candidates_create_lead'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/to_candidates.json')

    assert hiring_candidates_region_mock.times_called == 1
    hiring_candidates_call = hiring_candidates_region_mock.next_call()
    assert dict(hiring_candidates_call['request'].query) == {
        'phone': '+79998887766',
    }


@pytest.mark.parametrize(
    ('request_type', 'request_name'),
    [('invalid', 'phone_empty'), ('invalid', 'phone_invalid')],
)
@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
async def test_v1_tickets_create_with_invalid_phones_send_no_requests(
        request_tickets_create,
        mock_hiring_data_markup,
        mock_personal_api,
        mock_territories_api,
        stq_mock,
        load_json,
        web_app_client,
        web_app,
        get_stats_by_label_values,
        request_type,
        request_name,
):
    # arrange
    headers = {'X-Delivery-Id': 'x delivery id'}
    expected_stats = load_json(EXPECTED_STATS_FILE)

    request_data = load_json(REQUESTS_FILE)[request_type][request_name]
    data = request_data[FIELD_DATA]
    params = request_data[FIELD_ENDPOINT]

    # act
    await web_app_client.post(
        ROUTE, json=data, headers=headers, params={'endpoint': params},
    )

    # assert
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'salesforce.lead.creation'},
    )
    assert stats == [expected_stats[request_name]]

    assert stq_mock.times_called == 0


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.config(HIRING_API_DEFAULT_REGION_ID=12345)
async def test_v1_tickets_create_with_candidates_error_but_has_default_region(
        request_tickets_create,
        mock_hiring_candidates_region,
        mock_hiring_data_markup,
        mock_personal_api,
        mock_territories_api,
        stq_mock,
        load_json,
        web_app_client,
        web_app,
        get_stats_by_label_values,
):
    # arrange
    hiring_candidates_region_mock = mock_hiring_candidates_region(
        response=load_json('hiring_candidates_region_responses/error.json'),
        status=400,
    )
    headers = {'X-Delivery-Id': 'x delivery id'}
    expected_stats = load_json(EXPECTED_STATS_FILE)

    request_data = load_json(REQUESTS_FILE)['valid'][
        'send_to_infranaim_success'
    ]
    data = request_data[FIELD_DATA]
    params = request_data[FIELD_ENDPOINT]

    # act
    await web_app_client.post(
        ROUTE, json=data, headers=headers, params={'endpoint': params},
    )

    # assert
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'salesforce.lead.creation'},
    )
    assert stats == [expected_stats['send_to_infranaim_success']]

    # check that we send to stq messages
    assert stq_mock.times_called == 3

    # compare what we send to salesforce
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_send_to_salesforce'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/to_salesforce.json')

    # compare what we send to candidates
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_candidates_create_lead'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/to_candidates.json')

    # compare what we send to infranaim
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_send_to_infranaim_api'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/to_infranaim.json')

    assert hiring_candidates_region_mock.times_called == 1
    hiring_candidates_call = hiring_candidates_region_mock.next_call()
    assert dict(hiring_candidates_call['request'].query) == {
        'phone': '+79998887766',
    }


@pytest.mark.config(HIRING_API_ENABLE_FILLING_REGION_ID=True)
@pytest.mark.config(HIRING_API_DEFAULT_REGION_ID=10001)
async def test_v1_tickets_create_with_prefilled_region_makes_no_request(
        request_tickets_create,
        mock_hiring_data_markup,
        mock_personal_api,
        mock_territories_api,
        stq_mock,
        load_json,
        web_app_client,
        web_app,
        get_stats_by_label_values,
):
    # arrange
    headers = {'X-Delivery-Id': 'x delivery id'}
    expected_stats = load_json(EXPECTED_STATS_FILE)

    request_data = load_json(REQUESTS_FILE)['valid'][
        'success_with_prefilled_region'
    ]
    data = request_data[FIELD_DATA]
    params = request_data[FIELD_ENDPOINT]

    # act
    await web_app_client.post(
        ROUTE, json=data, headers=headers, params={'endpoint': params},
    )

    # assert
    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'salesforce.lead.creation'},
    )
    assert stats == [expected_stats['send_to_infranaim_success']]

    # check that we sent all messages to stq
    assert stq_mock.times_called == 3
    # compare what we send to salesforce
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_send_to_salesforce'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/to_salesforce.json')

    # compare what we send to candidates
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_candidates_create_lead'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/to_candidates.json')

    # compare what we send to infranaim
    stq_request = stq_mock.next_call()
    assert stq_request['queue_name'] == 'hiring_send_to_infranaim_api'
    assert len(stq_request['args']) == 1
    stq_args = stq_request['args'][0].json
    assert stq_args == load_json('stq_requests/to_infranaim.json')
