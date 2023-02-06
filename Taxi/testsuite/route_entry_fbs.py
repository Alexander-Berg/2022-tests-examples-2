# pylint: disable=import-error
# pylint: disable=no-name-in-module
import math

import flatbuffers
import geometry.fbs.Position as FbsPosition
import route.fbs.Leg as FbsLeg
import route.fbs.Route as FbsRoute
import route.fbs.RoutePoint as FbsRoutePoint
import route_entry.fbs.RouteEntry as FbsRouteEntry


def _round_away_from_zero(value):
    abs_value = abs(value)
    res = math.floor(abs_value) + math.floor(2 * (abs_value % 1))
    return res if value >= 0.0 else -res


def _deserialize_route_point(fbs_route_point):
    fbs_pos = FbsPosition.Position()
    return {
        'position': FbsPosition.deserialize_position(
            fbs_route_point.Position(fbs_pos),
        ),
        'time': fbs_route_point.TimeSinceRideStart(),
        'distance': fbs_route_point.DistanceSinceRideStart(),
    }


def _deserialize_leg(fbs_leg):
    return {
        'segment_index': fbs_leg.SegmentPosition(),
        'segment_position': fbs_leg.SegmentPosition(),
    }


def _serialize_route_point(builder, route_point):
    pos = route_point['position']
    lon = int(_round_away_from_zero(pos[0] * 1000000))
    lat = int(_round_away_from_zero(pos[1] * 1000000))
    time = route_point['time']
    distance = route_point['distance']
    return FbsRoutePoint.CreateRoutePoint(builder, lon, lat, time, distance)


def _serialize_leg(builder, leg):
    return FbsLeg.CreateLeg(
        builder, leg['segment_index'], leg['segment_position'],
    )


def deserialize_route_entry(data):
    """ Deserialize from flatbuffers buffer to route entry
    @param entry
    entry = {
        route: {
            route: [
                {
                    position: [37.37, 55.55],
                    time: 42,  # since start
                    distance: 100500,  # since start
                }
            ],
            distance: 100500,
            time: 142,
            closures: false,
            dead_jams: false,
            toll_roads: false,
        },
        timestamp: 1234567890,
    }
    """
    fbs_entry = FbsRouteEntry.RouteEntry.GetRootAsRouteEntry(data, 0)
    fbs_route = fbs_entry.Route()
    timestamp = fbs_entry.Timestamp()
    closures = bool(fbs_route.HasClosures())
    dead_jams = bool(fbs_route.HasDeadJams())
    toll_roads = bool(fbs_route.HasTollRoads())

    fbs_path_length = fbs_route.RouteLength()
    route = [
        _deserialize_route_point(fbs_route.Route(i))
        for i in range(fbs_path_length)
    ]
    fbs_legs_length = fbs_route.LegsLength()
    legs = [
        _deserialize_leg(fbs_route.Legs(i)) for i in range(fbs_legs_length)
    ]
    distance = fbs_route.RouteDistance()
    time = fbs_route.RouteTime()
    return {
        'route': {
            'route': route,
            'legs': legs,
            'distance': distance,
            'time': time,
            'closures': closures,
            'dead_jams': dead_jams,
            'toll_roads': toll_roads,
        },
        'timestamp': timestamp,
    }


def _serialize_route(builder, route):
    path = route['route']
    distance = route['distance']
    time = route['time']
    closures = route['closures']
    dead_jams = route['dead_jams']
    toll_roads = route['toll_roads']
    legs = route['legs']

    fbs_route_points_count = len(path)
    FbsRoute.RouteStartRouteVector(builder, fbs_route_points_count)
    for point in reversed(path):
        _serialize_route_point(builder, point)
    fbs_path = builder.EndVector(fbs_route_points_count)

    fbs_legs_count = len(legs)
    FbsRoute.RouteStartRouteVector(builder, fbs_legs_count)
    for leg in reversed(legs):
        _serialize_leg(builder, leg)
    fbs_leg = builder.EndVector(fbs_legs_count)

    FbsRoute.RouteStart(builder)
    FbsRoute.RouteAddRoute(builder, fbs_path)
    FbsRoute.RouteAddRouteTime(builder, time)
    FbsRoute.RouteAddRouteDistance(builder, distance)
    FbsRoute.RouteAddHasClosures(builder, closures)
    FbsRoute.RouteAddHasDeadJams(builder, dead_jams)
    FbsRoute.RouteAddHasTollRoads(builder, toll_roads)
    FbsRoute.RouteAddLegs(builder, fbs_leg)

    return FbsRoute.RouteEnd(builder)


def serialize_route_entry(entry):
    """ Serialize to flatbuffers
    @param entry
    entry = {
        'route': {
            'route': [
                {
                    'position': [37.37, 55.55],
                    'time': 42,  # since start
                    'distance': 100500,  # since start
                }
            ],
            'distance': 100500,
            'time': 142,
            'closures': false,
            'dead_jams': false,
            'toll_roads': false,
            'legs': [
                {
                    'segment_index': 0,
                    'segment_position': 0,
                }
            ]
        },
        'timestamp': 1234567890,
    }
    """
    timestamp = entry['timestamp']
    route = entry['route']

    builder = flatbuffers.Builder(1024)
    fbs_route = _serialize_route(builder, route)

    FbsRouteEntry.RouteEntryStart(builder)
    FbsRouteEntry.RouteEntryAddRoute(builder, fbs_route)
    FbsRouteEntry.RouteEntryAddTimestamp(builder, timestamp)
    obj = FbsRouteEntry.RouteEntryEnd(builder)

    builder.Finish(obj)
    return bytes(builder.Output())
