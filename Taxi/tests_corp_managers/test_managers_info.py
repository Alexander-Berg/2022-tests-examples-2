import pytest


@pytest.mark.parametrize(
    'params, expected_status_code, expected_response',
    [
        (
            {'manager_id': 'department_manager1'},
            200,
            {
                'id': 'department_manager1',
                'department_id': 'd1',
                'email': 'department_manager1@client1',
                'fullname': 'department_manager1',
                'phone': '+79161237701',
                'role': 'department_manager',
                'yandex_login': 'department_manager1',
            },
        ),
        (
            {'manager_id': 'manager1'},
            200,
            {
                'id': 'manager1',
                'fullname': 'Emily',
                'phone': '+79291112201',
                'yandex_login': 'emily',
                'role': 'manager',
            },
        ),
        (
            {'yandex_uid': 'emily_uid'},
            200,
            {
                'id': 'manager1',
                'fullname': 'Emily',
                'phone': '+79291112201',
                'yandex_login': 'emily',
                'role': 'manager',
            },
        ),
        (
            {'manager_id': 'client1'},
            200,
            {
                'id': 'client1',
                'yandex_login': 'client1_login',
                'role': 'client',
            },
        ),
        (
            {},
            400,
            {
                'code': 'BadRequest',
                'message': 'Missing manager_id or yandex_uid in query',
            },
        ),
        (
            {'manager_id': 'not_existed_id'},
            404,
            {'code': 'NotFound', 'message': 'Manager not found'},
        ),
    ],
)
async def test_managers_info(
        taxi_corp_managers, params, expected_status_code, expected_response,
):
    response = await taxi_corp_managers.post(
        '/v1/managers/info', params=params,
    )

    response_json = response.json()
    assert response.status == expected_status_code, response_json
    assert response_json == expected_response
