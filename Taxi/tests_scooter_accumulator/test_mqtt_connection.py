import pytest

PERIODIC_TASK = 'keep_mqtt_connection'


@pytest.mark.suspend_periodic_tasks(PERIODIC_TASK)
async def test_keep_mqtt_connection(taxi_scooter_accumulator):
    await taxi_scooter_accumulator.run_periodic_task(PERIODIC_TASK)
