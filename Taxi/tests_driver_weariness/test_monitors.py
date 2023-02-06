import datetime

import pytest

from tests_driver_weariness import const
from tests_driver_weariness import weariness_tools

_BEGIN = datetime.datetime(2020, 1, 1)
_PLUS1 = _BEGIN + datetime.timedelta(hours=1)
_PLUS4 = _BEGIN + datetime.timedelta(hours=4)
_PLUS6 = _BEGIN + datetime.timedelta(hours=6)
_PLUS7 = _BEGIN + datetime.timedelta(hours=7)
_PLUS10 = _BEGIN + datetime.timedelta(hours=10)


_DRIVER = 'park1_driverSS1'


@pytest.mark.now(_PLUS10.isoformat())
@pytest.mark.unique_drivers(stream=const.DEFAULT_UNIQUE_DRIVERS)
@pytest.mark.parametrize(
    'expected_result',
    [
        pytest.param(
            {
                'all_not_tired': 0,
                'hours_exceed': 1,
                'no_long_rest': 0,
                'not_tired': 0,
            },
            marks=pytest.mark.pgsql(
                'drivers_status_ranges',
                queries=[
                    weariness_tools.insert_range(_DRIVER, _BEGIN, _PLUS4),
                ],
            ),
        ),
        pytest.param(
            {
                'all_not_tired': 0,
                'hours_exceed': 0,
                'no_long_rest': 1,
                'not_tired': 0,
            },
            marks=pytest.mark.pgsql(
                'drivers_status_ranges',
                queries=[
                    weariness_tools.insert_range(_DRIVER, _BEGIN, _PLUS1),
                    weariness_tools.insert_range(_DRIVER, _PLUS6, _PLUS7),
                ],
            ),
        ),
        pytest.param(
            {
                'all_not_tired': 1,
                'hours_exceed': 0,
                'no_long_rest': 0,
                'not_tired': 1,
            },
            marks=pytest.mark.pgsql(
                'drivers_status_ranges',
                queries=[
                    weariness_tools.insert_range(_DRIVER, _BEGIN, _PLUS1),
                ],
            ),
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_config.json')
async def test_monitors(
        taxi_driver_weariness,
        taxi_driver_weariness_monitor,
        expected_result,
        experiments3,
):
    weariness_tools.add_experiment(
        experiments3, weariness_tools.WearinessConfig(1000000, 6 * 60, 3 * 60),
    )
    await taxi_driver_weariness.invalidate_caches()

    metrics = await taxi_driver_weariness_monitor.get_metrics()
    assert metrics['drivers_status'] == expected_result
