import pytest

from tests_access_control.helpers import admin_users_to_system


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
@pytest.mark.parametrize(
    'add_user_to_system_test_case',
    [
        admin_users_to_system.AddUserToSystemTestCase(
            id_for_pytest='Add to groups',
            add_user_to_system_request=(
                admin_users_to_system.AddUserToSystemRequest(
                    system='system1',
                    provider='yandex',
                    provider_user_id='1134567890123456',
                    groups=['group1', 'group2'],
                )
            ),
            expected_response={},
        ),
        admin_users_to_system.AddUserToSystemTestCase(
            id_for_pytest='user exists but in other system',
            add_user_to_system_request=(
                admin_users_to_system.AddUserToSystemRequest(
                    system='system2',
                    provider='yandex',
                    provider_user_id='1111111111111111',
                    groups=['group1'],
                )
            ),
            expected_response={},
        ),
    ],
    ids=admin_users_to_system.AddUserToSystemTestCase.get_id_for_pytest,
)
async def test_add_user_success(
        taxi_access_control, add_user_to_system_test_case,
):
    await admin_users_to_system.add_user_to_system(
        taxi_access_control,
        add_user_to_system_test_case.add_user_to_system_request,
        expected_status_code=200,
        expected_response_json=(
            add_user_to_system_test_case.expected_response
        ),
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
@pytest.mark.parametrize(
    'add_user_to_system_test_case',
    [
        admin_users_to_system.AddUserToSystemTestCase(
            id_for_pytest='user exists in same system',
            add_user_to_system_request=(
                admin_users_to_system.AddUserToSystemRequest(
                    system='system1',
                    provider='yandex',
                    provider_user_id='1111111111111111',
                    groups=['group2'],
                )
            ),
            expected_response={
                'code': 'user_already_exists_in_system',
                'message': (
                    'User with id \'1\' has already existed'
                    ' in system \'system1\''
                ),
            },
        ),
    ],
    ids=admin_users_to_system.AddUserToSystemTestCase.get_id_for_pytest,
)
async def test_add_user_conflict(
        taxi_access_control, add_user_to_system_test_case,
):
    await admin_users_to_system.add_user_to_system(
        taxi_access_control,
        add_user_to_system_test_case.add_user_to_system_request,
        expected_status_code=409,
        expected_response_json=(
            add_user_to_system_test_case.expected_response
        ),
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
@pytest.mark.parametrize(
    'add_user_to_system_test_case',
    [
        admin_users_to_system.AddUserToSystemTestCase(
            id_for_pytest='user not found',
            add_user_to_system_request=(
                admin_users_to_system.AddUserToSystemRequest(
                    system='system1',
                    provider='yandex',
                    provider_user_id='1165432109876543',
                    groups=['group1'],
                )
            ),
            expected_response={
                'code': 'user_not_found',
                'message': 'User \'yandex\':\'1165432109876543\' not found',
            },
        ),
        admin_users_to_system.AddUserToSystemTestCase(
            id_for_pytest='system doesn`t exists',
            add_user_to_system_request=(
                admin_users_to_system.AddUserToSystemRequest(
                    system='system100',
                    provider='yandex',
                    provider_user_id='1134567890123456',
                    groups=['group1'],
                )
            ),
            expected_response={
                'code': 'groups_not_found',
                'message': (
                    'Groups \'group1\' not found' ' in system \'system100\''
                ),
            },
        ),
        admin_users_to_system.AddUserToSystemTestCase(
            id_for_pytest='group system doesn`t exists',
            add_user_to_system_request=(
                admin_users_to_system.AddUserToSystemRequest(
                    system='system1',
                    provider='yandex',
                    provider_user_id='1134567890123456',
                    groups=['group1', 'group2', 'group3'],
                )
            ),
            expected_response={
                'code': 'groups_not_found',
                'message': (
                    'Groups \'group3\' not found' ' in system \'system1\''
                ),
            },
        ),
        admin_users_to_system.AddUserToSystemTestCase(
            id_for_pytest='group does not exist',
            add_user_to_system_request=(
                admin_users_to_system.AddUserToSystemRequest(
                    system='system1',
                    provider='yandex',
                    provider_user_id='1134567890123456',
                    groups=['group_system_meow'],
                )
            ),
            expected_response={
                'code': 'groups_not_found',
                'message': (
                    'Groups \'group_system_meow\' not found'
                    ' in system \'system1\''
                ),
            },
        ),
        admin_users_to_system.AddUserToSystemTestCase(
            id_for_pytest='group exists in other system',
            add_user_to_system_request=(
                admin_users_to_system.AddUserToSystemRequest(
                    system='system1',
                    provider='yandex',
                    provider_user_id='1134567890123456',
                    groups=['group_system_3'],
                )
            ),
            expected_response={
                'code': 'groups_not_found',
                'message': (
                    'Groups \'group_system_3\' not found'
                    ' in system \'system1\''
                ),
            },
        ),
    ],
    ids=admin_users_to_system.AddUserToSystemTestCase.get_id_for_pytest,
)
async def test_add_user_not_found(
        taxi_access_control, add_user_to_system_test_case,
):
    await admin_users_to_system.add_user_to_system(
        taxi_access_control,
        add_user_to_system_test_case.add_user_to_system_request,
        expected_status_code=404,
        expected_response_json=(
            add_user_to_system_test_case.expected_response
        ),
    )
