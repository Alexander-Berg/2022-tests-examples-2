# pylint: disable=import-error
import io
import logging

import flatbuffers
from heatmaps.polygons import Box
from heatmaps.polygons import Polygon
from heatmaps.polygons import PolygonsHeatmap
from heatmaps.polygons import Position
from heatmaps.polygons import Region
import PIL.Image
import pytest

from tests_heatmap_renderer import common

CONTENT_KEY = 'polygons_content'

# due to some 3rd-party implementation-specific details we can get different
# pixels on hexagons borders (impossible to identify it by eye).
# So we use threshold to identify if images are quite equal
SIMILARITY_THRESHOLD = 0.995

logger = logging.getLogger(__name__)


def build_polygons_map(map_data):
    builder = flatbuffers.Builder(0)
    regions = map_data['regions']
    for region in map_data['regions']:
        polygons = region['polygons']
        for polygon in polygons:
            points = polygon['points']
            points_fbs = []
            for point in points:
                logger.info(point)
                Position.PositionStart(builder)
                Position.PositionAddLon(builder, point['lon'])
                Position.PositionAddLat(builder, point['lat'])
                point_fbs = Position.PositionEnd(builder)
                points_fbs.append(point_fbs)
            points_fbs.reverse()
            Polygon.PolygonStartPointsVector(builder, len(points_fbs))
            for point_fbs in points_fbs:
                builder.PrependUOffsetTRelative(point_fbs)
            points = builder.EndVector(len(points_fbs))

            Polygon.PolygonStart(builder)
            Polygon.PolygonAddPoints(builder, points)
            Polygon.PolygonAddValue(builder, polygon['value'])
            polygon['fbs'] = Polygon.PolygonEnd(builder)

        Region.RegionStartPolygonsVector(builder, len(polygons))
        for polygon in polygons:
            builder.PrependUOffsetTRelative(polygon['fbs'])
        polygons = builder.EndVector(len(polygons))

        region['legend_fb'] = builder.CreateString(region['legend'])

        Position.PositionStart(builder)
        Position.PositionAddLon(builder, region['envelope']['tl']['lon'])
        Position.PositionAddLat(builder, region['envelope']['tl']['lat'])
        box_tl = Position.PositionEnd(builder)

        Position.PositionStart(builder)
        Position.PositionAddLon(builder, region['envelope']['br']['lon'])
        Position.PositionAddLat(builder, region['envelope']['br']['lat'])
        box_br = Position.PositionEnd(builder)

        Box.BoxStart(builder)
        Box.BoxAddTl(builder, box_tl)
        Box.BoxAddBr(builder, box_br)
        box = Box.BoxEnd(builder)

        Region.RegionStart(builder)
        Region.RegionAddPolygons(builder, polygons)
        Region.RegionAddEnvelope(builder, box)
        Region.RegionAddMinValue(builder, region['min_value'])
        Region.RegionAddMaxValue(builder, region['max_value'])
        Region.RegionAddLegend(builder, region['legend_fb'])
        Region.RegionAddLegendPrecision(builder, region['legend_precision'])
        region['fbs'] = Region.RegionEnd(builder)

    PolygonsHeatmap.PolygonsHeatmapStartRegionsVector(builder, len(regions))
    for region in regions:
        builder.PrependUOffsetTRelative(region['fbs'])
    regions = builder.EndVector(len(regions))

    PolygonsHeatmap.PolygonsHeatmapStart(builder)
    PolygonsHeatmap.PolygonsHeatmapAddRegions(builder, regions)
    surge_value_map = PolygonsHeatmap.PolygonsHeatmapEnd(builder)
    builder.Finish(surge_value_map)
    return builder.Output()


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.config(HEATMAP_RENDERER_AVAILABLE_CONTENT_KEYS=[CONTENT_KEY])
async def test_meta_and_tile(
        taxi_heatmap_renderer, heatmap_storage, get_file_path,
):
    heatmap_storage.add_map(
        CONTENT_KEY,
        6,
        '2019-01-02T03:00:00+0000',
        '2019-01-02T04:00:00+0000',
        'polygons',
        serialized_map=build_polygons_map(
            {
                'regions': [
                    {
                        'polygons': [
                            {
                                'points': [
                                    {'lon': 37.6272, 'lat': 55.7179},
                                    {'lon': 37.6272, 'lat': 55.7679},
                                    {'lon': 37.6672, 'lat': 55.7679},
                                    {'lon': 37.6672, 'lat': 55.7179},
                                ],
                                'value': 1.3,
                            },
                            {
                                'points': [
                                    {'lon': 37.6672, 'lat': 55.7579},
                                    {'lon': 37.6772, 'lat': 55.7079},
                                    {'lon': 37.6872, 'lat': 55.7579},
                                ],
                                'value': 1.6,
                            },
                        ],
                        'envelope': {
                            'br': {'lon': 37.0, 'lat': 55.0},
                            'tl': {'lon': 38.0, 'lat': 56.0},
                        },
                        'legend': '1.3 - 1.6',
                        'legend_precision': 2,
                        'min_value': 1.3,
                        'max_value': 1.6,
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
        'legend': '1.3 - 1.6',
        'legend_max': 1.6,
        'legend_min': 1.3,
        'legend_precision': 2,
        'updated_epoch': 1546398000,
        'version_id': '6',
    }

    tile_response = await taxi_heatmap_renderer.get(
        'tile?v=6&x=2476&y=1284&z=12',
    )

    assert tile_response.status_code == 200
    assert tile_response.headers['Access-Control-Allow-Origin'] == '*'
    response_image = PIL.Image.open(io.BytesIO(tile_response.content))
    expected_image = PIL.Image.open(get_file_path('polygons_tile.png'))

    assert (
        common.images_similarity(response_image, expected_image)
        >= SIMILARITY_THRESHOLD
    )
    # buf = io.BytesIO(tile_response.content)
    # with open('/home/diplomate/Desktop/useful/picture_polygon.png',
    # 'wb') as f:
    #     f.write(buf.getbuffer())
