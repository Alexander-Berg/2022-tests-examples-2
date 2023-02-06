import pytest


@pytest.mark.parametrize(
    'user_id, expected_code, expected_departments',
    [
        pytest.param(
            'user_id_1',
            200,
            [{'_id': 'department_id_1'}, {'_id': 'department_id_2'}],
        ),
        pytest.param('user_id_2', 200, []),
        pytest.param('user_id_3', 404, []),
    ],
)
async def test_department(
        taxi_corp_integration_api,
        user_id,
        expected_code,
        expected_departments,
):
    response = await taxi_corp_integration_api.post(
        '/v1/departments/by_user', json={'user_id': user_id},
    )

    assert response.status == expected_code
    if expected_code == 200:
        assert (await response.json())['departments'] == expected_departments
