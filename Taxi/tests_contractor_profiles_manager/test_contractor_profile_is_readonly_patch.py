import pytest

ENDPOINT_URL = '/driver-profiles/contractors/v1/is-readonly'


@pytest.mark.parametrize(
    'park_id, contractor_id, is_readonly, http_code',
    [
        ('parkid', 'profileid', True, 200),
        ('parkid', 'profileid', False, 200),
        ('parkid', 'profileid', False, 404),
    ],
)
async def test_update_is_readonly(
        taxi_contractor_profiles_manager,
        mock_driver_profiles,
        park_id,
        contractor_id,
        is_readonly,
        http_code,
):
    mock_driver_profiles.set_data(save_response_code=http_code)
    response = await taxi_contractor_profiles_manager.patch(
        ENDPOINT_URL,
        params={'park_id': park_id, 'contractor_profile_id': contractor_id},
        json={'is_readonly': is_readonly},
    )

    assert response.status == http_code
