import pytest

from tests_access_control.helpers import admin_users


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
@pytest.mark.parametrize(
    'create_user_test_case',
    [
        admin_users.CreateUserTestCase(
            id_for_pytest='success: user doesn`t exists',
            create_user_request=admin_users.CreateUserRequest(
                provider='yandex', provider_user_id='1134567890123456',
            ),
            expected_status_code=200,
            expected_response={},
        ),
        admin_users.CreateUserTestCase(
            id_for_pytest='success restapp: user doesn`t exists',
            create_user_request=admin_users.CreateUserRequest(
                provider='restapp', provider_user_id='136263',
            ),
            expected_status_code=200,
            expected_response={},
        ),
        admin_users.CreateUserTestCase(
            id_for_pytest='failed: user exists',
            create_user_request=admin_users.CreateUserRequest(
                provider='yandex', provider_user_id='1111111111111111',
            ),
            expected_status_code=409,
            expected_response={
                'code': 'already_exists',
                'message': (
                    'User \'yandex\':\'1111111111111111\' has already existed'
                ),
            },
        ),
    ],
    ids=admin_users.CreateUserTestCase.get_id_for_pytest,
)
async def test_create_user(taxi_access_control, create_user_test_case):
    await admin_users.create_user(
        taxi_access_control,
        create_user_test_case.create_user_request,
        expected_status_code=create_user_test_case.expected_status_code,
        expected_response_json=create_user_test_case.expected_response,
    )
