import pytest

from tests_access_control.helpers import admin_groups


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_retrieve_groups_all(taxi_access_control):
    await admin_groups.retrieve_groups(
        taxi_access_control,
        {},
        {'system': 'system1'},
        expected_status_code=200,
        expected_response_json={
            'groups': [
                {
                    'id': 1,
                    'name': 'agroup1',
                    'slug': 'agroup1',
                    'system': 'system1',
                },
                {
                    'id': 3,
                    'parent_id': 1,
                    'parent_slug': 'agroup1',
                    'name': 'bgroup12',
                    'slug': 'bgroup12',
                    'system': 'system1',
                },
                {
                    'id': 5,
                    'name': 'qgroup3',
                    'slug': 'qgroup3',
                    'system': 'system1',
                },
                {
                    'id': 4,
                    'name': 'xgroup2',
                    'slug': 'xgroup2',
                    'system': 'system1',
                },
                {
                    'id': 2,
                    'parent_id': 1,
                    'parent_slug': 'agroup1',
                    'name': 'zgroup11',
                    'slug': 'zgroup11',
                    'system': 'system1',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_retrieve_groups_filters_name_like(taxi_access_control):
    await admin_groups.retrieve_groups(
        taxi_access_control,
        {'filters': {'name': 'group1'}},
        {'system': 'system1'},
        expected_status_code=200,
        expected_response_json={
            'groups': [
                {
                    'id': 1,
                    'name': 'agroup1',
                    'slug': 'agroup1',
                    'system': 'system1',
                },
                {
                    'id': 3,
                    'parent_id': 1,
                    'parent_slug': 'agroup1',
                    'name': 'bgroup12',
                    'slug': 'bgroup12',
                    'system': 'system1',
                },
                {
                    'id': 2,
                    'parent_id': 1,
                    'parent_slug': 'agroup1',
                    'name': 'zgroup11',
                    'slug': 'zgroup11',
                    'system': 'system1',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_retrieve_groups_filters_slug_like(taxi_access_control):
    await admin_groups.retrieve_groups(
        taxi_access_control,
        {'filters': {'slug': 'group1'}},
        {'system': 'system1'},
        expected_status_code=200,
        expected_response_json={
            'groups': [
                {
                    'id': 1,
                    'name': 'agroup1',
                    'slug': 'agroup1',
                    'system': 'system1',
                },
                {
                    'id': 3,
                    'parent_id': 1,
                    'parent_slug': 'agroup1',
                    'name': 'bgroup12',
                    'slug': 'bgroup12',
                    'system': 'system1',
                },
                {
                    'id': 2,
                    'parent_id': 1,
                    'parent_slug': 'agroup1',
                    'name': 'zgroup11',
                    'slug': 'zgroup11',
                    'system': 'system1',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_retrieve_groups_filters_name_exact(taxi_access_control):
    await admin_groups.retrieve_groups(
        taxi_access_control,
        {'filters': {'name': 'group2'}},
        {'system': 'system1'},
        expected_status_code=200,
        expected_response_json={
            'groups': [
                {
                    'id': 4,
                    'name': 'xgroup2',
                    'slug': 'xgroup2',
                    'system': 'system1',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_retrieve_groups_pagination_limit(taxi_access_control):
    await admin_groups.retrieve_groups(
        taxi_access_control,
        {'limit': 1},
        {'system': 'system1'},
        expected_status_code=200,
        expected_response_json={
            'groups': [
                {
                    'id': 1,
                    'name': 'agroup1',
                    'slug': 'agroup1',
                    'system': 'system1',
                },
            ],
            'cursor': {'greater_than_slug': 'agroup1'},
        },
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_retrieve_groups_pagination_limit_offset(taxi_access_control):
    await admin_groups.retrieve_groups(
        taxi_access_control,
        {'cursor': {'greater_than_slug': 'bgroup12'}, 'limit': 2},
        {'system': 'system1'},
        expected_status_code=200,
        expected_response_json={
            'cursor': {'greater_than_slug': 'xgroup2'},
            'groups': [
                {
                    'id': 5,
                    'name': 'qgroup3',
                    'slug': 'qgroup3',
                    'system': 'system1',
                },
                {
                    'id': 4,
                    'name': 'xgroup2',
                    'slug': 'xgroup2',
                    'system': 'system1',
                },
            ],
        },
    )


@pytest.mark.pgsql('access_control', files=['test_data.sql'])
async def test_retrieve_groups_pagination_limit_offset_filters(
        taxi_access_control,
):
    await admin_groups.retrieve_groups(
        taxi_access_control,
        {
            'filters': {'name': 'group1'},
            'cursor': {'greater_than_slug': 'bgroup12'},
            'limit': 2,
        },
        {'system': 'system1'},
        expected_status_code=200,
        expected_response_json={
            'groups': [
                {
                    'id': 2,
                    'parent_id': 1,
                    'parent_slug': 'agroup1',
                    'name': 'zgroup11',
                    'slug': 'zgroup11',
                    'system': 'system1',
                },
            ],
        },
    )
