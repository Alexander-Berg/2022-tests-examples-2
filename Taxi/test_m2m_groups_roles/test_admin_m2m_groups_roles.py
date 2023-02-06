import pytest

from tests_access_control.helpers import admin_groups_roles


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
@pytest.mark.parametrize(
    'test_case',
    [
        admin_groups_roles.BulkGroupsRolesTestCase(
            id_for_pytest='empty query',
            request_json={'groups_roles': []},
            expected_status_code=200,
            expected_response={
                'added_groups_roles': [],
                'existing_groups_roles': [],
                'not_found_groups_roles': [],
            },
        ),
        admin_groups_roles.BulkGroupsRolesTestCase(
            id_for_pytest='all cases of groups_roles',
            request_json={
                'groups_roles': [
                    {
                        'role': 'main_role',
                        'group': 'group1',
                        'system': 'system_1',
                    },
                    {
                        'role': 'other_role',
                        'group': 'group1',
                        'system': 'system_1',
                    },
                    {
                        'role': 'existed_role',
                        'group': 'group1',
                        'system': 'system_1',
                    },
                    {
                        'role': 'main_role',
                        'group': 'group2',
                        'system': 'system_1',
                    },
                    {
                        'role': 'main_role',
                        'group': 'group1',
                        'system': 'system_1',
                    },
                    {
                        'role': 'other_role',
                        'group': 'group1',
                        'system': 'system_1',
                    },
                ],
            },
            expected_status_code=200,
            expected_response={
                'added_groups_roles': [
                    {
                        'role': 'main_role',
                        'group': 'group1',
                        'system': 'system_1',
                    },
                    {
                        'role': 'other_role',
                        'group': 'group1',
                        'system': 'system_1',
                    },
                ],
                'existing_groups_roles': [
                    {
                        'role': 'existed_role',
                        'group': 'group1',
                        'system': 'system_1',
                    },
                    {
                        'role': 'main_role',
                        'group': 'group1',
                        'system': 'system_1',
                    },
                    {
                        'role': 'other_role',
                        'group': 'group1',
                        'system': 'system_1',
                    },
                ],
                'not_found_groups_roles': [
                    {
                        'role': 'main_role',
                        'group': 'group2',
                        'system': 'system_1',
                    },
                ],
            },
        ),
    ],
    ids=admin_groups_roles.BulkGroupsRolesTestCase.get_id_for_pytest,
)
async def test_bulk_create_groups_roles(taxi_access_control, test_case):
    await admin_groups_roles.bulk_create_groups_roles(
        taxi_access_control,
        test_case.request_json,
        expected_status_code=test_case.expected_status_code,
        expected_response_json=test_case.expected_response,
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
@pytest.mark.parametrize(
    'test_case',
    [
        admin_groups_roles.BulkGroupsRolesTestCase(
            id_for_pytest='delete some groups-roles links',
            request_json={
                'groups_roles_slugs': [
                    {'group_slug': 'group2', 'role_slug': 'role1'},
                    {'group_slug': 'group2', 'role_slug': 'role2'},
                    {'group_slug': 'group2', 'role_slug': 'role3'},
                    {'group_slug': 'group3', 'role_slug': 'role1'},
                    {'group_slug': 'group1', 'role_slug': 'role8'},
                    {'group_slug': 'group8', 'role_slug': 'main_role'},
                    {'group_slug': 'group4', 'role_slug': 'role1'},
                    {'group_slug': 'group1', 'role_slug': 'existed_role'},
                ],
            },
            params={'system': 'system5'},
            expected_status_code=200,
            expected_response={
                'deleted_groups_roles': [
                    {'role_slug': 'role1', 'group_slug': 'group2'},
                    {'role_slug': 'role1', 'group_slug': 'group3'},
                    {'role_slug': 'role2', 'group_slug': 'group2'},
                    {'role_slug': 'role3', 'group_slug': 'group2'},
                ],
                'not_found_groups_roles': [
                    {'role_slug': 'existed_role', 'group_slug': 'group1'},
                    {'role_slug': 'main_role', 'group_slug': 'group8'},
                    {'role_slug': 'role1', 'group_slug': 'group4'},
                    {'role_slug': 'role8', 'group_slug': 'group1'},
                ],
            },
        ),
    ],
    ids=admin_groups_roles.BulkGroupsRolesTestCase.get_id_for_pytest,
)
async def test_bulk_delete_groups_roles(taxi_access_control, test_case):
    await admin_groups_roles.bulk_delete_groups_roles(
        taxi_access_control,
        test_case.request_json,
        test_case.params,
        expected_status_code=test_case.expected_status_code,
        expected_response_json=test_case.expected_response,
    )
