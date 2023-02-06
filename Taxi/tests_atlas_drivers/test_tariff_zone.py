# flake8: noqa F401, IS001
# pylint: disable=C5521
from tests_atlas_drivers import driver_info
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import drivers


_DRIVERS_COUNT = 7
_SAMPLE_DRIVERS = drivers.generate_drivers(
    _DRIVERS_COUNT,
    point=drivers.generate_point,
    tariff_zone=drivers.generate_tariff_zone,
)


async def test_tariff_zone(taxi_atlas_drivers, candidates):
    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted([])

    categories = ['tariff_zone']
    request = {
        'search_area': {
            'top_left': {'lon': 36, 'lat': 54},
            'bottom_right': {'lon': 39, 'lat': 57},
        },
        'required_fields': categories,
    }
    response = await taxi_atlas_drivers.post('v1/find-in-area', json=request)
    assert response.status_code == 200

    infos = fbs_parse.parse_drivers_info(response.content)
    assert len(infos) == len(_SAMPLE_DRIVERS)

    infos = list(sorted(infos, key=lambda x: x.ids.park_id))
    for lhs, rhs in zip(infos, _SAMPLE_DRIVERS):
        driver_info.compare_drivers(lhs, rhs, categories)
