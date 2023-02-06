import pytest

LAST_USER_CURSOR = 'djEgMTYxNDUwNDYwMC4wMDIgdGVzdF91c2VyXzc='
ALL_USERS_IDS = [
    '857ddf8d410446679b198f80324be32e',
    'test_user_3',
    'test_user_4',
    'test_user_5',
    'test_user_1',
    'test_user_7',
]


@pytest.mark.parametrize(
    ['query_params', 'response_params', 'expected_user_ids'],
    [
        pytest.param(
            {'client_id': 'client3', 'limit': 2},
            {
                'total_amount': 6,
                'limit': 2,
                'next_cursor': 'djEgTm9uZSB0ZXN0X3VzZXJfMw==',
            },
            ALL_USERS_IDS[:2],
            id='start list',
        ),
        pytest.param(
            {
                'client_id': 'client3',
                'limit': 3,
                'cursor': 'djEgTm9uZSB0ZXN0X3VzZXJfMw==',
            },
            {
                'total_amount': 6,
                'limit': 3,
                'next_cursor': 'djEgMTYxNDUwNDYwMC4wMDEgdGVzdF91c2VyXzE=',
            },
            ALL_USERS_IDS[2:5],
            id='cursor list',
        ),
        pytest.param(
            {
                'client_id': 'client3',
                'limit': 100,
                'cursor': 'djEgMTYxNDUwNDYwMC4wMDEgdGVzdF91c2VyXzE=',
            },
            {'total_amount': 6, 'next_cursor': LAST_USER_CURSOR},
            ALL_USERS_IDS[5:],
            id='cursor list with last user',
        ),
        pytest.param(
            {'client_id': 'client3', 'limit': 1000},
            {'total_amount': 6, 'limit': 100, 'next_cursor': LAST_USER_CURSOR},
            ALL_USERS_IDS,
            id='full list',
        ),
        pytest.param(
            {
                'client_id': 'client3',
                'limit': 100,
                'cursor': 'djEgMTYxNDUwNDYwMC4wMDIgdGVzdF91c2VyXzc=',
            },
            {'total_amount': 6, 'limit': 100, 'next_cursor': None},
            [],
            id='empty list',
        ),
    ],
)
async def test_list_users(
        web_app_client,
        mock_personal,
        query_params,
        response_params,
        expected_user_ids,
):
    response = await web_app_client.get('/v2/users/list', params=query_params)
    response_data = await response.json()
    assert [u['id'] for u in response_data['items']] == expected_user_ids
    assert response_data.get('cursor') == query_params.get('cursor')
    for param, value in response_params.items():
        assert response_data.get(param) == value, f'{param} must be {value}'
