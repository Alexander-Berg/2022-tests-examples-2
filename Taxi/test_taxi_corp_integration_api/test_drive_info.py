import pytest


@pytest.mark.parametrize(
    'expected_response',
    [
        pytest.param(
            {
                'results': [
                    {
                        'account_id': 1,
                        'client_id': 'client_id_1',
                        'user_id': 'user_id_1',
                        'personal_phone_id': 'pd_id_1',
                        'department_id': 'department_id_1',
                        'role_id': 'role_id_1',
                        'yandex_uid': 'yandex_uid_1',
                    },
                    {
                        'account_id': 3,
                        'client_id': 'client_id_3',
                        'user_id': 'user_id_3',
                        'personal_phone_id': 'pd_id_3',
                        'department_id': None,
                        'yandex_uid': '',
                        'client_billing_id': '123',
                    },
                ],
            },
            id='happy_path',
        ),
    ],
)
async def test_drive_info(taxi_corp_integration_api, expected_response):
    response = await taxi_corp_integration_api.post(
        '/v1/drive/info', json={'account_ids': [1, 3, 4]},
    )

    data = await response.json()

    assert response.status == 200, data
    assert data == expected_response
