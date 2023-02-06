import pytest


@pytest.mark.pgsql('busy_drivers', files=['chain_busy_drivers.sql'])
async def test_chain_busy_driver_statistics(
        taxi_busy_drivers, testpoint, load_json,
):
    @testpoint('chain_busy_driver_statistics_collected')
    def statistics_collected(data):
        return data

    await taxi_busy_drivers.enable_testpoints()
    await taxi_busy_drivers.run_task('chain-busy-driver-statistics')

    data = await statistics_collected.wait_call()
    assert data == load_json('statistics.json')
