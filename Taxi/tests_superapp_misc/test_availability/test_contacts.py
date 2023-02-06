import pytest

from tests_superapp_misc.test_availability import consts
from tests_superapp_misc.test_availability import helpers


@pytest.mark.experiments3(filename='exp3_whereami.json')
@pytest.mark.experiments3(filename='exp3_superapp_availability.json')
async def test_scooters_availability(taxi_superapp_misc):
    response = await taxi_superapp_misc.post(
        consts.URL, helpers.build_payload(),
    )
    assert response.status_code == 200
    contacts_mode = helpers.build_mode('contacts', available=True)
    assert contacts_mode in response.json()['modes']
