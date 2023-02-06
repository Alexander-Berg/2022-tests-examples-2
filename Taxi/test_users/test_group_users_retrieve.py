import pytest

SQL_FILES = ['add_systems.sql', 'add_groups.sql', 'add_many_users.sql']


SYSTEM_MAIN_GROUP_1 = {
    'id': 1,
    'name': 'system main group 1',
    'slug': 'system_main_group_1',
    'system': 'system_main',
}

SYSTEM_MAIN_GROUP_2 = {
    'id': 2,
    'parent_id': 1,
    'parent_slug': 'system_main_group_1',
    'name': 'system main group 2',
    'slug': 'system_main_group_2',
    'system': 'system_main',
}

USER_1 = {
    'groups': [SYSTEM_MAIN_GROUP_1],
    'provider': 'yandex',
    'provider_user_id': 'user1',
}

USER_2 = {
    'provider': 'yandex',
    'provider_user_id': 'user2',
    'groups': [SYSTEM_MAIN_GROUP_2],
}

USER_3 = {
    'provider': 'yandex',
    'provider_user_id': 'user3',
    'groups': [SYSTEM_MAIN_GROUP_2],
}

USER_5 = {
    'provider': 'yandex',
    'provider_user_id': 'user5',
    'groups': [SYSTEM_MAIN_GROUP_1, SYSTEM_MAIN_GROUP_2],
}

USER_6 = {
    'provider': 'yandex',
    'provider_user_id': 'user6',
    'groups': [SYSTEM_MAIN_GROUP_1, SYSTEM_MAIN_GROUP_2],
}

USER_8 = {
    'provider': 'yandex',
    'provider_user_id': 'user8',
    'groups': [SYSTEM_MAIN_GROUP_2],
}

USER_9 = {
    'provider': 'yandex',
    'provider_user_id': 'user9',
    'groups': [SYSTEM_MAIN_GROUP_2],
}

USER_10 = {
    'provider': 'yandex',
    'provider_user_id': 'user10',
    'groups': [SYSTEM_MAIN_GROUP_2],
}


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_users_all(
        group_users_retrieve_request, assert_response,
):
    response = await group_users_retrieve_request(
        {}, system='system_main', group='system_main_group_2',
    )
    assert_response(
        response,
        200,
        {'users': [USER_10, USER_2, USER_3, USER_5, USER_6, USER_8, USER_9]},
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_users_filters_name_like(
        group_users_retrieve_request, assert_response,
):
    response = await group_users_retrieve_request(
        {'filters': {'provider_user_id_part': 'ser1'}},
        system='system_main',
        group='system_main_group_2',
    )
    assert_response(response, 200, {'users': [USER_10]})


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_users_cursor(
        group_users_retrieve_request, assert_response,
):
    response = await group_users_retrieve_request(
        {'limit': 2}, system='system_main', group='system_main_group_2',
    )
    assert_response(
        response,
        200,
        {
            'cursor': {
                'greater_than_user': {
                    'provider': 'yandex',
                    'provider_user_id': 'user2',
                },
            },
            'users': [USER_10, USER_2],
        },
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_users_cursor_request(
        group_users_retrieve_request, assert_response,
):
    response = await group_users_retrieve_request(
        {
            'limit': 6,
            'cursor': {
                'greater_than_user': {
                    'provider': 'yandex',
                    'provider_user_id': 'user2',
                },
            },
        },
        system='system_main',
        group='system_main_group_2',
    )
    assert_response(
        response, 200, {'users': [USER_3, USER_5, USER_6, USER_8, USER_9]},
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_users_all_filters(
        group_users_retrieve_request, assert_response,
):
    response = await group_users_retrieve_request(
        {
            'limit': 4,
            'cursor': {
                'greater_than_user': {
                    'provider': 'yandex',
                    'provider_user_id': 'user2',
                },
            },
            'filters': {'provider_user_id_part': 'user3'},
        },
        system='system_main',
        group='system_main_group_2',
    )
    assert_response(response, 200, {'users': [USER_3]})


@pytest.mark.parametrize(
    ['system', 'group'],
    [
        ('no_system', 'system_main_group_2'),
        ('system_main', 'no_group'),
        ('system_main', 'system_main_group_3'),
    ],
)
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_users_empty(
        group_users_retrieve_request, assert_response, system, group,
):
    response = await group_users_retrieve_request(
        {}, system=system, group=group,
    )
    assert_response(response, 200, {'users': []})


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_users_by_ids(
        group_users_retrieve_request, assert_response,
):
    response = await group_users_retrieve_request(
        {
            'filters': {
                'provider': 'yandex',
                'provider_user_ids': ['user2', 'user8', 'user10', 'user100'],
            },
        },
        system='system_main',
        group='system_main_group_2',
    )
    assert_response(response, 200, {'users': [USER_10, USER_2, USER_8]})


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_users_by_groups(
        group_users_retrieve_request, assert_response,
):
    response = await group_users_retrieve_request(
        {
            'filters': {
                'provider': 'yandex',
                'provider_user_ids': ['user2', 'user8', 'user10', 'user5'],
                'groups': [
                    'system_main_group_2',
                    'system_main_group_1',
                    'system_main_group_3',
                ],
            },
        },
        system='system_main',
    )
    assert_response(
        response, 200, {'users': [USER_10, USER_2, USER_5, USER_8]},
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_retrieve_with_only_system(
        group_users_retrieve_request, assert_response,
):
    response = await group_users_retrieve_request(
        {'limit': 3}, system='system_main',
    )
    assert_response(
        response,
        200,
        {
            'cursor': {
                'greater_than_user': {
                    'provider': 'yandex',
                    'provider_user_id': 'user2',
                },
            },
            'users': [USER_1, USER_10, USER_2],
        },
    )
