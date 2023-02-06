import pytest

EXPECTED_FILE = 'expected.json'
EXPECTED_STATS_FILE = 'expected_stats.json'
EXTERNAL_ID = '4552995ef815c9bba2dae61d5e0f643a'
REQUESTS_FILE = 'requests.json'
ROUTE = '/v2/leads/create'
X_DELIVERY_ID = 'das3tji43tjgj3j9u484tj3fiewo'


@pytest.mark.parametrize(
    ('request_name', 'expected_name'),
    [
        ('without_asset', 'without_asset'),
        ('with_asset', 'with_asset'),
        ('with_phone_pd', 'without_asset'),
        ('phone_without_plus', 'without_asset'),
        ('trash_phone', 'without_asset'),
    ],
)
@pytest.mark.usefixtures(
    'mock_personal_api', 'mock_territories_api', 'mock_hiring_data_markup',
)
async def test_leads_create(
        taxi_hiring_api_web,
        mock_stq_queue,
        load_json,
        request_name,
        expected_name,
):
    request = load_json(REQUESTS_FILE)[request_name]
    expected = load_json(EXPECTED_FILE)[expected_name]

    response = await taxi_hiring_api_web.post(ROUTE, **request)
    assert response.status == 200

    assert mock_stq_queue.times_called == 2

    # SF stq call
    stq_call = mock_stq_queue.next_call()
    stq_call_request = stq_call['request']
    stq_call_json = stq_call_request.json
    assert stq_call_json == expected['sf_stq_call']

    # Candidates stq call
    stq_call = mock_stq_queue.next_call()
    stq_call_request = stq_call['request']
    stq_call_json = stq_call_request.json
    assert stq_call_json == expected['candidates_stq_call']


@pytest.mark.parametrize(
    ('enable_candidates_stq', 'stq_count'), [(True, 2), (False, 1)],
)
@pytest.mark.usefixtures(
    'mock_personal_api', 'mock_territories_api', 'mock_hiring_data_markup',
)
async def test_crete_lead_with_candidates_config(
        taxi_hiring_api_web,
        taxi_config,
        mock_stq_queue,
        load_json,
        enable_candidates_stq,
        stq_count,
):
    request = load_json(REQUESTS_FILE)['without_asset']
    taxi_config.set_values(
        {
            'HIRING_API_ENABLE_CANDIDATES_CREATE_LEAD_STQ': (
                enable_candidates_stq
            ),
        },
    )

    response = await taxi_hiring_api_web.post(ROUTE, **request)
    assert response.status == 200
    assert mock_stq_queue.times_called == stq_count


@pytest.mark.parametrize('use_external_id', [True, False])
@pytest.mark.usefixtures(
    'mock_personal_api', 'mock_territories_api', 'mock_hiring_data_markup',
)
async def test_leads_create_check_id(
        taxi_hiring_api_web,
        mock_stq_queue,
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
    request = load_json(REQUESTS_FILE)['check_external_id']
    response = await taxi_hiring_api_web.post(ROUTE, **request)
    assert response.status == 200
    result = await response.json()
    external_id = result['details']['external_ids']
    assert external_id == [EXTERNAL_ID] if use_external_id else [X_DELIVERY_ID]


@pytest.mark.parametrize(
    ('request_name', 'stats_name'),
    [('success_stats', 'success'), ('error_stats', 'error')],
)
async def test_send_metric_to_solomon_lead_creation(
        request_tickets_create,
        mock_personal_api,
        mock_territories_api,
        mock_hiring_data_markup,
        stq_mock,
        load_json,
        web_app_client,
        web_app,
        get_stats_by_label_values,
        request_name,
        stats_name,
):

    request = load_json(REQUESTS_FILE)[request_name]
    headers = request['headers']
    data = request['json']
    params = request['params']

    await web_app_client.post(ROUTE, json=data, headers=headers, params=params)

    stats = get_stats_by_label_values(
        web_app['context'], {'sensor': 'salesforce.lead.creation'},
    )

    expected_stats = load_json(EXPECTED_STATS_FILE)[stats_name]
    assert stats == [expected_stats]
