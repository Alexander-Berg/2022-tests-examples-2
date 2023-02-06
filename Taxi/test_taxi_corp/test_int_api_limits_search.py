import pytest

from taxi_corp.api import routes


BASE_LIMIT_RESPONSE = {
    'can_edit': True,
    'categories': ['econom'],
    'client_id': 'client1',
    'geo_restrictions': [
        {
            'destination': 'destination_restriction_id',
            'source': 'source_restriction_1',
        },
    ],
    'id': 'limit1',
    'limits': {
        'orders_amount': {'period': 'day', 'value': 12},
        'orders_cost': {'period': 'month', 'value': '1000'},
    },
    'service': 'taxi',
    'time_restrictions': [
        {
            'days': ['mo', 'tu', 'we', 'th', 'fr'],
            'end_time': '18:40:00',
            'start_time': '10:30:00',
            'type': 'weekly_date',
        },
    ],
    'title': 'limit',
}


@pytest.mark.parametrize(
    [
        'passport_mock',
        'corp_users_search_response',
        'expected_code',
        'expected_response',
    ],
    [
        pytest.param(
            'client3',
            {
                'limits': [BASE_LIMIT_RESPONSE],
                'limit': 1,
                'offset': 0,
                'total_amount': 1,
            },
            200,
            {
                'items': [BASE_LIMIT_RESPONSE],
                'limit': 1,
                'offset': 0,
                'total_amount': 1,
            },
            id='common-flow',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_search_limits_proxy(
        taxi_corp_real_auth_client,
        mock_corp_users,
        passport_mock,
        corp_users_search_response,
        expected_code,
        expected_response,
):
    mock_corp_users.data.search_limit_response = corp_users_search_response
    mock_corp_users.data.search_limit_code = expected_code

    params = {'limit': '1', 'offset': '0', 'service': 'taxi'}
    response = await taxi_corp_real_auth_client.get(
        f'{routes.API_PREFIX}/2.0/limits/search', params=params,
    )
    response_data = await response.json()
    assert response.status == expected_code, response_data
    assert response_data == expected_response

    assert mock_corp_users.search_limits.next_call()['request'].query == dict(
        params, client_id='client3', performer_department_id='dep1',
    )
