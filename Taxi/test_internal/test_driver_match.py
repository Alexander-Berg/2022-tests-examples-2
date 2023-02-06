import pytest


@pytest.mark.parametrize(
    'park_id,driver_profile_id,selfreg_id',
    [
        ('park_id1', 'driver_profile_id1', '5a7581722016667706734a34'),
        ('park_id1', 'driver_profile_id_not_exist', None),
        ('park_id_not_exist', 'driver_profile_id1', None),
        ('park_id_not_exist', 'driver_profile_id_not_exist', None),
    ],
)
async def test_validate_token(
        taxi_selfreg, park_id, driver_profile_id, selfreg_id,
):
    data = {'park_id': park_id, 'driver_profile_id': driver_profile_id}
    response = await taxi_selfreg.post(
        '/internal/selfreg/v1/driver/match',
        json=data,
        headers={'Content-Type': 'application/json'},
    )
    if selfreg_id is None:
        assert response.status == 404
        return
    assert response.status == 200
    response_json = await response.json()
    assert response_json['selfreg_id'] == selfreg_id
