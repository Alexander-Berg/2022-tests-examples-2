# flake8: noqa F401, IS001
# pylint: disable=C5521
from tests_atlas_drivers import driver_info
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import drivers


_SAMPLE_DRIVERS = drivers.generate_drivers(
    7, order_info=drivers.generate_order_info,
)


def _generate_busy_drivers(sample_drivers):
    busy_drivers = []
    for driver in sample_drivers:
        if driver.order_info:
            driver_id = driver.ids.park_id + '_' + driver.ids.driver_profile_id
            busy_driver = {
                'driver_id': driver_id,
                'order_id': driver.order_info.order_id,
                'taxi_status': 1,
            }
            if driver.order_info.point_b:
                busy_driver['destination'] = {
                    'lat': driver.order_info.point_b.lat,
                    'lon': driver.order_info.point_b.lon,
                }
            busy_drivers.append(busy_driver)
    return busy_drivers


async def test_order_info(taxi_atlas_drivers, candidates, busy_drivers_mocks):
    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted([])

    busy_drivers_mocks.set_drivers(_generate_busy_drivers(_SAMPLE_DRIVERS))
    await taxi_atlas_drivers.invalidate_caches()

    categories = ['order_info']
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
