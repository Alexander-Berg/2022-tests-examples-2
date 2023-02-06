import pytest


@pytest.mark.pgsql(
    'access_control', files=['add_systems.sql', 'add_groups.sql'],
)
@pytest.mark.parametrize(
    'params, data, expected',
    [
        (
            {'system': 'system_second', 'group': 'system_second_group_2'},
            {'name': 'updated_group'},
            {
                'id': 5,
                'name': 'updated_group',
                'parent_id': 4,
                'parent_slug': 'system_second_group_1',
                'slug': 'system_second_group_2',
                'system': 'system_second',
            },
        ),
        (
            {'system': 'system_main', 'group': 'system_main_group_1'},
            {'name': 'updated_group'},
            {
                'id': 1,
                'name': 'updated_group',
                'slug': 'system_main_group_1',
                'system': 'system_main',
            },
        ),
    ],
)
async def test_update_group_common(
        groups_update_request, assert_response, expected, data, params,
):
    expected_response_json = {'group': expected}
    response = await groups_update_request(body=data, params=params)
    assert_response(response, 200, expected_response_json)


@pytest.mark.pgsql(
    'access_control', files=['add_systems.sql', 'add_groups.sql'],
)
@pytest.mark.parametrize(
    'params, data, expected',
    [
        (
            {'system': 'system_second', 'group': 'group_404'},
            {'name': 'updated_group'},
            {
                'message': (
                    'group group_404 is not found in system system_second'
                ),
                'code': 'group_not_found',
            },
        ),
    ],
)
async def test_update_group_error_404(
        groups_update_request, assert_response, expected, data, params,
):
    response = await groups_update_request(body=data, params=params)
    assert_response(response, 404, expected)


@pytest.mark.pgsql(
    'access_control', files=['add_systems.sql', 'add_groups.sql'],
)
@pytest.mark.parametrize(
    'params, data, expected',
    [
        (
            {'system': 'system_second', 'group': 'system_second_group_2'},
            {},
            {'message': 'There is nothing to update', 'code': 'empty_body'},
        ),
    ],
)
async def test_update_group_error_400(
        groups_update_request, assert_response, expected, data, params,
):
    response = await groups_update_request(body=data, params=params)
    assert_response(response, 400, expected)
