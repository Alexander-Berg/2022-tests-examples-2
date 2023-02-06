import pytest

from tests_access_control.helpers import admin_groups


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_create_groups_success(taxi_access_control):
    await admin_groups.create_group(
        taxi_access_control,
        'system1',
        'Группа 2',
        'group2',
        parent_group_slug='group1',
        expected_status_code=200,
        expected_response_json={
            'group': {
                'id': 2,
                'parent_id': 1,
                'name': 'Группа 2',
                'slug': 'group2',
                'parent_slug': 'group1',
                'system': 'system1',
            },
        },
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_create_groups_conflict(taxi_access_control):
    await admin_groups.create_group(
        taxi_access_control,
        'system1',
        'Группа 1',
        'group1',
        parent_group_slug=None,
        expected_status_code=409,
        expected_response_json={
            'code': 'already_exist',
            'message': 'Group already exist',
        },
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_create_groups_failed_system_not_found(taxi_access_control):
    await admin_groups.create_group(
        taxi_access_control,
        'not_found',
        'Группа 1',
        'group1',
        parent_group_slug=None,
        expected_status_code=404,
        expected_response_json={
            'message': 'system not_found not found',
            'code': 'system_not_found',
        },
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_create_groups_failed_parent_not_found(taxi_access_control):
    await admin_groups.create_group(
        taxi_access_control,
        'system1',
        'Группа 1',
        'group1',
        parent_group_slug='not_found',
        expected_status_code=404,
        expected_response_json={
            'message': 'Parent group not_found not found',
            'code': 'parent_group_not_found',
        },
    )
