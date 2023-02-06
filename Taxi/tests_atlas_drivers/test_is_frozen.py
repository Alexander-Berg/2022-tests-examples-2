# flake8: noqa F401, IS001
# pylint: disable=C5521
from tests_atlas_drivers import driver_info
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import drivers


_SAMPLE_DRIVERS = drivers.generate_drivers(
    32, is_frozen=drivers.generate_is_frozen,
)


def _generate_is_frozens():
    unique_driver_ids = []
    car_ids = []
    for i in range(64):
        is_frozen = drivers.generate_is_frozen(i)
        if is_frozen.freeze:
            unique_driver_ids.append(drivers.generate_id('udid', i))
            car_ids.append(drivers.generate_id('car_number', i))
    return {
        'unique_driver_ids': unique_driver_ids,
        'car_ids': car_ids,
        'timestamp': 1,
    }


async def test_is_frozen(taxi_atlas_drivers, candidates, frozen_drivers_mocks):
    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted(['unique_driver_id', 'car_number'])

    frozen_drivers_mocks.set_frozen_drivers(_generate_is_frozens())
    await taxi_atlas_drivers.invalidate_caches()

    categories = ['is_frozen']
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
