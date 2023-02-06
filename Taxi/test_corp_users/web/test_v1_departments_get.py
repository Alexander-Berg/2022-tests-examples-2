import pytest


@pytest.mark.parametrize(
    ['department_id', 'expected_result'],
    [
        pytest.param(
            'd1_1',
            {
                'counters': {'users': 0},
                'id': 'd1_1',
                'limit': {'budget': None},
                'limits': {
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                    'taxi': {'budget': None},
                },
                'name': 'd1_1',
                'parent_id': 'd1',
            },
        ),
        pytest.param(
            'd4_1',
            {
                'counters': {'users': 0},
                'id': 'd4_1',
                'limit': {'budget': 10000},
                'limits': {
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                    'taxi': {'budget': 10000},
                },
                'name': 'd4_1',
                'parent_id': 'd4',
            },
        ),
        pytest.param(
            'd4_1_1',
            {
                'counters': {'users': 0},
                'id': 'd4_1_1',
                'limit': {'budget': None},
                'limits': {
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                    'taxi': {'budget': None},
                },
                'name': 'd4_1_1',
                'parent_id': 'd4_1',
            },
        ),
    ],
)
async def test_get_one_department(
        web_app_client, department_id, expected_result,
):
    response = await web_app_client.get(
        '/v1/departments', params={'department_id': department_id},
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    assert response_json == expected_result


@pytest.mark.parametrize(
    ['department_id', 'expected_result'],
    [
        pytest.param(
            'd1',
            {
                'counters': {'users': 0},
                'id': 'd1',
                'limit': {'budget': None},
                'limits': {
                    'eats2': {'budget': None},
                    'tanker': {'budget': 45116},
                    'taxi': {'budget': None},
                },
                'name': 'd1',
            },
        ),
        pytest.param(
            'd1_1_1',
            {
                'counters': {'users': 0},
                'id': 'd1_1_1',
                'limit': {'budget': None},
                'limits': {
                    'eats2': {'budget': None},
                    'tanker': {'budget': None},
                    'taxi': {'budget': None},
                },
                'name': 'd1_1_1',
                'parent_id': 'd1_1',
                'parents': [
                    {'id': 'd1', 'name': 'd1'},
                    {'id': 'd1_1', 'name': 'd1_1', 'parent_id': 'd1'},
                ],
            },
        ),
    ],
)
async def test_get_one_department_with_parents(
        web_app_client, department_id, expected_result,
):
    response = await web_app_client.get(
        '/v1/departments',
        params={
            'department_id': department_id,
            'include_parent_departments': 1,
        },
    )

    response_json = await response.json()
    assert response.status == 200, response_json

    assert response_json == expected_result


@pytest.mark.parametrize(
    ['department_id', 'expected_status'], [pytest.param('non-existed', 404)],
)
async def test_get_one_department_fail(
        web_app_client, department_id, expected_status,
):
    response = await web_app_client.get(
        '/v1/departments', params={'department_id': department_id},
    )

    response_json = await response.json()
    assert response.status == expected_status, response_json
    assert response_json == {
        'code': 'NOT_FOUND',
        'message': 'Not found',
        'reason': 'Department non-existed not found',
    }
