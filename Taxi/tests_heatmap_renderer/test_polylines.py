# pylint: disable=import-error
import io

import flatbuffers
from heatmaps.polylines import Box
from heatmaps.polylines import Edge
from heatmaps.polylines import EdgesVec
from heatmaps.polylines import PolylinesHeatmap
from heatmaps.polylines import Position
from heatmaps.polylines import Region
import PIL.Image
import pytest

from tests_heatmap_renderer import common


CONTENT_KEY = 'polylines_content'

# due to some 3rd-party implementation-specific details we can get different
# pixels on hexagons borders (impossible to identify it by eye).
# So we use threshold to identify if images are quite equal
SIMILARITY_THRESHOLD = 0.995


def build_polylines_map(map_data):
    builder = flatbuffers.Builder(0)
    regions = map_data['regions']
    for region in map_data['regions']:
        for edges_vec in region['all_edges']:
            edges = edges_vec['edges']
            for edge in edges:
                Edge.EdgeStart(builder)
                Edge.EdgeAddStart(
                    builder,
                    Position.CreatePosition(
                        builder, edge['start']['lon'], edge['start']['lat'],
                    ),
                )
                Edge.EdgeAddEnd(
                    builder,
                    Position.CreatePosition(
                        builder, edge['end']['lon'], edge['end']['lat'],
                    ),
                )
                Edge.EdgeAddValue(builder, edge['value'])
                Edge.EdgeAddRoadClass(builder, edge['road_class'])
                Edge.EdgeAddEdgeId(builder, edge['edge_id'])
                edge['fbs'] = Edge.EdgeEnd(builder)
            EdgesVec.EdgesVecStartEdgesVector(builder, len(edges))
            for edge in edges:
                builder.PrependUOffsetTRelative(edge['fbs'])
            edges = builder.EndVector(len(edges))

            EdgesVec.EdgesVecStart(builder)
            EdgesVec.EdgesVecAddEdges(builder, edges)
            edges_vec['fbs'] = EdgesVec.EdgesVecEnd(builder)

        all_edges = region['all_edges']
        Region.RegionStartAllEdgesVector(builder, len(all_edges))
        for edges_vec in all_edges:
            builder.PrependUOffsetTRelative(edges_vec['fbs'])
        all_edges = builder.EndVector(len(all_edges))
        region['legend_fb'] = builder.CreateString(region['legend'])
        Region.RegionStart(builder)
        Region.RegionAddAllEdges(builder, all_edges)
        Region.RegionAddEnvelope(
            builder,
            Box.CreateBox(
                builder,
                region['envelope']['tl']['lon'],
                region['envelope']['tl']['lat'],
                region['envelope']['br']['lon'],
                region['envelope']['br']['lat'],
            ),
        )
        Region.RegionAddMinValue(builder, region['min_value'])
        Region.RegionAddMaxValue(builder, region['max_value'])
        Region.RegionAddLegend(builder, region['legend_fb'])
        Region.RegionAddLegendPrecision(builder, region['legend_precision'])
        region['fbs'] = Region.RegionEnd(builder)

    PolylinesHeatmap.PolylinesHeatmapStartRegionsVector(builder, len(regions))
    for region in regions:
        builder.PrependUOffsetTRelative(region['fbs'])
    regions = builder.EndVector(len(regions))

    PolylinesHeatmap.PolylinesHeatmapStart(builder)
    PolylinesHeatmap.PolylinesHeatmapAddRegions(builder, regions)
    surge_value_map = PolylinesHeatmap.PolylinesHeatmapEnd(builder)
    builder.Finish(surge_value_map)
    return builder.Output()


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.config(
    HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS=[CONTENT_KEY],
    HEATMAP_RENDERER_POLYLINE_RANK_ZOOMS=[
        12,
        12,
        12,
        12,
        12,
        12,
        12,
        12,
        12,
        12,
    ],
)
@pytest.mark.parametrize(
    'expected_png_filename',
    [
        pytest.param(
            'polylines_tile_no_aa.png',
            marks=pytest.mark.config(
                HEATMAP_RENDERER_POLYLINES_IMAGEMAGICK=False,
            ),
        ),
        pytest.param(
            'polylines_tile_aa.png',
            marks=pytest.mark.config(
                HEATMAP_RENDERER_POLYLINES_IMAGEMAGICK=True,
            ),
        ),
    ],
)
async def test_meta_and_tile(
        taxi_heatmap_renderer,
        heatmap_storage,
        get_file_path,
        expected_png_filename,
):
    heatmap_storage.add_map(
        CONTENT_KEY,
        5,
        '2019-01-02T03:00:00+0000',
        '2019-01-02T04:00:00+0000',
        'polylines',
        serialized_map=build_polylines_map(
            {
                'regions': [
                    {
                        'all_edges': [
                            {
                                'edges': [
                                    {
                                        'start': {
                                            'lon': 37.6172,
                                            'lat': 55.7179,
                                        },
                                        'end': {
                                            'lon': 37.7051,
                                            'lat': 55.7674,
                                        },
                                        'value': 1.1,
                                        'road_class': 5,
                                        'edge_id': 100,
                                    },
                                    {
                                        'start': {
                                            'lon': 37.6172,
                                            'lat': 55.7279,
                                        },
                                        'end': {
                                            'lon': 37.7051,
                                            'lat': 55.7279,
                                        },
                                        'value': 1.2,
                                        'road_class': 7,
                                        'edge_id': 100,
                                    },
                                    {
                                        'start': {
                                            'lon': 37.6472,
                                            'lat': 55.7079,
                                        },
                                        'end': {
                                            'lon': 37.6472,
                                            'lat': 55.7574,
                                        },
                                        'value': 1.3,
                                        'road_class': 6,
                                        'edge_id': 100,
                                    },
                                    {
                                        'start': {
                                            'lon': 37.6172,
                                            'lat': 55.6979,
                                        },
                                        'end': {
                                            'lon': 37.7051,
                                            'lat': 55.7474,
                                        },
                                        'value': 1.4,
                                        'road_class': 3,
                                        'edge_id': 100,
                                    },
                                ],
                            },
                        ],
                        'envelope': {
                            'br': {'lon': 37.0, 'lat': 55.0},
                            'tl': {'lon': 38.0, 'lat': 56.0},
                        },
                        'legend': '1.1 - 1.4',
                        'legend_precision': 2,
                        'min_value': 1.1,
                        'max_value': 1.4,
                    },
                ],
            },
        ),
    )
    await taxi_heatmap_renderer.run_periodic_task('heatmaps-component')

    meta_response = await taxi_heatmap_renderer.get(
        '/v2/meta?content={}&hash=ucfv12uxf'.format(CONTENT_KEY),
    )

    assert meta_response.status_code == 200

    assert meta_response.json() == {
        'legend': '1.1 - 1.4',
        'legend_max': 1.4,
        'legend_min': 1.1,
        'legend_precision': 2,
        'updated_epoch': 1546398000,
        'version_id': '5',
    }

    tile_response = await taxi_heatmap_renderer.get(
        'tile?v=5&x=2476&y=1284&z=12',
    )

    # Uncomment to save the result of the test
    # buf = io.BytesIO(tile_response.content)
    # with open('/home/diplomate/Desktop/useful/polylines.png', 'wb') as f:
    #     f.write(buf.getbuffer())

    assert tile_response.status_code == 200
    assert tile_response.headers['Access-Control-Allow-Origin'] == '*'
    response_image = PIL.Image.open(io.BytesIO(tile_response.content))
    expected_image = PIL.Image.open(get_file_path(expected_png_filename))

    assert (
        common.images_similarity(response_image, expected_image)
        >= SIMILARITY_THRESHOLD
    )
