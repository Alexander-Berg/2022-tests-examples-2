import pytest


@pytest.mark.parametrize(
    ['headers', 'query_params', 'expected_response'],
    [
        pytest.param(
            {'X-YaTAxi-Corp-ACL-Client-Id': 'client3'},
            {},
            {
                'limit': 100,
                'offset': 0,
                'total_amount': 2,
                'items': [
                    {
                        'id': 'dep1',
                        'limits': {
                            'eats2': {'budget': 100},
                            'tanker': {'budget': None},
                            'taxi': {'budget': 200.2},
                        },
                        'name': 'department 1',
                        'parent_id': None,
                    },
                    {
                        'id': 'dep1_1',
                        'limits': {
                            'eats2': {'budget': None},
                            'tanker': {'budget': None},
                            'taxi': {'budget': None},
                        },
                        'name': 'department 1.1',
                        'parent_id': 'dep1',
                    },
                ],
            },
            id='empty query',
        ),
        pytest.param(
            {'X-YaTAxi-Corp-ACL-Client-Id': 'client3'},
            {'limit': 1},
            {
                'limit': 1,
                'offset': 0,
                'total_amount': 2,
                'items': [
                    {
                        'id': 'dep1',
                        'limits': {
                            'eats2': {'budget': 100},
                            'tanker': {'budget': None},
                            'taxi': {'budget': 200.2},
                        },
                        'name': 'department 1',
                        'parent_id': None,
                    },
                ],
            },
            id='test limit',
        ),
        pytest.param(
            {'X-YaTAxi-Corp-ACL-Client-Id': 'client3'},
            {'offset': 1},
            {
                'limit': 100,
                'offset': 1,
                'total_amount': 2,
                'items': [
                    {
                        'id': 'dep1_1',
                        'limits': {
                            'eats2': {'budget': None},
                            'tanker': {'budget': None},
                            'taxi': {'budget': None},
                        },
                        'name': 'department 1.1',
                        'parent_id': 'dep1',
                    },
                ],
            },
            id='test offset',
        ),
        pytest.param(
            {
                'X-YaTAxi-Corp-ACL-Client-Id': 'client3',
                'X-YaTAxi-Corp-ACL-Department-Id': 'dep1_1',
            },
            {},
            {
                'limit': 100,
                'offset': 0,
                'total_amount': 1,
                'items': [
                    {
                        'id': 'dep1_1',
                        'limits': {
                            'eats2': {'budget': None},
                            'tanker': {'budget': None},
                            'taxi': {'budget': None},
                        },
                        'name': 'department 1.1',
                        'parent_id': 'dep1',
                    },
                ],
            },
            id='test access department_id',
        ),
    ],
)
async def test_search_departments(
        web_app_client, headers, query_params, expected_response,
):
    response = await web_app_client.get(
        '/integration/v2/departments/list',
        params=query_params,
        headers=headers,
    )
    response_data = await response.json()
    assert response_data == expected_response
