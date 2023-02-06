import pytest

from tests_access_control.helpers import admin_system


@pytest.mark.pgsql(
    'access_control',
    files=[
        'system/group1.sql',
        'system/group2.sql',
        'system/xyz.sql',
        'system/group3.sql',
    ],
)
async def test_retrieve_system_all(taxi_access_control):
    await admin_system.retrieve_system(
        taxi_access_control,
        {},
        expected_status_code=200,
        expected_response_json={
            'systems': [
                {'id': 1, 'slug': 'group1'},
                {'id': 2, 'slug': 'group2'},
                {'id': 4, 'slug': 'group3'},
                {'id': 3, 'slug': 'xyz'},
            ],
        },
    )


@pytest.mark.pgsql(
    'access_control',
    files=[
        'system/group1.sql',
        'system/group2.sql',
        'system/xyz.sql',
        'system/group3.sql',
    ],
)
async def test_retrieve_system_filters_slug_like(taxi_access_control):
    await admin_system.retrieve_system(
        taxi_access_control,
        {'filters': {'slug': 'gro'}},
        expected_status_code=200,
        expected_response_json={
            'systems': [
                {'id': 1, 'slug': 'group1'},
                {'id': 2, 'slug': 'group2'},
                {'id': 4, 'slug': 'group3'},
            ],
        },
    )


@pytest.mark.pgsql(
    'access_control',
    files=[
        'system/group1.sql',
        'system/group2.sql',
        'system/xyz.sql',
        'system/group3.sql',
    ],
)
async def test_retrieve_system_filters_slug_exact(taxi_access_control):
    await admin_system.retrieve_system(
        taxi_access_control,
        {'filters': {'slug': 'group1'}},
        expected_status_code=200,
        expected_response_json={'systems': [{'id': 1, 'slug': 'group1'}]},
    )


@pytest.mark.pgsql(
    'access_control',
    files=[
        'system/group1.sql',
        'system/group2.sql',
        'system/xyz.sql',
        'system/group3.sql',
    ],
)
async def test_retrieve_system_pagination_limit(taxi_access_control):
    await admin_system.retrieve_system(
        taxi_access_control,
        {'limit': 1},
        expected_status_code=200,
        expected_response_json={
            'systems': [{'id': 1, 'slug': 'group1'}],
            'cursor': {'greater_than_slug': 'group1'},
        },
    )


@pytest.mark.pgsql(
    'access_control',
    files=[
        'system/group1.sql',
        'system/group2.sql',
        'system/xyz.sql',
        'system/group3.sql',
    ],
)
async def test_retrieve_system_pagination_limit_offset(taxi_access_control):
    await admin_system.retrieve_system(
        taxi_access_control,
        {'cursor': {'greater_than_slug': 'group2'}, 'limit': 2},
        expected_status_code=200,
        expected_response_json={
            'systems': [{'id': 4, 'slug': 'group3'}, {'id': 3, 'slug': 'xyz'}],
            'cursor': {'greater_than_slug': 'xyz'},
        },
    )


@pytest.mark.pgsql(
    'access_control',
    files=[
        'system/group1.sql',
        'system/group2.sql',
        'system/xyz.sql',
        'system/group3.sql',
    ],
)
async def test_retrieve_system_pagination_limit_offset_filters(
        taxi_access_control,
):
    await admin_system.retrieve_system(
        taxi_access_control,
        {
            'filters': {'slug': 'group'},
            'limit': 2,
            'cursor': {'greater_than_slug': 'group2'},
        },
        expected_status_code=200,
        expected_response_json={'systems': [{'id': 4, 'slug': 'group3'}]},
    )
