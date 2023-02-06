# flake8: noqa F401, IS001
# pylint: disable=C5521
from tests_atlas_drivers import driver_info
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import drivers


_SAMPLE_DRIVERS = drivers.generate_drivers(
    7, statuses=drivers.generate_statuses,
)


def _generate_busy_drivers(sample_drivers):
    order_status_map = {'driving': 1, 'waiting': 2, 'transporting': 3}

    busy_drivers = []
    for driver in sample_drivers:
        if driver.statuses.order:
            driver_id = driver.ids.park_id + '_' + driver.ids.driver_profile_id
            order_status = order_status_map[driver.statuses.order]
            busy_drivers.append(
                {
                    'driver_id': driver_id,
                    'order_id': 'order_id_any',
                    'taxi_status': order_status,
                },
            )
    return busy_drivers


async def test_busy_drivers(
        taxi_atlas_drivers, candidates, busy_drivers_mocks,
):
    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted(['status'])

    busy_drivers_mocks.set_drivers(_generate_busy_drivers(_SAMPLE_DRIVERS))
    await taxi_atlas_drivers.invalidate_caches()

    categories = ['statuses']
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
