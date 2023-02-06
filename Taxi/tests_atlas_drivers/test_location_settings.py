# flake8: noqa F401, IS001
# pylint: disable=C5521
from tests_atlas_drivers import driver_info
from tests_atlas_drivers import fbs_parse
from tests_atlas_drivers.candidates_fixture import _candidates
from tests_atlas_drivers import drivers

SOURCES = {
    'realtime_source': 'android_gps',
    'verified_source': 'yandex_lbs_wifi',
}
_SAMPLE_DRIVERS = drivers.generate_drivers(
    7, location_settings=lambda _: driver_info.LocationSettings(**SOURCES),
)


async def test_location_settings(taxi_atlas_drivers, candidates, mockserver):
    @mockserver.json_handler('/coord-control/atlas/performers-meta-info')
    def _performers_meta_info(request):
        response = []
        for performer in request.json['performers']:
            response.append({'dbid_uuid': performer['dbid_uuid'], **SOURCES})
        return {'performers': response}

    categories = ['location_settings']

    candidates.set_drivers(_SAMPLE_DRIVERS)
    candidates.set_data_keys_wanted([])

    await taxi_atlas_drivers.invalidate_caches()

    response = await taxi_atlas_drivers.post(
        'v1/find-in-area',
        json={
            'search_area': drivers.DEFAULT_SEARCH_AREA,
            'required_fields': categories,
        },
    )
    assert response.status_code == 200

    infos = fbs_parse.parse_drivers_info(response.content)
    assert len(infos) == len(_SAMPLE_DRIVERS)

    infos = list(sorted(infos, key=lambda x: x.ids.park_id))
    for lhs, rhs in zip(infos, _SAMPLE_DRIVERS):
        driver_info.compare_drivers(lhs, rhs, categories)
