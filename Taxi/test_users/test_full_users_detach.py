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
async def test_detach_full_one_from_system(
        full_users_detach,
        assert_response,
        assert_all_users_pg,
        assert_user_group_links_pg,
):
    response = await full_users_detach(
        system='system_main', groups=['system_main_group_1'],
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
                    'group_slug': 'system_main_group_1',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user4',
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
                    'group_slug': 'system_main_group_1',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user6',
                    },
                },
                {
                    'group_slug': 'system_main_group_1',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user7',
                    },
                },
            ],
        },
    )
    await assert_all_users_pg()
    await assert_user_group_links_pg(
        [(2, 2), (2, 3), (2, 5), (2, 6), (2, 8), (2, 9), (2, 10)],
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_detach_full_two_from_system(
        full_users_detach,
        assert_response,
        assert_all_users_pg,
        assert_user_group_links_pg,
):
    response = await full_users_detach(
        system='system_main', groups=['system_main_group_2'],
    )
    assert_response(
        response,
        200,
        {
            'detached_users': [
                {
                    'group_slug': 'system_main_group_2',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user10',
                    },
                },
                {
                    'group_slug': 'system_main_group_2',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user2',
                    },
                },
                {
                    'group_slug': 'system_main_group_2',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user3',
                    },
                },
                {
                    'group_slug': 'system_main_group_2',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user5',
                    },
                },
                {
                    'group_slug': 'system_main_group_2',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user6',
                    },
                },
                {
                    'group_slug': 'system_main_group_2',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user8',
                    },
                },
                {
                    'group_slug': 'system_main_group_2',
                    'user': {
                        'provider': 'yandex',
                        'provider_user_id': 'user9',
                    },
                },
            ],
        },
    )
    await assert_all_users_pg()
    await assert_user_group_links_pg([(1, 1), (1, 4), (1, 5), (1, 6), (1, 7)])


@pytest.mark.parametrize('groups', [[], ['not_existed']])
@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_detach_full_empty_from_system(
        full_users_detach,
        assert_response,
        assert_all_users_pg,
        assert_user_group_links_pg,
        groups,
):
    response = await full_users_detach(system='system_main', groups=groups)
    assert_response(response, 200, {'detached_users': []})
    await assert_all_users_pg()
    await assert_user_group_links_pg(
        [
            (1, 1),
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
            (2, 10),
        ],
    )
