import pytest


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.parametrize(
    'testcase',
    (
        'default',
        'default_english',
        'full_query',
        'user_by_license',
        'user_by_employment_types',
        'user_by_city_and_tariff',
        'user_by_date_active',
        'user_by_source_park_db',
        'user_by_statuses',
        'with_circular',
        'pagination',
        'eats_consumer',
        'user_by_eats_statuses',
    ),
)
@pytest.mark.now('2021-03-03T03:10:00+03:00')
async def test_v1_leads_list(
        tvm_client,
        mockserver,
        taxi_hiring_partners_app_web,
        load_json,
        mock_user_permissions,
        mock_candidates_v1_leads_list,
        testcase,
):
    # arrange
    requests_data = load_json('requests.json')[testcase]
    request = requests_data['REQUEST']
    candidates_request = requests_data['CANDIDATES_REQUEST']
    responses = load_json('responses.json')
    expected_response = responses.get(testcase, responses['default'])
    candidates_responses = load_json('candidates_responses.json')
    candidates_response = candidates_responses.get(
        testcase, candidates_responses['default'],
    )
    permissions_mock = mock_user_permissions(requests_data['PERMISSIONS'])
    candidates_mock = mock_candidates_v1_leads_list(candidates_response)

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/v1/leads/list', json=request['data'], headers=request['headers'],
    )

    # assert
    assert response.status == request['status']
    assert await response.json() == expected_response

    assert permissions_mock.has_calls
    assert candidates_mock.has_calls
    call_request = candidates_mock.next_call()['request']
    assert (
        call_request.headers['X-Consumer-Id'] == candidates_request['consumer']
    )
    check_query_dict_equality(candidates_request['body'], call_request.json)


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.parametrize(
    'testcase',
    ('user_not_found', 'invalid_user_by_date_active_missing_active_date'),
)
@pytest.mark.now('2021-03-03T03:10:00+03:00')
async def test_v1_leads_list_errors(
        tvm_client,
        mockserver,
        taxi_hiring_partners_app_web,
        load_json,
        mock_user_permissions,
        mock_candidates_v1_leads_list,
        testcase,
):
    # arrange
    requests_data = load_json('requests.json')[testcase]
    request = requests_data['REQUEST']
    responses = load_json('responses.json')
    expected_response = responses.get(testcase, responses['default'])
    candidates_responses = load_json('candidates_responses.json')
    candidates_response = candidates_responses.get(
        testcase, candidates_responses['default'],
    )
    mock_user_permissions(requests_data['PERMISSIONS'])
    mock_candidates_v1_leads_list(candidates_response)

    # act
    response = await taxi_hiring_partners_app_web.post(
        '/v1/leads/list', json=request['data'], headers=request['headers'],
    )

    # assert
    assert response.status == request['status']
    assert await response.json() == expected_response


def check_query_dict_equality(target, actual):
    def _sort_lists_in_query(dict_):
        for value in dict_.values():
            if isinstance(value, list):
                value.sort()

    _sort_lists_in_query(target)
    _sort_lists_in_query(actual)
    assert target == actual
