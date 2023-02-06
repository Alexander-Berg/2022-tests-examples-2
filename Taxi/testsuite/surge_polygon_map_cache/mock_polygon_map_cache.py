# pylint: disable=unused-import, import-only-modules, import-error
# pylint: disable=invalid-name, unused-variable, wrong-import-order
import typing as tp

import flatbuffers
from heatmaps.polygons import Box
from heatmaps.polygons import Polygon
from heatmaps.polygons import PolygonsHeatmap
from heatmaps.polygons import Position
from heatmaps.polygons import Region
import pytest

FILENAME = 'surge_polygon_map.json'


def build_polygons_map(map_data):
    builder = flatbuffers.Builder(0)
    regions = map_data['regions']
    for region in map_data['regions']:
        polygons = region['polygons']
        for polygon in polygons:
            points = polygon['points']
            points_fbs = []
            for point in points:
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


@pytest.fixture
def s3_polygon_storage(s3_heatmap_storage, load_json):
    class PolygonStorageContext:
        def add_map(
                self,
                content_key: str,
                s3version: str,
                created: tp.Optional[str],
                expires: tp.Optional[str],
        ):
            polygon_map = load_json(FILENAME)
            s3_heatmap_storage.add_map(
                content_key,
                s3version,
                created,
                expires,
                'polygons',
                build_polygons_map(polygon_map),
            )

    context = PolygonStorageContext()
    return context
