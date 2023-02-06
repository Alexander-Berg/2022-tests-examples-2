import pytest


ENDPOINT_URL = 'v1/work-modes/driver-fix/park-commission-rate'


@pytest.mark.config(TVM_ENABLED=False)
@pytest.mark.parametrize(
    'park_id, driver_profile_id,expected_rate',
    [
        ('park1', 'driver1', '0.0011'),
        ('park1', 'driver2', '1.0000'),
        ('park1', 'driver3', '0.0000'),
        ('park1', 'driver4', '0.0000'),
        ('park1', 'driver5', '0.0000'),
        ('park3', 'driver6', '0.0000'),
    ],
)
async def test_ok(
        taxi_driver_work_modes,
        driver_profiles,
        driver_work_rules,
        park_id,
        driver_profile_id,
        expected_rate,
):

    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={
            'park_id': park_id,
            'driver_profile_id': driver_profile_id,
            'at': '2019-01-01T00:00:00+0000',
        },
    )

    assert response.status_code == 200, response.text
    assert response.json() == {'park_commission_rate': expected_rate}


async def test_driver_profiles_empty(taxi_driver_work_modes, mockserver):
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_callback(request):
        return {'profiles': []}

    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={
            'park_id': 'park1',
            'driver_profile_id': 'driver1',
            'at': '2019-01-01T00:00:00+0000',
        },
    )

    assert mock_callback.times_called == 1
    assert response.status_code == 500, response.text


@pytest.mark.parametrize(
    'park_id,driver_profile_id',
    [('not_existed_park_id', 'driver1'), ('park1', 'not_existed_driver_id')],
)
async def test_not_found(
        taxi_driver_work_modes,
        driver_profiles,
        driver_work_rules,
        park_id,
        driver_profile_id,
):

    response = await taxi_driver_work_modes.get(
        ENDPOINT_URL,
        params={
            'park_id': park_id,
            'driver_profile_id': driver_profile_id,
            'at': '2019-01-01T00:00:00+0000',
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'driver_not_found',
        'message': 'Driver not found',
    }
