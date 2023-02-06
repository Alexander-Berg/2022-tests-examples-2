# pylint: disable=redefined-outer-name
import pytest

from hiring_candidates.generated.cron import run_cron
from test_hiring_candidates import conftest


@pytest.mark.usefixtures('mock_fetch_drivers_rides_table')
async def test_fetch_drivers_rides(get_all_drivers_v2):
    await run_cron.main(
        ['hiring_candidates.crontasks.fetch_drivers_rides', '-t', '0'],
    )
    drivers = get_all_drivers_v2()
    assert len(drivers) == conftest.DRIVERS_COUNT
