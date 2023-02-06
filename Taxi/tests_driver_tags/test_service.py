import pytest


# Every service must have this handler
@pytest.mark.unique_drivers(
    stream={
        'licenses_by_unique_drivers': {'last_revision': '0_0', 'items': []},
        'license_by_driver_profile': {'last_revision': '0_0', 'items': []},
    },
)
@pytest.mark.servicetest
async def test_ping(taxi_driver_tags):
    response = await taxi_driver_tags.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''
