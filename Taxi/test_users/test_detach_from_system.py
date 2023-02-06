import pytest

SQL_FILES = ['add_systems.sql', 'add_groups.sql', 'add_many_users.sql']


@pytest.fixture(name='assert_all_users_pg')
def _assert_all_users_pg(assert_users_pg):
    async def _wrapper():
        expected = [('yandex', 'user1'), ('yandex', 'user10')]
        expected += [
            ('yandex', f'user{user_num}') for user_num in range(2, 10)
        ]
        await assert_users_pg(expected)

    return _wrapper


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_detach_bulk_from_system(
        detach_bulk_groups_users,
        assert_response,
        assert_all_users_pg,
        assert_user_group_links_pg,
):
    response = await detach_bulk_groups_users(
        system='system_main',
        users=[
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user10'},
                'group_slug': 'system_main_group_1',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user1'},
                'group_slug': 'system_main_group_1',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user1'},
                'group_slug': 'not_existed',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user10'},
                'group_slug': 'system_main_group_2',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user2'},
                'group_slug': 'system_second_group_1',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user5'},
                'group_slug': 'system_main_group_1',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user5'},
                'group_slug': 'system_main_group_2',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user20'},
                'group_slug': 'system_second_group_1',
            },
        ],
    )
    assert_response(
        response,
        200,
        {
            'detached_users': [
                {
                    'group_slug': 'system_main_group_1',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user1',
                    },
                },
                {
                    'group_slug': 'system_main_group_2',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user10',
                    },
                },
                {
                    'group_slug': 'system_main_group_1',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user5',
                    },
                },
                {
                    'group_slug': 'system_main_group_2',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user5',
                    },
                },
            ],
            'errors': [
                {
                    'code': 'not_existed_links',
                    'details': {
                        'groups_users_links': [
                            {
                                'group_slug': 'system_main_group_1',
                                'user': {
                                    'provider': 'yandex',
                                    'provider_user_id': 'user10',
                                },
                            },
                            {
                                'group_slug': 'not_existed',
                                'user': {
                                    'provider': 'yandex',
                                    'provider_user_id': 'user1',
                                },
                            },
                            {
                                'group_slug': 'system_second_group_1',
                                'user': {
                                    'provider': 'yandex',
                                    'provider_user_id': 'user2',
                                },
                            },
                            {
                                'group_slug': 'system_second_group_1',
                                'user': {
                                    'provider': 'yandex',
                                    'provider_user_id': 'user20',
                                },
                            },
                        ],
                    },
                    'message': 'Next links are not exist',
                },
            ],
        },
    )
    await assert_all_users_pg()
    await assert_user_group_links_pg(
        [(2, 2), (2, 3), (1, 4), (1, 6), (2, 6), (1, 7), (2, 8), (2, 9)],
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_detach_bulk_from_system_double(
        detach_bulk_groups_users,
        assert_response,
        assert_all_users_pg,
        assert_user_group_links_pg,
):
    response = await detach_bulk_groups_users(
        system='system_main',
        users=[
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user10'},
                'group_slug': 'system_main_group_1',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user10'},
                'group_slug': 'system_main_group_2',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user1'},
                'group_slug': 'system_main_group_1',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user1'},
                'group_slug': 'system_second_group_1',
            },
            {
                'user': {'provider': 'yandex', 'provider_user_id': 'user1'},
                'group_slug': 'system_main_group_1',
            },
        ],
    )
    assert_response(
        response,
        200,
        {
            'detached_users': [
                {
                    'group_slug': 'system_main_group_1',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user1',
                    },
                },
                {
                    'group_slug': 'system_main_group_2',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user10',
                    },
                },
            ],
            'errors': [
                {
                    'code': 'not_existed_links',
                    'details': {
                        'groups_users_links': [
                            {
                                'group_slug': 'system_main_group_1',
                                'user': {
                                    'provider': 'yandex',
                                    'provider_user_id': 'user10',
                                },
                            },
                            {
                                'group_slug': 'system_second_group_1',
                                'user': {
                                    'provider': 'yandex',
                                    'provider_user_id': 'user1',
                                },
                            },
                        ],
                    },
                    'message': 'Next links are not exist',
                },
            ],
        },
    )
    await assert_all_users_pg()
    await assert_user_group_links_pg(
        [
            (2, 2),
            (2, 3),
            (1, 4),
            (1, 5),
            (2, 5),
            (1, 6),
            (2, 6),
            (1, 7),
            (2, 8),
            (2, 9),
        ],
    )
