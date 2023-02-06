import pytest


ENDPOINT = '/service/profile-view/v1/banners/permits'


@pytest.mark.config(
    CONTRACTOR_BANNERS_SUPPORTED_PERMITS=['role1', 'role2', 'role3'],
)
async def test_banners_permits(taxi_driver_profile_view):
    response = await taxi_driver_profile_view.get(ENDPOINT)

    assert response.status_code == 200
    assert response.json() == {
        'supported_permits': ['role1', 'role2', 'role3'],
    }
