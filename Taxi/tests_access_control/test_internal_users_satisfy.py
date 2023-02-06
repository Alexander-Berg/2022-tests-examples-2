import pytest


@pytest.mark.pgsql('access_control', files=['simple_test_data.sql'])
@pytest.mark.parametrize(
    ['request_body', 'expected_status_code', 'expected_response_json'],
    [
        pytest.param(
            {
                'system': 'group1',
                'conditions': {
                    'permissions': {
                        'any_of': [
                            {
                                'all_of': [
                                    {
                                        'type': 'permission',
                                        'name': 'permission1',
                                    },
                                ],
                            },
                        ],
                    },
                },
            },
            200,
            {
                'users': [
                    {'provider': 'yandex', 'provider_user_id': 'user1'},
                    {'provider': 'restapp', 'provider_user_id': 'user2'},
                ],
            },
            id='check_simple_permissions_include',
        ),
        pytest.param(
            {
                'system': 'group1',
                'provider': 'yandex',
                'provider_user_id': 'user1',
                'conditions': {
                    'permissions': {
                        'any_of': [
                            {
                                'all_of': [
                                    {
                                        'type': 'permission',
                                        'name': 'permission1',
                                    },
                                ],
                            },
                        ],
                    },
                },
            },
            200,
            {'users': [{'provider': 'yandex', 'provider_user_id': 'user1'}]},
            id='check_single_user_access',
        ),
        pytest.param(
            {
                'system': 'group1',
                'conditions': {
                    'permissions': {
                        'any_of': [
                            {
                                'all_of': [
                                    {
                                        'type': 'permission',
                                        'name': 'permission1',
                                    },
                                    {
                                        'type': 'permission',
                                        'name': 'non_existing_permission',
                                    },
                                ],
                            },
                        ],
                    },
                },
            },
            200,
            {'users': []},
            marks=[pytest.mark.xfail()],
            id='no_users_with_such_permission_now_not_supported_fix_it',
        ),
        pytest.param(
            {
                'system': 'group1',
                'conditions': {
                    'permissions': {
                        'any_of': [
                            {
                                'all_of': [
                                    {
                                        'type': 'permission',
                                        'name': 'permission1',
                                    },
                                ],
                            },
                            {
                                'all_of': [
                                    {
                                        'type': 'permission',
                                        'name': 'non_existing_permission',
                                    },
                                ],
                            },
                        ],
                    },
                },
            },
            200,
            {
                'users': [
                    {'provider': 'yandex', 'provider_user_id': 'user1'},
                    {'provider': 'restapp', 'provider_user_id': 'user2'},
                ],
            },
            id='users_with_at_least_one_of_provided_permissions',
        ),
    ],
)
async def test_internal_user_satisfy(
        taxi_access_control,
        request_body,
        expected_status_code,
        expected_response_json,
):
    response = await taxi_access_control.post(
        '/v1/internal/users/satisfy/', json=request_body,
    )
    response_json = response.json()

    assert response.status_code == expected_status_code, (
        response.status_code,
        expected_status_code,
        response_json,
    )
    assert expected_response_json == response_json, (
        expected_response_json,
        response_json,
    )
