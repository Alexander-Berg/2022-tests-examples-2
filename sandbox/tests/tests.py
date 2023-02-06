from datetime import datetime

import sandbox.projects.garden.OfflineTileCacheToStat as OT


def _create_build(build_name, build_id, release_name="", status="completed"):
    return {
        "id": build_id,
        "name": build_name,
        "contour_name": "stable",
        "properties": {
            "release_name": release_name
        },
        "started_at": datetime.now().isoformat(),
        "completed_at": datetime.now().isoformat(),
    }


OFFLINE_CACHE_BUILDS = [
    _create_build(OT.OFFLINE_TILE_CACHE_MODULE, 0, release_name="release_0"),
]

OFFLINE_CACHE_RESOURCES = [
    {
        "name": "cache_file_uploaded_navi-1_en_RU_vnav2fb_0_0_15",
        "type": "YMDSFileResource",
        "key": "00017d50c0a4ebe738e3007c15f9ba01",
        "properties": {
            "domain": "navi",
            "layer": "vnav2fb",
            "locale": "en_RU",
            "region": 1,
            "release_name": "21.05.16-0",
            "release_version": "21.05.16-0",
        },
        "contour": "datatesting",
        "size": {
            "bytes": 1
        },
        "uri": "",
        "created_at": "2021-05-16T06:36:59.567000+00:00"
    },
    {
        "name": "cache_file_uploaded_navi-5_en_RU_vnav2fb_0_0_15",
        "type": "YMDSFileResource",
        "key": "00017d50c0a4ebe738e3007c15f9ba01",
        "properties": {
            "domain": "navi",
            "layer": "vnav2fb",
            "locale": "en_RU",
            "region": 5,
            "release_name": "21.05.16-0",
            "release_version": "21.05.16-0",
        },
        "contour": "datatesting",
        "size": {
            "bytes": 1
        },
        "uri": "",
        "created_at": "2021-05-16T06:36:59.567000+00:00"
    },
]


def test_render_modules_to_stat(requests_mock):
    garden_url = "http://localhost"
    contour = "stable"
    from_date = datetime.now().isoformat()

    module_path = OT.GARDEN_MODULE_STATISTICS_URL + "?from={}&module={}&contour={}"
    requests_mock.get(module_path.format(garden_url, from_date, OT.OFFLINE_TILE_CACHE_MODULE, contour),
                      json=OFFLINE_CACHE_BUILDS)

    storage_path = OT.GARDEN_STORAGE_URL + "?build={}&limit={}"
    for build in OFFLINE_CACHE_BUILDS:
        requests_mock.get(storage_path.format(garden_url, "{0}:{1}".format(build["name"], build["id"]), 20000),
                          json=OFFLINE_CACHE_RESOURCES)

    data = []
    for b in OT._get_module_builds(garden_url, OT.OFFLINE_TILE_CACHE_MODULE, from_date, contour):
        data.extend(OT._gather_stat(b, OT._get_build_resources(garden_url, b)))
    assert len(data) == 2

    aggr_data = OT._aggregate_stat(data)
    assert len(aggr_data) == 1
    assert aggr_data[0]["size"] == 2

    filtered_data = [r for r in data if OT._in_stat_dict(r)]
    assert len(filtered_data) == 1
