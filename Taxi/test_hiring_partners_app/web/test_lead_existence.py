import pytest

PERMISSIONS_EXP_CONFIG_NAME = 'hiring_partners_app_permission_flags'
PERMISSIONS_EXP_CONSUMER = 'hiring/permission_flags'


@pytest.mark.config(
    HIRING_PARTNERS_APP_PERMISSIONS_SETTINGS=[
        {
            'consumer_name': 'hiring/permission_flags',
            'config3_name': 'hiring_partners_app_permission_flags',
        },
    ],
)
@pytest.mark.now('2021-03-03T03:10:00+03:00')
@pytest.mark.parametrize(
    ['request_name', 'existence', 'metarole'],
    [
        ('driver_license_lead_exists', 'exists', 'agent'),
        ('phone_lead_exists', 'exists', 'agent'),
        ('allowed_channel', 'not_exists', 'scout'),
        ('ban_period_has_expired', 'not_exists', 'agent'),
    ],
)
async def test_lead_existence(
        request_name,
        existence,
        metarole,
        mock_candidates_v1_leads_list,
        mock_configs3,
        taxi_hiring_partners_app_web,
        load_json,
        personal,
):
    # arrange
    restrictions_expected = load_json(
        'experiments_mock_data/restrictions_expected.json',
    )[request_name]
    exp3_responses = load_json('experiments_mock_data/exp3_responses.json')
    experiments3_mock = mock_configs3(exp3_responses[metarole])

    expected_candidates_request = load_json(
        'candidates_mock_data/candidates_requests.json',
    )[request_name]
    candidates_response = load_json(
        'candidates_mock_data/candidates_response.json',
    )[existence]
    hiring_candidates_mock = mock_candidates_v1_leads_list(candidates_response)

    request = load_json('requests.json')[request_name]
    expected_response = load_json('expected_responses.json')[existence]

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/v1/check/lead', json=request['body'], headers=request['headers'],
    )

    # assert
    assert experiments3_mock.has_calls
    assert experiments3_mock.times_called == 2
    permission_flags_config3 = experiments3_mock.next_call()['request'].json
    assert permission_flags_config3['consumer'] == PERMISSIONS_EXP_CONSUMER
    assert (
        permission_flags_config3['config_name'] == PERMISSIONS_EXP_CONFIG_NAME
    )

    exp3_request = experiments3_mock.next_call()['request'].json
    assert exp3_request == restrictions_expected

    assert hiring_candidates_mock.has_calls
    candidates_request = hiring_candidates_mock.next_call()['request'].json
    assert candidates_request == expected_candidates_request

    body = await response.json()
    assert body == expected_response['body']
    assert response.status == expected_response['status']


@pytest.mark.config(
    HIRING_PARTNERS_APP_PERMISSIONS_SETTINGS=[
        {
            'consumer_name': 'hiring/permission_flags',
            'config3_name': 'hiring_partners_app_permission_flags',
        },
    ],
)
async def test_no_restrictions(
        taxi_hiring_partners_app_web, load_json, personal, mock_configs3,
):
    # arrange
    restrictions_expected = load_json(
        'experiments_mock_data/restrictions_expected.json',
    )['no_restrictions']
    exp3_responses = load_json('experiments_mock_data/exp3_responses.json')
    experiments3_mock = mock_configs3(exp3_responses['eats_freelancer'])

    request = load_json('requests.json')['no_restrictions']
    expected_response = load_json('expected_responses.json')['no_restrictions']

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/v1/check/lead', json=request['body'], headers=request['headers'],
    )

    # assert
    assert experiments3_mock.has_calls
    assert experiments3_mock.times_called == 2

    permission_flags_config3 = experiments3_mock.next_call()['request'].json
    assert permission_flags_config3['consumer'] == PERMISSIONS_EXP_CONSUMER
    assert (
        permission_flags_config3['config_name'] == PERMISSIONS_EXP_CONFIG_NAME
    )

    exp3_request = experiments3_mock.next_call()['request'].json
    assert exp3_request == restrictions_expected

    body = await response.json()
    assert body == expected_response['body']
    assert response.status == expected_response['status']


@pytest.mark.parametrize('request_name', ['bad_request', 'user_not_found'])
async def test_without_call_candidates(
        request_name, taxi_hiring_partners_app_web, load_json, personal,
):
    # arrange
    request = load_json('requests.json')[request_name]
    expected_response = load_json('expected_responses.json')[request_name]

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/v1/check/lead', json=request['body'], headers=request['headers'],
    )

    # assert
    body = await response.json()
    assert body == expected_response['body']
    assert response.status == expected_response['status']
