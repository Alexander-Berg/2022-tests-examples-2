# flake8: noqa F401, IS001
# pylint: disable=C5521
import json

import pytest

from tests_atlas_drivers import driver_info
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import drivers


_SAMPLE_DRIVERS = drivers.generate_drivers(
    32,
    airports=(lambda i: None if i % 2 == 1 else driver_info.Airports(i / 2)),
)


@pytest.mark.config(
    DISPATCH_AIRPORT_ZONES={
        'moscow': {
            'airport_title_key': 'moscow_airport_key',
            'enabled': True,
            'main_area': 'moscow_main',
            'notification_area': 'moscow_notification',
            'old_mode_enabled': False,
            'tariff_home_zone': 'moscow_home',
            'update_interval_sec': 5,
            'use_queue': True,
            'waiting_area': 'moscow_waiting',
            'whitelist_classes': {
                'econom': {'reposition_enabled': False, 'nearest_mins': 60},
            },
        },
    },
)
async def test_airports(taxi_atlas_drivers, candidates, mockserver):
    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted([])

    @mockserver.json_handler('/dispatch-airport/v1/active-drivers-queues')
    def _(_):
        return {
            'queues': [
                {
                    'tariff': 'econom',
                    'active_drivers': [
                        {
                            'dbid_uuid': f'{driver.ids.park_id}_{driver.ids.driver_profile_id}',
                            'queued': '2019-06-10T13:02:20Z',
                        }
                        for driver in _SAMPLE_DRIVERS[::2]
                    ],
                },
            ],
        }

    categories = ['airports']
    request = {
        'search_area': drivers.DEFAULT_SEARCH_AREA,
        'required_fields': categories,
    }
    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)
    assert response.status_code == 200

    infos = fbs_parse.parse_drivers_info(response.content)
    assert len(infos) == len(_SAMPLE_DRIVERS)

    infos = list(sorted(infos, key=lambda x: x.ids.park_id))
    for lhs, rhs in zip(infos, _SAMPLE_DRIVERS):
        driver_info.compare_drivers(lhs, rhs, categories)
