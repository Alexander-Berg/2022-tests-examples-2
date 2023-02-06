# pylint: disable=import-error, no-name-in-module
from heatmaps.polylines import PolylinesHeatmap
from heatmaps.polylines import Position
import pytest

S3MOCKHANDLE = '/heatmap-mds-s3'

EXPECTED_REGIONS = [
    {
        'envelope': {
            'tl': {'lon': 37.0, 'lat': 56.0},
            'br': {'lon': 38.0, 'lat': 55.0},
        },
        'all_edges': [
            [
                {
                    'start': {'lon': 37.58, 'lat': 55.81},
                    'end': {'lon': 37.58, 'lat': 55.81},
                    'value': 1.0,
                    'road_class': 3,
                    'edge_id': 18195,
                },
                {
                    'start': {'lon': 37.58, 'lat': 55.81},
                    'end': {'lon': 37.58, 'lat': 55.81},
                    'value': 1.0,
                    'road_class': 3,
                    'edge_id': 18280,
                },
                {
                    'start': {'lon': 37.58, 'lat': 55.81},
                    'end': {'lon': 37.58, 'lat': 55.81},
                    'value': 1.0,
                    'road_class': 6,
                    'edge_id': 18281,
                },
                {
                    'start': {'lon': 37.58, 'lat': 55.81},
                    'end': {'lon': 37.579, 'lat': 55.811},
                    'value': 1.0,
                    'road_class': 3,
                    'edge_id': 235368,
                },
                {
                    'start': {'lon': 37.58, 'lat': 55.81},
                    'end': {'lon': 37.58, 'lat': 55.81},
                    'value': 1.0,
                    'road_class': 6,
                    'edge_id': 235576,
                },
            ],
        ],
        'min_value': 1.0,
        'max_value': 2.0,
        'legend': '1.00 - 2.00',
        'legend_precision': 2,
    },
]


def parse_map(map_fbs):
    map_fb = PolylinesHeatmap.PolylinesHeatmap.GetRootAsPolylinesHeatmap(
        map_fbs, 0,
    )
    regions = []
    for i in range(map_fb.RegionsLength()):
        region_fb = map_fb.Regions(i)
        edges_vecs = []
        for j in range(region_fb.AllEdgesLength()):
            edges_vec_fb = region_fb.AllEdges(j)
            edges = []
            for k in range(edges_vec_fb.EdgesLength()):
                edge_fb = edges_vec_fb.Edges(k)
                edge = {
                    'start': {
                        'lon': round(edge_fb.Start().Lon(), 3),
                        'lat': round(edge_fb.Start().Lat(), 3),
                    },
                    'end': {
                        'lon': round(edge_fb.End().Lon(), 3),
                        'lat': round(edge_fb.End().Lat(), 3),
                    },
                    'value': round(edge_fb.Value(), 3),
                    'road_class': edge_fb.RoadClass(),
                    'edge_id': edge_fb.EdgeId(),
                }
                edges.append(edge)
            edges_vecs.append(edges)
        tl_fb = Position.Position()
        tl_fb = region_fb.Envelope().Tl(tl_fb)
        br_fb = Position.Position()
        br_fb = region_fb.Envelope().Br(br_fb)
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
            'all_edges': edges_vecs,
            'min_value': round(region_fb.MinValue(), 3),
            'max_value': round(region_fb.MaxValue(), 3),
            'legend': region_fb.Legend().decode(),
            'legend_precision': region_fb.LegendPrecision(),
        }
        regions.append(region)
    return {'regions': regions}


# +5 min after samples' 'created' time
@pytest.mark.now('2019-03-08T00:05:00Z')
@pytest.mark.experiments3(filename='calc_graph_surge_map_settings.json')
@pytest.mark.config(
    PIN_STORAGE_GENERATE_GRAPH_SURGE_MAP=True,
    PIN_STORAGE_GRAPH_LOG_EDGES_CALCULATIONS={
        'enabled': True,
        'zone': {'point': [37, 55], 'radius_m': 100_000},
    },
)
@pytest.mark.suspend_periodic_tasks('calc-graph-surge-map-periodic')
@pytest.mark.usefixtures('distlocks_mockserver')
async def test_calc_graph_heatmap(taxi_pin_storage, mockserver, testpoint):
    actual_saved_map = {}

    @mockserver.handler(S3MOCKHANDLE, prefix=True)
    def _mock_s3_put(request):
        assert request.method == 'PUT'
        map_data = request.get_data()
        content_key = request.path[len(f'{S3MOCKHANDLE}/') :]

        actual_saved_map[content_key] = map_data
        return mockserver.make_response('OK', 200)

    @testpoint('calc-graph-surge-map-finish')
    def handle_calc_job_finish(_):
        pass

    await taxi_pin_storage.enable_testpoints()
    await taxi_pin_storage.run_periodic_task('calc-graph-surge-map-periodic')
    await handle_calc_job_finish.wait_call()

    assert actual_saved_map.keys() == {'taxi_graph_surge/__default__/default'}

    heatmap = actual_saved_map['taxi_graph_surge/__default__/default']
    actual = parse_map(heatmap)
    actual_regions = actual['regions']

    # Sort by cluster tl lon
    def normalized_regions(regions):
        regions_sorted = list(
            sorted(regions, key=lambda x: x['envelope']['tl']['lon']),
        )
        for region in regions_sorted:
            for i, edges in enumerate(region['all_edges']):
                for edge in edges:
                    edge['start']['lon'] = round(edge['start']['lon'], 2)
                    edge['start']['lat'] = round(edge['start']['lat'], 2)
                    edge['end']['lon'] = round(edge['end']['lon'], 2)
                    edge['end']['lat'] = round(edge['end']['lat'], 2)
                region['all_edges'][i] = sorted(
                    edges, key=lambda x: x['edge_id'],
                )

        return regions_sorted

    assert len(actual_regions) == len(EXPECTED_REGIONS)

    normalized_actual_regions = normalized_regions(actual_regions)
    normalized_expected_regions = normalized_regions(EXPECTED_REGIONS)

    for i, expected_region in enumerate(normalized_expected_regions):
        actual_region = normalized_actual_regions[i]

        actual_edges = actual_region['all_edges'][0]
        expected_edges = expected_region['all_edges'][0]

        # Sort by road_class
        def normalized_edges(edges):
            edges_sorted = list(sorted(edges, key=lambda x: x['edge_id']))
            return edges_sorted

        assert normalized_edges(actual_edges) == normalized_edges(
            expected_edges,
        )
