import pytest

from tests_access_control.helpers import admin_system


async def test_create_system_success(taxi_access_control):
    await admin_system.create_system(
        taxi_access_control,
        'group1',
        expected_status_code=200,
        expected_response_json={'system': {'id': 1, 'slug': 'group1'}},
    )


@pytest.mark.pgsql('access_control', files=['system/group1.sql'])
async def test_create_system_conflict(taxi_access_control):
    await admin_system.create_system(
        taxi_access_control,
        'group1',
        expected_status_code=409,
        expected_response_json={
            'code': 'already_exist',
            'message': 'System already exist',
        },
    )
