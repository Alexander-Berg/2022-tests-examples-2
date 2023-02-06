import pytest

from tests_access_control.helpers import admin_users_to_system


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
@pytest.mark.parametrize(
    'add_users_to_system_test_case',
    [
        admin_users_to_system.AddUsersToSystemTestCase(
            id_for_pytest='add users',
            add_users_to_system_request=(
                admin_users_to_system.AddUsersToSystemRequest(
                    system='system1',
                    users=[
                        admin_users_to_system.User(
                            provider='yandex',
                            provider_user_id='1111111111111111',
                        ),
                        admin_users_to_system.User(
                            provider='yandex',
                            provider_user_id='1134567890123456',
                        ),
                        admin_users_to_system.User(
                            provider='yandex',
                            provider_user_id='0000000000000000',
                        ),
                    ],
                    groups=['group2', 'non_existing'],
                )
            ),
            expected_response={
                'invalid_users': [],
                'non_existing_users': [
                    {
                        'provider': 'yandex',
                        'provider_user_id': '0000000000000000',
                    },
                ],
                'non_existing_groups': ['non_existing'],
            },
        ),
    ],
    ids=admin_users_to_system.AddUsersToSystemTestCase.get_id_for_pytest,
)
async def test_bulk_add_users_to_system(
        taxi_access_control, add_users_to_system_test_case,
):
    await admin_users_to_system.add_users_to_system(
        taxi_access_control,
        add_users_to_system_test_case.add_users_to_system_request,
        expected_status_code=200,
        expected_response_json=(
            add_users_to_system_test_case.expected_response
        ),
    )
