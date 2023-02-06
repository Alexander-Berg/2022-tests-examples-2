# pylint: disable=import-error
import flatbuffers
from heatmap_sample_storage.surge_points.fbs import Point
from heatmap_sample_storage.surge_points.fbs import SurgePoint
from heatmap_sample_storage.surge_points.fbs import SurgePointsResponse
import pytest

FILENAME = 'surge_points_calculations.json'


def build_surge_points_fb(surge_points_response):
    builder = flatbuffers.Builder(0)
    points = surge_points_response['points']
    points_fbs = []
    for point in points:
        category_fbs = builder.CreateString(point['category'])
        id_ = builder.CreateString(point.get('id', ''))
        percentiles = point.get('point_b_adj_percentiles', [])
        SurgePoint.SurgePointStartPointBAdjPercentilesVector(
            builder, len(percentiles),
        )
        for percentile in reversed(percentiles):
            builder.PrependFloat64(percentile)
        point_b_adj_percentiles_fb = builder.EndVector(len(percentiles))

        SurgePoint.SurgePointStart(builder)
        position = point['position']
        SurgePoint.SurgePointAddPosition(
            builder,
            Point.CreatePoint(builder, position['lat'], position['lon']),
        )
        SurgePoint.SurgePointAddCategory(builder, category_fbs)
        SurgePoint.SurgePointAddPins(builder, point['pins'])
        SurgePoint.SurgePointAddPinsOrder(builder, point['pins_order'])
        SurgePoint.SurgePointAddPinsDriver(builder, point['pins_driver'])
        SurgePoint.SurgePointAddFree(builder, point['free'])
        SurgePoint.SurgePointAddTotal(builder, point['total'])
        SurgePoint.SurgePointAddRadius(builder, point['radius'])
        SurgePoint.SurgePointAddValueRaw(builder, point['value_raw'])
        SurgePoint.SurgePointAddValueSmooth(builder, point['value_smooth'])
        SurgePoint.SurgePointAddCreatedTs(builder, point['created_ts'])
        SurgePoint.SurgePointAddSurgeValueInTariff(
            builder, point['surge_value_in_tariff'],
        )
        SurgePoint.SurgePointAddPsShiftPastRaw(
            builder, point['ps_shift_past_raw'],
        )
        SurgePoint.SurgePointAddDeviationFromTargetAbs(
            builder, point['deviation_from_target_abs'],
        )
        SurgePoint.SurgePointAddValueRawGraph(
            builder, point['value_raw_graph'],
        )
        SurgePoint.SurgePointAddCost(builder, point['cost'])
        SurgePoint.SurgePointAddId(builder, id_)
        SurgePoint.SurgePointAddPointBAdjPercentiles(
            builder, point_b_adj_percentiles_fb,
        )
        points_fbs.append(SurgePoint.SurgePointEnd(builder))

    SurgePointsResponse.SurgePointsResponseStartPointsVector(
        builder, len(points_fbs),
    )
    for point_fbs in points_fbs:
        builder.PrependUOffsetTRelative(point_fbs)
    points_vec = builder.EndVector(len(points_fbs))

    cursor_fbs = builder.CreateString(surge_points_response['cursor'])
    SurgePointsResponse.SurgePointsResponseStart(builder)
    SurgePointsResponse.SurgePointsResponseAddPoints(builder, points_vec)
    SurgePointsResponse.SurgePointsResponseAddCursor(builder, cursor_fbs)
    SurgePointsResponse.SurgePointsResponseAddTtlSec(
        builder, surge_points_response['ttl_sec'],
    )
    response_fbs = SurgePointsResponse.SurgePointsResponseEnd(builder)
    builder.Finish(response_fbs)
    return builder.Output()


class CalculationsContext:
    def __init__(self, calculations):
        self.calculations = calculations

    def set_surge_points_calculations(self, calculations):
        self.calculations = calculations


@pytest.fixture(autouse=True)
def surge_points_calculations(mockserver, load_json):
    calculations = []
    try:
        calculations = load_json(FILENAME)
    except FileNotFoundError:
        pass

    ctx = CalculationsContext(calculations)

    @mockserver.json_handler('/heatmap-sample-storage/v1/surge_points')
    def _v1_surge_points(request):
        if not request.args.get('cursor'):
            return mockserver.make_response(
                response=build_surge_points_fb(
                    {
                        'cursor': 'some_cursor',
                        'ttl_sec': 600,
                        'points': ctx.calculations,
                    },
                ),
                content_type='application/flatbuffer',
            )
        return mockserver.make_response(status=204)

    return ctx
