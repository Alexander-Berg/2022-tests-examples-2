import pytest


@pytest.fixture
def taxi_scooter_accumulator_bot_mocks(
        scooter_accumulator_bot_scooter_accumulator_mocks,
        scooter_accumulator_bot_profile_mocks,
        scooter_accumulator_bot_personal_mocks,
        scooter_accumulator_bot_scooters_misc_mocks,
        scooter_accumulator_bot_scooter_backend_mocks,
        scooter_accumulator_bot_scooters_ops_repair_mocks,
        scooter_accumulator_bot_experiments_mocks,
):  # pylint: disable=C0103
    pass


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_scooter_accumulator_bot_mocks')
async def test_ping(taxi_scooter_accumulator_bot_web):
    response = await taxi_scooter_accumulator_bot_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
