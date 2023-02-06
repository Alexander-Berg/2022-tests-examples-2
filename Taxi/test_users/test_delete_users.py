import pytest

SQL_FILES = ['add_systems.sql', 'add_groups.sql', 'add_many_users.sql']


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_delete_bulk_users(
        delete_bulk_users, assert_response, assert_users_pg,
):
    response = await delete_bulk_users(
        users=[
            {'provider': 'yandex', 'provider_user_id': 'user10'},
            {'provider': 'yandex', 'provider_user_id': 'user1'},
        ],
    )
    assert_response(
        response,
        200,
        {
            'deleted_users': [
                {'provider': 'yandex', 'provider_user_id': 'user10'},
                {'provider': 'yandex', 'provider_user_id': 'user1'},
            ],
        },
    )
    await assert_users_pg(
        [('yandex', f'user{user_num}') for user_num in range(2, 10)],
    )


@pytest.mark.pgsql('access_control', files=SQL_FILES)
async def test_delete_bulk_not_existed_users(
        delete_bulk_users, assert_response, assert_users_pg,
):
    response = await delete_bulk_users(
        users=[
            {'provider': 'yandex', 'provider_user_id': 'user10'},
            {'provider': 'yandex', 'provider_user_id': 'user1'},
            {'provider': 'yandex', 'provider_user_id': 'lmao'},
            {'provider': 'yandex', 'provider_user_id': 'not_existed'},
        ],
    )
    assert_response(
        response,
        200,
        {
            'deleted_users': [
                {'provider': 'yandex', 'provider_user_id': 'user10'},
                {'provider': 'yandex', 'provider_user_id': 'user1'},
            ],
            'errors': [
                {
                    'code': 'not_existed_users',
                    'details': {
                        'users': [
                            {'provider': 'yandex', 'provider_user_id': 'lmao'},
                            {
                                'provider': 'yandex',
                                'provider_user_id': 'not_existed',
                            },
                        ],
                    },
                    'message': 'Next users are not exist',
                },
            ],
        },
    )
    await assert_users_pg(
        [('yandex', f'user{user_num}') for user_num in range(2, 10)],
    )
