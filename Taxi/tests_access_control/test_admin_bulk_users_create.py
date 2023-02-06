import pytest

from tests_access_control.helpers import admin_users


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
@pytest.mark.parametrize(
    'bulk_create_users_test_case',
    [
        admin_users.BulkCreateUsersTestCase(
            id_for_pytest='all users doesn`t exists',
            bulk_create_users_request=[
                admin_users.CreateUserRequest(
                    provider='yandex', provider_user_id='1134567890123456',
                ),
                admin_users.CreateUserRequest(
                    provider='yandex', provider_user_id='1134567890123457',
                ),
            ],
            expected_status_code=200,
            expected_response={
                'created_users': [
                    {
                        'provider': 'yandex',
                        'provider_user_id': '1134567890123456',
                    },
                    {
                        'provider': 'yandex',
                        'provider_user_id': '1134567890123457',
                    },
                ],
                'existing_users': [],
                'invalid_users': [],
            },
        ),
        admin_users.BulkCreateUsersTestCase(
            id_for_pytest='all type of users',
            bulk_create_users_request=[
                admin_users.CreateUserRequest(
                    provider='yandex', provider_user_id='1134567890123456',
                ),
                admin_users.CreateUserRequest(
                    provider='yandex', provider_user_id='1111111111111111',
                ),
            ],
            expected_status_code=200,
            expected_response={
                'created_users': [
                    {
                        'provider': 'yandex',
                        'provider_user_id': '1134567890123456',
                    },
                ],
                'existing_users': [
                    {
                        'provider': 'yandex',
                        'provider_user_id': '1111111111111111',
                    },
                ],
                'invalid_users': [],
            },
        ),
    ],
    ids=admin_users.CreateUserTestCase.get_id_for_pytest,
)
async def test_create_user(taxi_access_control, bulk_create_users_test_case):
    await admin_users.bulk_create_users(
        taxi_access_control,
        bulk_create_users_test_case.bulk_create_users_request,
        expected_status_code=bulk_create_users_test_case.expected_status_code,
        expected_response_json=bulk_create_users_test_case.expected_response,
    )
