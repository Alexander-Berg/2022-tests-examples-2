import pytest

from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers


@pytest.mark.experiments3(filename='exp3_scooters.json')
@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
async def test_scooters_availability(taxi_superapp_misc):
    response = await taxi_superapp_misc.post(
        consts.URL, helpers.build_payload(),
    )
    assert response.status_code == 200
    scooters_mode = helpers.build_mode(
        'scooters', available=True, deathflag=False,
    )
    scooters_available = scooters_mode in response.json()['modes']
    assert scooters_available
