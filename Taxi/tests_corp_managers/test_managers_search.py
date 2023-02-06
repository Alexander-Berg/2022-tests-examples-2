import pytest


@pytest.mark.parametrize(
    'post_content, expected_managers, expected_total',
    [
        (
            {
                'client_id': 'client1',
                'roles': ['department_manager', 'department_secretary'],
            },
            [
                {
                    'id': 'department_manager1',
                    'department_id': 'd1',
                    'email': 'department_manager1@client1',
                    'fullname': 'department_manager1',
                    'phone': '+79161237701',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager1',
                },
                {
                    'id': 'department_manager1_1',
                    'department_id': 'd1_1',
                    'email': 'department_manager1_1@client1',
                    'fullname': 'department_manager1_1',
                    'phone': '+79161237702',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager1_1',
                },
                {
                    'id': 'department_manager1_1_1',
                    'department_id': 'd1_1_1',
                    'email': 'department_manager1_1_1@client1',
                    'fullname': 'department_manager1_1_1',
                    'phone': '+79161237703',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager1_1_1',
                },
                {
                    'id': 'department_manager2',
                    'department_id': 'd1',
                    'email': 'department_manager2@client1',
                    'fullname': 'department_manager2',
                    'phone': '+79161237704',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager2',
                },
                {
                    'id': 'secretary1',
                    'department_id': 'd1',
                    'email': 'secretary1@client1',
                    'fullname': 'secretary1',
                    'phone': '+79161237705',
                    'role': 'department_secretary',
                    'yandex_login': 'secretary1',
                },
                {
                    'id': 'department_manager3',
                    'department_id': 'd2',
                    'email': 'department_manager3@client1',
                    'fullname': 'department_manager3',
                    'phone': '7',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager3',
                },
            ],
            6,
        ),
        (
            {
                'client_id': 'client1',
                'department_ids': ['d1_1', 'd1_1_1'],
                'roles': ['department_manager', 'department_secretary'],
            },
            [
                {
                    'id': 'department_manager1_1',
                    'department_id': 'd1_1',
                    'email': 'department_manager1_1@client1',
                    'fullname': 'department_manager1_1',
                    'phone': '+79161237702',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager1_1',
                },
                {
                    'id': 'department_manager1_1_1',
                    'department_id': 'd1_1_1',
                    'email': 'department_manager1_1_1@client1',
                    'fullname': 'department_manager1_1_1',
                    'phone': '+79161237703',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager1_1_1',
                },
            ],
            2,
        ),
        (
            {
                'client_id': 'client1',
                'offset': 3,
                'limit': 1,
                'sort': [{'field': 'fullname', 'direction': 'desc'}],
                'roles': ['department_manager', 'department_secretary'],
            },
            [
                {
                    'id': 'department_manager1_1_1',
                    'department_id': 'd1_1_1',
                    'email': 'department_manager1_1_1@client1',
                    'fullname': 'department_manager1_1_1',
                    'phone': '+79161237703',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager1_1_1',
                },
            ],
            6,
        ),
        (
            {
                'client_id': 'client1',
                'search': 'manager1',
                'roles': ['department_manager', 'department_secretary'],
            },
            [
                {
                    'id': 'department_manager1',
                    'department_id': 'd1',
                    'email': 'department_manager1@client1',
                    'fullname': 'department_manager1',
                    'phone': '+79161237701',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager1',
                },
                {
                    'id': 'department_manager1_1',
                    'department_id': 'd1_1',
                    'email': 'department_manager1_1@client1',
                    'fullname': 'department_manager1_1',
                    'phone': '+79161237702',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager1_1',
                },
                {
                    'id': 'department_manager1_1_1',
                    'department_id': 'd1_1_1',
                    'email': 'department_manager1_1_1@client1',
                    'fullname': 'department_manager1_1_1',
                    'phone': '+79161237703',
                    'role': 'department_manager',
                    'yandex_login': 'department_manager1_1_1',
                },
            ],
            3,
        ),
        (
            {'client_id': 'client1', 'search': 'Bill', 'roles': ['manager']},
            [
                {
                    'id': 'manager2',
                    'fullname': 'Bill',
                    'phone': '+79291112202',
                    'role': 'manager',
                    'yandex_login': 'bill',
                },
            ],
            1,
        ),
    ],
)
async def test_managers_search(
        taxi_corp_managers, post_content, expected_managers, expected_total,
):
    response = await taxi_corp_managers.post(
        '/v1/managers/search', json=post_content,
    )

    response_json = response.json()
    assert response.status == 200, response_json

    assert response_json['total'] == expected_total

    if 'sort' not in post_content:
        for item in expected_managers:
            assert item in response_json['managers']
    else:
        assert response_json['managers'] == expected_managers
