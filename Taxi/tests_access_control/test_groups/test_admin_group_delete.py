import pytest


@pytest.mark.pgsql(
    'access_control',
    files=[
        'add_systems.sql',
        'add_groups.sql',
        'add_users.sql',
        'add_roles.sql',
        'add_link_groups_roles.sql',
        'add_link_groups_users.sql',
    ],
)
async def test_delete_group_common(groups_delete_request, assert_response):
    expected = {
        'id': 1,
        'name': 'system main group 1',
        'parent_slug': 'system_main_group_1',
        'slug': 'system_main_group_1',
        'system': 'system main group 1',
    }
    expected_response_json = {'group': expected}
    response = await groups_delete_request(
        system='system_main', group='system_main_group_1',
    )
    assert_response(response, 200, expected_response_json)


@pytest.mark.pgsql(
    'access_control',
    files=[
        'add_systems.sql',
        'add_groups.sql',
        'add_users.sql',
        'add_roles.sql',
        'add_link_groups_roles.sql',
        'add_link_groups_users.sql',
    ],
)
@pytest.mark.parametrize(
    'system, group, expected',
    [
        (
            'system_main',
            'system_main_group_2',
            {
                'message': (
                    'Group "system_main_group_2" can not be deleted! '
                    'You should detach the roles, users, '
                    'and inherited groups.'
                ),
                'code': 'used_group',
            },
        ),
        (
            'system_main',
            'system_main_group_3',
            {
                'message': (
                    'Group "system_main_group_3" can not be deleted! '
                    'You should detach the roles, users, '
                    'and inherited groups.'
                ),
                'code': 'used_group',
            },
        ),
        (
            'system_second',
            'system_second_group_1',
            {
                'message': (
                    'Group "system_second_group_1" can not be deleted! '
                    'You should detach the roles, users, '
                    'and inherited groups.'
                ),
                'code': 'used_group',
            },
        ),
    ],
)
async def test_delete_group_error_409(
        groups_delete_request, assert_response, expected, system, group,
):
    response = await groups_delete_request(system=system, group=group)
    assert_response(response, 409, expected)


@pytest.mark.pgsql(
    'access_control', files=['add_systems.sql', 'add_groups.sql'],
)
@pytest.mark.parametrize(
    'system, group, expected',
    [
        (
            'system_second',
            'system_main_group_1',
            {
                'message': (
                    'Group "system_main_group_1" is not found '
                    'in system "system_second"'
                ),
                'code': 'group_not_found',
            },
        ),
    ],
)
async def test_delete_group_error_404(
        groups_delete_request, assert_response, expected, system, group,
):
    response = await groups_delete_request(system=system, group=group)
    assert_response(response, 404, expected)
