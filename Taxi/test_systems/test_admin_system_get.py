import pytest

from tests_access_control.helpers import admin_system


@pytest.mark.pgsql('access_control', files=['add_systems.sql'])
@pytest.mark.parametrize(
    'slug, expected_id', [('system_main', 1), ('system_second', 2)],
)
async def test_get_system_by_slug(taxi_access_control, slug, expected_id):
    await admin_system.get_system(
        taxi_access_control,
        {'system': slug},
        expected_status_code=200,
        expected_response_json={'system': {'id': expected_id, 'slug': slug}},
    )


@pytest.mark.pgsql('access_control', files=['add_systems.sql'])
async def test_system_not_found(taxi_access_control):
    await admin_system.get_system(
        taxi_access_control,
        {'system': 'not a system at all'},
        expected_status_code=404,
        expected_response_json={
            'message': 'System "not a system at all" is not found',
            'code': 'system_not_found',
        },
    )
