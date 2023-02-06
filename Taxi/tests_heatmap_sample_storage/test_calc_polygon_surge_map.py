# pylint: disable=import-error, no-name-in-module
import logging

from heatmaps.polygons import PolygonsHeatmap
import pytest

S3MOCKHANDLE = '/heatmap-mds-s3'

logger = logging.getLogger(__name__)

EXPECTED_REGIONS = [
    {
        'polygons': [
            {
                'points': [
                    {'lat': 1.0, 'lon': 1.0},
                    {'lat': 2.0, 'lon': 5.0},
                    {'lat': 3.0, 'lon': 5.0},
                    {'lat': 3.0, 'lon': 4.0},
                    {'lat': 4.5, 'lon': 4.5},
                    {'lat': 5.0, 'lon': 4.0},
                    {'lat': 4.0, 'lon': 1.0},
                ],
                'value': 1.0,
            },
            {
                'points': [
                    {'lat': 3.0, 'lon': 4.0},
                    {'lat': 3.0, 'lon': 5.0},
                    {'lat': 4.0, 'lon': 5.0},
                    {'lat': 4.5, 'lon': 4.5},
                ],
                'value': 1.5,
            },
            {
                'points': [
                    {'lat': 3.0, 'lon': 5.0},
                    {'lat': 3.0, 'lon': 7.0},
                    {'lat': 6.0, 'lon': 7.0},
                    {'lat': 6.0, 'lon': 5.0},
                    {'lat': 4.5, 'lon': 4.5},
                    {'lat': 4.0, 'lon': 5.0},
                ],
                'value': 2.0,
            },
        ],
        'envelope': {
            'br': {'lat': 55.0, 'lon': 38.0},
            'tl': {'lat': 56.0, 'lon': 37.0},
        },
        'legend': '1.00 - 2.00',
        'legend_precision': 2,
        'min_value': 1.0,
        'max_value': 2.0,
    },
    {
        'polygons': [
            {
                'points': [
                    {'lat': 7.0, 'lon': 2.0},
                    {'lat': 7.0, 'lon': 4.0},
                    {'lat': 8.0, 'lon': 4.5},
                    {'lat': 8.0, 'lon': 4.0},
                    {'lat': 8.2, 'lon': 4.6},
                    {'lat': 9.0, 'lon': 5.0},
                    {'lat': 9.0, 'lon': 3.0},
                    {'lat': 10.0, 'lon': 2.0},
                ],
                'value': 3.0,
            },
            {
                'points': [
                    {'lat': 8.0, 'lon': 4.0},
                    {'lat': 8.0, 'lon': 4.5},
                    {'lat': 8.2, 'lon': 4.6},
                ],
                'value': 4.0,
            },
            {
                'points': [
                    {'lat': 8.0, 'lon': 4.5},
                    {'lat': 8.0, 'lon': 7.0},
                    {'lat': 9.0, 'lon': 7.0},
                    {'lat': 8.2, 'lon': 4.6},
                ],
                'value': 5.0,
            },
        ],
        'envelope': {
            'br': {'lat': 58.0, 'lon': 41.0},
            'tl': {'lat': 59.0, 'lon': 40.0},
        },
        'legend': '4.00 - 5.00',
        'legend_precision': 2,
        'min_value': 4.0,
        'max_value': 5.0,
    },
]


