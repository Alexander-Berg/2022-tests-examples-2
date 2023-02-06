import pytest


ROUTE = '/v1/leads/create'

REQUESTS_FILE = 'requests.json'
HIRING_API_RESPONSES_FILE = 'hiring_api_responses.json'
EXPECTED_RESPONSES_FILE = 'expected_responses.json'
EXPECTED_HIRING_API_FILE = 'expected_hiring_api_calls.json'


@pytest.mark.usefixtures('mock_personal_api', 'mock_data_markup', 'tvm_client')
@pytest.mark.parametrize(
    (
        'request_name',
        'hiring_api_response_name',
        'expected_response_name',
        'expected_call_name',
    ),
    [
        ('valid_agent', 'success', 'success', 'valid_agent'),
        ('valid_agent', 'failure', 'failure', 'valid_agent'),
        ('valid_scout', 'success', 'success', 'valid_scout'),
        ('agent_with_asset', 'success', 'success', 'agent_with_asset'),
    ],
)
@pytest.mark.now('2021-03-03T03:10:00+03:00')
async def test_v1_leads_create(
        mock_hiring_api_v2_leads_create,
        taxi_hiring_partners_app_web,
        load_json,
        request_name,
        hiring_api_response_name,
        expected_response_name,
        expected_call_name,
):
    request = load_json(REQUESTS_FILE)[request_name]
    hiring_api_response = load_json(HIRING_API_RESPONSES_FILE)[
        hiring_api_response_name
    ]
    hiring_api_mock = mock_hiring_api_v2_leads_create(
        hiring_api_response['body'], hiring_api_response['status'],
    )

    response = await taxi_hiring_partners_app_web.post(
        ROUTE, json=request['data'], headers=request['headers'],
    )

    expected_response = load_json(EXPECTED_RESPONSES_FILE)[
        expected_response_name
    ]
    assert response.status == expected_response['status']
    body = await response.json()
    assert body == expected_response['body']

    expected_hiring_api = load_json(EXPECTED_HIRING_API_FILE)[
        expected_call_name
    ]
    assert hiring_api_mock.times_called == expected_hiring_api['times_called']

    hiring_api_call = hiring_api_mock.next_call()
    request = hiring_api_call['request']
    x_delivery_id = request.headers['X-Delivery-Id']
    query = dict(request.query)
    json = request.json
    assert x_delivery_id == expected_hiring_api['x_delivery_id']
    assert query == expected_hiring_api['query']
    assert json == expected_hiring_api['json']


@pytest.mark.parametrize(
    (
        'request_name',
        'hiring_api_response_name',
        'expected_response_name',
        'expected_call_name',
    ),
    [
        ('valid_agent', 'success', 'success', 'valid_agent'),
        ('valid_agent', 'failure', 'hiring_api_failure', 'valid_agent'),
        ('valid_scout', 'success', 'success', 'valid_scout'),
        ('agent_with_asset', 'success', 'success', 'agent_with_asset'),
    ],
)
@pytest.mark.config(
    HIRING_PARTNERS_APP_LEADS_CREATE_FLOW_WITHOUT_MARKUP_ENABLED=True,
)
@pytest.mark.now('2021-03-03T03:10:00+03:00')
async def test_v1_leads_create_2(
        mock_personal_api,
        mock_data_markup,
        tvm_client,
        mock_hiring_api_external_v2_leads_create,
        taxi_hiring_partners_app_web,
        load_json,
        request_name,
        hiring_api_response_name,
        expected_response_name,
        expected_call_name,
):
    # arrange
    request = load_json('requests.json')[request_name]
    hiring_api_response = load_json('hiring_api_responses.json')[
        hiring_api_response_name
    ]
    hiring_api_mock = mock_hiring_api_external_v2_leads_create(
        hiring_api_response['body'], hiring_api_response['status'],
    )
    expected_response = load_json('expected_responses.json')[
        expected_response_name
    ]
    expected_hiring_api = load_json('expected_hiring_api_external_calls.json')[
        expected_call_name
    ]

    # act
    response = await taxi_hiring_partners_app_web.post(
        ROUTE, json=request['data'], headers=request['headers'],
    )

    # assert
    assert response.status == expected_response['status']
    assert await response.json() == expected_response['body']

    assert hiring_api_mock.times_called == expected_hiring_api['times_called']
    hiring_api_request = hiring_api_mock.next_call()['request']
    x_delivery_id = hiring_api_request.headers['X-Delivery-Id']
    assert x_delivery_id == expected_hiring_api['x_delivery_id']
    assert dict(hiring_api_request.query) == expected_hiring_api['query']
    assert hiring_api_request.json == expected_hiring_api['json']
