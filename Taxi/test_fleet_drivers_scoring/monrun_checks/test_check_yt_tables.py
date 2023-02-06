import pytest

# pylint: disable=redefined-outer-name
from fleet_drivers_scoring.generated.cron import run_monrun


@pytest.mark.pgsql('fleet_drivers_scoring', files=['yt_tables.sql'])
@pytest.mark.now('2020-05-18T00:00')
async def test_ok():
    msg = await run_monrun.run(
        ['fleet_drivers_scoring.monrun_checks.cron_creates_yt_tables'],
    )
    assert msg == '0; Check done'


@pytest.mark.pgsql('fleet_drivers_scoring', files=['yt_tables.sql'])
@pytest.mark.now('2020-05-21T00:00')
async def test_crit():
    msg = await run_monrun.run(
        ['fleet_drivers_scoring.monrun_checks.cron_creates_yt_tables'],
    )
    assert (
        msg
        == """2; Critical outdated tables ['driving_style', 'high_speed_driving', 'orders', 'passenger_tags', 'quality_metrics', 'ratings']"""  # noqa: E501
    )
