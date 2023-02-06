import pytest

from tests_access_control.helpers import admin_groups


@pytest.mark.pgsql(
    'access_control', files=['add_systems.sql', 'add_groups.sql'],
)
@pytest.mark.parametrize(
    'system_slug, slug, expected',
    [
        (
            'system_main',
            'system_main_group_1',
            {
                'id': 1,
                'name': 'system main group 1',
                'slug': 'system_main_group_1',
                'system': 'system_main',
            },
        ),
        (
            'system_second',
            'system_second_group_2',
            {
                'id': 5,
                'name': 'system second group 2',
                'parent_id': 4,
                'parent_slug': 'system_second_group_1',
                'slug': 'system_second_group_2',
                'system': 'system_second',
            },
        ),
    ],
)
async def test_get_group_by_slug(
        taxi_access_control, slug, expected, system_slug,
):
    await admin_groups.get_group(
        taxi_access_control,
        {'group': slug, 'system': system_slug},
        expected_status_code=200,
        expected_response_json={'group': expected},
    )


@pytest.mark.pgsql(
    'access_control', files=['add_systems.sql', 'add_groups.sql'],
)
@pytest.mark.parametrize(
    'system_slug, slug',
    [
        pytest.param('system_main', 'not_a_group', id='group does not exist'),
        pytest.param(
            'not_a_system', 'system_main_group_1', id='system does not exist',
        ),
        pytest.param(
            'system_main',
            'system_second_group_2',
            id='group exists in other system',
        ),
    ],
)
async def test_group_not_found(taxi_access_control, system_slug, slug):
    error_msg = f'Group "{slug}" is not found in system "{system_slug}"'
    await admin_groups.get_group(
        taxi_access_control,
        {'group': slug, 'system': system_slug},
        expected_status_code=404,
        expected_response_json={
            'message': error_msg,
            'code': 'group_not_found',
        },
    )
