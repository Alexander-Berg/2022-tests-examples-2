import pytest


@pytest.mark.parametrize(
    ['found_users_amount', 'query_params'],
    [
        pytest.param(
            4,
            {'client_id': 'client3', 'performer_department_id': 'dep1'},
            id='common search',
        ),
        pytest.param(
            1, {'client_id': 'client1'}, id='test without deleted user',
        ),
        pytest.param(
            4,
            {
                'client_id': 'client3',
                'performer_department_id': 'dep1',
                'department_id': 'dep1',
            },
            id='search by dep with sub dep',
        ),
        pytest.param(
            1,
            {
                'client_id': 'client3',
                'performer_department_id': 'dep1',
                'department_id': 'dep1_1',
            },
            id='search by single dep',
        ),
        pytest.param(
            2,  # they are 3, but only 2 are in the allowed department
            {
                'client_id': 'client3',
                'performer_department_id': 'dep1',
                'cost_centers_id': 'cost_center_1',
            },
            id='search by cost center id',
        ),
        pytest.param(
            0,
            {
                'client_id': 'client3',
                'performer_department_id': 'dep1',
                'cost_centers_id': 'cost_center_3',
            },
            id='search by cost center id with no users',
        ),
        pytest.param(
            1,
            {
                'client_id': 'client3',
                'performer_department_id': 'dep1',
                'limit': 1,
            },
            id='with limit search param',
        ),
        pytest.param(
            3,
            {
                'client_id': 'client3',
                'performer_department_id': 'dep1',
                'offset': 1,
            },
            id='with offset search param',
        ),
        pytest.param(
            1,
            {
                'client_id': 'client3',
                'performer_department_id': 'dep1',
                'search': '6543',
            },
            id='search by phone',
        ),
        pytest.param(
            1,
            {
                'client_id': 'client3',
                'performer_department_id': 'dep1',
                'search': 'full',
            },
            id='search by fullname',
        ),
    ],
)
async def test_search_users(
        web_app_client, mock_personal, found_users_amount, query_params,
):
    response = await web_app_client.get(
        '/v2/users/search', params=query_params,
    )
    response_data = await response.json()
    assert len(response_data['items']) == found_users_amount