def parse_map(map_fbs):
    map_fb = PolygonsHeatmap.PolygonsHeatmap.GetRootAsPolygonsHeatmap(
        map_fbs, 0,
    )
    regions = []
    logger.info(f'RegionsLength={map_fb.RegionsLength()}')
    for i in range(map_fb.RegionsLength()):
        region_fb = map_fb.Regions(i)
        polygons = []
        logger.info(f'PolygonsLength={region_fb.PolygonsLength()}')
        for j in range(region_fb.PolygonsLength()):
            polygon_fb = region_fb.Polygons(j)
            points = []
            logger.info(f'PointsLength={polygon_fb.PointsLength()}')
            for k in range(polygon_fb.PointsLength()):
                point_fb = polygon_fb.Points(k)
                point = {
                    'lon': round(point_fb.Lon(), 3),
                    'lat': round(point_fb.Lat(), 3),
                }
                points.append(point)
            polygon = {'points': points, 'value': round(polygon_fb.Value(), 3)}
            polygons.append(polygon)
        tl_fb = region_fb.Envelope().Tl()
        br_fb = region_fb.Envelope().Br()
        region = {
            'envelope': {
                'tl': {
                    'lon': round(tl_fb.Lon(), 3),
                    'lat': round(tl_fb.Lat(), 3),
                },
                'br': {
                    'lon': round(br_fb.Lon(), 3),
                    'lat': round(br_fb.Lat(), 3),
                },
            },
            'polygons': polygons,
            'min_value': round(region_fb.MinValue(), 3),
            'max_value': round(region_fb.MaxValue(), 3),
            'legend': region_fb.Legend().decode(),
            'legend_precision': region_fb.LegendPrecision(),
        }
        regions.append(region)
    return {'regions': regions}


# +5  min after samples' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.experiments3(filename='polygon_map_config.json')
@pytest.mark.config(
    HEATMAP_SAMPLE_STORAGE_ENABLED_JOBS={'calc-polygon-surge-map': True},
)
@pytest.mark.suspend_periodic_tasks('calc-polygon-surge-map-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_calc_polygon_heatmap(
        taxi_heatmap_sample_storage, mockserver, testpoint,
):
    actual_saved_map = {}

    @mockserver.handler(S3MOCKHANDLE, prefix=True)
    def _mock_s3_put(request):
        assert request.method == 'PUT'
        map_data = request.get_data()
        content_key = request.path[len(f'{S3MOCKHANDLE}/') :]

        actual_saved_map[content_key] = map_data
        return mockserver.make_response('OK', 200)

    @testpoint('calc-polygon-surge-map-finish')
    def handle_calc_job_finish(arg):
        pass

    await taxi_heatmap_sample_storage.enable_testpoints()
    await taxi_heatmap_sample_storage.run_periodic_task(
        'calc-polygon-surge-map-periodic',
    )
    await handle_calc_job_finish.wait_call()

    assert actual_saved_map.keys() == {
        'taxi_polygon_surge/__default__/default',
    }

    heatmap = actual_saved_map['taxi_polygon_surge/__default__/default']
    actual = parse_map(heatmap)
    actual_regions = actual['regions']

    assert len(actual_regions) == len(EXPECTED_REGIONS)

    # Sort by cluster tl lon
    def normalized_regions(regions):
        regions_sorted = list(
            sorted(regions, key=lambda x: x['envelope']['tl']['lon']),
        )
        return regions_sorted

    normalized_actual_regions = normalized_regions(actual_regions)
    normalized_expected_regions = normalized_regions(EXPECTED_REGIONS)

    # Must be equal, taking into consideration cyclic permutations of points
    def compare_points(actual, expected) -> bool:
        logger.info(f'actual={actual}, expected={expected}')
        if len(actual) != len(expected):
            return False
        # Two cyclic permutations are equal,
        # if one is a substring of the doubled another
        double_actual = actual + actual
        # Have to compare like this because could be {lat, lon} or {lon, lat}
        for _i in range(0, len(actual)):
            equal = True
            for _j in range(_i, _i + len(actual)):
                if sorted(double_actual[_j]) != sorted(expected[_j]):
                    equal = False
                    break
            if equal:
                return True
        return False

    for i, expected_region in enumerate(normalized_expected_regions):
        actual_region = normalized_actual_regions[i]

        actual_polygons = actual_region['polygons']
        expected_polygons = expected_region['polygons']

        # Sort by value
        def normalized_polygons(polygons):
            polygons_sorted = list(sorted(polygons, key=lambda x: x['value']))
            return polygons_sorted

        assert len(actual_polygons) == len(expected_polygons)

        normalized_actual_polygons = normalized_polygons(actual_polygons)
        normalized_expected_polygons = normalized_polygons(expected_polygons)

        for j, actual_polygon in enumerate(normalized_actual_polygons):
            assert (
                actual_polygon['value']
                == normalized_expected_polygons[j]['value']
            )
            assert compare_points(
                actual_polygon['points'],
                normalized_expected_polygons[j]['points'],
            )
