import pytest


@pytest.mark.parametrize(
    ['yandex_uid', 'expected_code', 'expected_response'],
    [
        pytest.param(
            'client1_uid',
            200,
            {
                'client_id': 'client1',
                'role': 'client',
                'permissions': [
                    'taxi',
                    'taxi_client',
                    'taxi_department_create',
                    'taxi_department_part',
                    'taxi_department_full',
                    'taxi_other',
                    'logistics',
                ],
            },
            id='test client role',
        ),
        pytest.param(
            'department_manager1_uid',
            200,
            {
                'client_id': 'client1',
                'role': 'department_manager',
                'department_id': 'd1',
                'permissions': [
                    'taxi',
                    'taxi_department_create',
                    'taxi_department_part',
                    'taxi_department_full',
                    'taxi_other',
                ],
            },
            id='test department manager role',
        ),
        pytest.param(
            'secretary1_uid',
            200,
            {
                'client_id': 'client1',
                'role': 'department_secretary',
                'department_id': 'd1',
                'permissions': ['taxi', 'taxi_department_part', 'taxi_other'],
            },
            id='test department secretary role',
        ),
        pytest.param(
            'boris_uid',
            200,
            {
                'client_id': 'client2',
                'role': 'manager',
                'permissions': [
                    'taxi',
                    'taxi_client',
                    'taxi_department_create',
                    'taxi_department_part',
                    'taxi_department_full',
                    'taxi_other',
                    'logistics',
                ],
            },
            id='test manager role',
        ),
        pytest.param(
            'not_existed_yandex_uid',
            404,
            None,
            id='test not existed yandex uid',
        ),
    ],
)
async def test_managers_access_data(
        taxi_corp_managers, yandex_uid, expected_code, expected_response,
):
    response = await taxi_corp_managers.post(
        '/v1/managers/access-data', params={'yandex_uid': yandex_uid},
    )
    assert response.status == expected_code

    if response.status == 200:

        assert response.json() == expected_response
