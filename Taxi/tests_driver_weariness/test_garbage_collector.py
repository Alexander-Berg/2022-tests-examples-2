import pytest

from tests_driver_weariness import const
from tests_driver_weariness import weariness_tools


@pytest.mark.now('2021-02-20T21:50:00+00:00')
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.pgsql(
    'drivers_status_ranges',
    files=['pg_new_working_ranges.sql', 'pg_whitelist_items.sql'],
)
@pytest.mark.experiments3(filename='exp3_config.json')
@pytest.mark.config(
    DRIVER_WEARINESS_GARBAGE_COLLECTOR_SETTINGS={
        '__default__': {'enabled': False},
        'cleanup_working_ranges': {'enabled': True},
        'cleanup_white_list': {'enabled': True},
    },
)
async def test_garbage_collector(taxi_driver_weariness, pgsql):
    await weariness_tools.activate_task(
        taxi_driver_weariness, 'garbage-collector',
    )

    ranges = weariness_tools.select_working_ranges(
        pgsql['drivers_status_ranges'],
    )
    assert ranges == {
        'park1_driverSS1': {
            '2021-02-19T15:51:00+0300': '2021-02-19T15:53:00+0300',
            '2021-02-19T17:01:00+0300': '2021-02-19T18:50:00+0300',
        },
    }

    whitelist = weariness_tools.select_whitelist(
        pgsql['drivers_status_ranges'],
    )
    assert whitelist == [
        {
            'unique_driver_id': 'udid2',
            'author': 'petrov',
            'ttl': '2023-01-21T18:45:00+0000',
        },
        {
            'unique_driver_id': 'udid3',
            'author': 'sidorov',
            'ttl': '2022-01-21T18:45:00+0000',
        },
    ]
