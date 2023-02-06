# pylint: disable=unused-import, import-only-modules, import-error
# pylint: disable=invalid-name, unused-variable, wrong-import-order
import typing as tp

import flatbuffers
from heatmaps.polylines import Box
from heatmaps.polylines import Edge
from heatmaps.polylines import EdgesVec
from heatmaps.polylines import PolylinesHeatmap
from heatmaps.polylines import Position
from heatmaps.polylines import Region
import pytest

FILENAME = 'surge_polylines_map.json'


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


@pytest.fixture
def s3_polyline_storage(s3_heatmap_storage, load_json):
    class PolylineStorageContext:
        def add_map(
                self,
                content_key: str,
                s3version: str,
                created: tp.Optional[str],
                expires: tp.Optional[str],
        ):
            polyline_map = load_json(FILENAME)
            s3_heatmap_storage.add_map(
                content_key,
                s3version,
                created,
                expires,
                'polylines',
                build_polylines_map(polyline_map),
            )

    context = PolylineStorageContext()
    return context
