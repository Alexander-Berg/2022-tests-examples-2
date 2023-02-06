# pylint: disable=import-error
# pylint: disable=no-name-in-module
import json
import math

import flatbuffers
import geometry.fbs.Position as FbsPosition
import output_entry.fbs.OutputEntry as OutputEntry
import output_entry.fbs.TimeDistanceLeft as TimeDistanceLeft
import route.fbs.Leg as FbsLeg
import route.fbs.Route as FbsRoute
import route.fbs.RoutePoint as FbsRoutePoint
import route_entry.fbs.RouteEntry as FbsRouteEntry

import tests_driver_route_watcher.points_list_fbs as PointslistFbs
import tests_driver_route_watcher.position_fbs as PositionFbs


def _round_away_from_zero(value):
    abs_value = abs(value)
    res = math.floor(abs_value) + math.floor(2 * (abs_value % 1))
    return res if value >= 0.0 else -res


def serialize_etas_fbs(builder, etas):
    if etas is None:
        return None
    OutputEntry.OutputEntryStartEtasVector(builder, len(etas))
    for eta in reversed(etas):
        TimeDistanceLeft.CreateTimeDistanceLeft(
            builder, eta['time_left'], eta['distance_left'],
        )
    return builder.EndVector(len(etas))


def deserialize_etas_fbs(fbs_entry):
    if fbs_entry is None:
        return None

    return [
        {
            'time_left': fbs_entry.Etas(i).TimeLeft(),
            'distance_left': fbs_entry.Etas(i).DistanceLeft(),
        }
        for i in range(fbs_entry.EtasLength())
    ]


def deserialize_output_entry(data):
    """ Deserialize from flatbuffers buffer to output entry
    @param entry
    entry = {
        'time_left': 42,
        'distance_left': 100500,
        'position': [37, 55],
        'raw_position': [37, 55],
        'destination': [38, 56],
        'direction': 277,
        'raw_direction': 137,
        'tracking_type': 'linear_fallback',  # or route_tracking
        'service_id': 'some-service-id',
        'route_id': 'some-route-id',
        'metainfo': {'some_field': 'some_value'},
        'points': [[11, 22], [33, 44], [38, 56]],
        'segment_id': 333,
        'etas': [
            {
                'time_left': 10,
                'distance_left': 2000,
            },
            {
                'time_left': 20,
                'distance_left': 20000,
            },
            {
                'time_left': 42,
                'distance_left': 100500,
            },
        ],
        'updated_since': timestamp, # seconds since epoch
        'eta_multiplier': 1,
    }
    """
    fbs_entry = OutputEntry.OutputEntry.GetRootAsOutputEntry(data, 0)
    fbs_time_distance = fbs_entry.TimeDistanceLeft()
    tracking_type = fbs_entry.TrackingType()
    position = PositionFbs.deserialize_position(fbs_entry.Position())
    raw_position = PositionFbs.deserialize_position(fbs_entry.RawPosition())
    destination = PositionFbs.deserialize_position(fbs_entry.Destination())
    time_left = fbs_time_distance.TimeLeft()
    distance_left = fbs_time_distance.DistanceLeft()
    raw_direction = fbs_entry.RawDirection()
    points = PointslistFbs.deserialize_pointslist_fbs(
        fbs_entry.Points(),
    ) or PointslistFbs.to_point_list([destination])
    order_id = fbs_entry.OrderId()
    route_id = fbs_entry.RouteId()
    tracking_type_map = {
        0: 'route_tracking',
        1: 'linear_fallback',
        2: 'unknown_destination',
    }
    segment_id = fbs_entry.SegmentId()
    output_updated = fbs_entry.UpdatedSince()
    eta_multiplier = fbs_entry.EtaMultiplier()
    ret = {
        'time_left': time_left,
        'distance_left': distance_left,
        'position': position,
        'raw_position': raw_position,
        'destination': destination,
        'tracking_type': tracking_type_map[tracking_type],  # or route_tracking
        'direction': fbs_entry.Direction(),
        'raw_direction': raw_direction if raw_direction >= 0 else None,
        'service_id': (fbs_entry.ServiceId() or b'').decode(),
        'metainfo': json.loads((fbs_entry.Metainfo() or b'{}').decode()),
        'points': points,
        'etas': deserialize_etas_fbs(fbs_entry),
        'updated_since': output_updated,
        'eta_multiplier': eta_multiplier,
    }
    if order_id is not None:
        ret.update({'order_id': order_id.decode()})
    if route_id is not None:
        ret.update({'route_id': route_id.decode()})
    if segment_id > -1:
        ret.update({'segment_id': segment_id})
    return ret


def serialize_output_entry(entry):
    """ Serialize to flatbuffers
    @param entry
    entry = {
        'time_left': 42,
        'distance_left': 100500,
        'position': [37, 55],
        'raw_position': [37, 55],
        'destination': [38, 56],
        'tracking_type': 'linear_fallback',  # or route_tracking
        'service_id': 'some-service-id',
        'metainfo': 'some:metainfo',
        'points': [[11, 22], [33, 44], [38, 56]],
        'order_id': 'some_order_id',  # optional
        'route_id': 'some_route_id',  # optional
        'etas': [
            {
                'time_left': 10,
                'distance_left': 2000,
            },
            {
                'time_left': 20,
                'distance_left': 20000,
            },
            {
                'time_left': 42,
                'distance_left': 100500,
            },
        ],
        'updated_since': timestamp, # seconds since epoch
        'eta_multiplier': 1,
    }
    """
    tracking_type_map = {
        'route_tracking': 0,
        'linear_fallback': 1,
        'unknown_destination': 2,
    }
    time_left = entry['time_left']
    distance_left = entry['distance_left']
    position = entry['position']
    raw_position = entry['raw_position']
    destination = entry['destination']
    direction = entry['direction']
    raw_direction = entry.get('raw_direction', -1)
    tracking_type = tracking_type_map[entry['tracking_type']]
    points = entry.get('points', PointslistFbs.to_point_list([destination]))
    order_id = entry.get('order_id')
    route_id = entry.get('route_id')
    segment_id = entry.get('segment_id', -1)
    updated_since = entry.get('updated_since', -1)
    eta_multiplier = entry.get('eta_multiplier', 1)

    builder = flatbuffers.Builder(0)

    fbs_service_id = builder.CreateString(entry.get('service_id', ''))
    fbs_metainfo = builder.CreateString(json.dumps(entry.get('metainfo', {})))
    fbs_points = PointslistFbs.serialize_pointslist_fbs(builder, points)
    fbs_order_id = (
        builder.CreateString(order_id) if order_id is not None else None
    )
    fbs_route_id = (
        builder.CreateString(route_id) if route_id is not None else None
    )
    fbs_etas = serialize_etas_fbs(builder, entry.get('etas'))

    OutputEntry.OutputEntryStart(builder)
    raw_position_fbs = PositionFbs.serialize_position(builder, raw_position)
    OutputEntry.OutputEntryAddRawPosition(builder, raw_position_fbs)

    position_fbs = PositionFbs.serialize_position(builder, position)
    OutputEntry.OutputEntryAddPosition(builder, position_fbs)

    destination_fbs = PositionFbs.serialize_position(builder, destination)
    OutputEntry.OutputEntryAddDestination(builder, destination_fbs)

    time_distance_left_fbs = TimeDistanceLeft.CreateTimeDistanceLeft(
        builder, time_left, distance_left,
    )
    OutputEntry.OutputEntryAddTimeDistanceLeft(builder, time_distance_left_fbs)

    OutputEntry.OutputEntryAddUpdatedSince(builder, updated_since)
    OutputEntry.OutputEntryAddEtaMultiplier(builder, eta_multiplier)

    OutputEntry.OutputEntryAddTrackingType(builder, tracking_type)
    OutputEntry.OutputEntryAddDirection(builder, direction)
    OutputEntry.OutputEntryAddRawDirection(builder, raw_direction)
    OutputEntry.OutputEntryAddServiceId(builder, fbs_service_id)
    OutputEntry.OutputEntryAddMetainfo(builder, fbs_metainfo)
    OutputEntry.OutputEntryAddPoints(builder, fbs_points)
    OutputEntry.OutputEntryAddSegmentId(builder, segment_id)
    if fbs_order_id:
        OutputEntry.OutputEntryAddOrderId(builder, fbs_order_id)
    if fbs_route_id:
        OutputEntry.OutputEntryAddRouteId(builder, fbs_route_id)
    if fbs_etas:
        OutputEntry.OutputEntryAddEtas(builder, fbs_etas)
    obj = OutputEntry.OutputEntryEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())


def _deserialize_route_point(fbs_route_point):
    fbs_pos = FbsPosition.Position()
    return {
        'position': PositionFbs.deserialize_position(
            fbs_route_point.Position(fbs_pos),
        ),
        'time': fbs_route_point.TimeSinceRideStart(),
        'distance': fbs_route_point.DistanceSinceRideStart(),
    }


def _deserialize_leg(fbs_leg):
    return {
        'segment_index': fbs_leg.SegmentIndex(),
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
    legs = route.get('legs')
    route_id = route.get('route_id', 'none')

    fbs_route_points_count = len(path)
    FbsRoute.RouteStartRouteVector(builder, fbs_route_points_count)
    for point in reversed(path):
        _serialize_route_point(builder, point)
    fbs_path = builder.EndVector(fbs_route_points_count)
    fbs_route_id = builder.CreateString(route_id)

    fbs_leg = None
    if legs:
        fbs_legs_count = len(legs)
        FbsRoute.RouteStartRouteVector(builder, fbs_legs_count)
        for leg in reversed(legs):
            _serialize_leg(builder, leg)
        fbs_leg = builder.EndVector(fbs_legs_count)
    else:
        # add default leg
        fbs_legs_count = 1
        FbsRoute.RouteStartRouteVector(builder, fbs_legs_count)
        _serialize_leg(builder, {'segment_index': 0, 'segment_position': 0})
        fbs_leg = builder.EndVector(fbs_legs_count)

    FbsRoute.RouteStart(builder)
    FbsRoute.RouteAddRoute(builder, fbs_path)
    FbsRoute.RouteAddRouteTime(builder, time)
    FbsRoute.RouteAddRouteDistance(builder, distance)
    FbsRoute.RouteAddRouteId(builder, fbs_route_id)
    FbsRoute.RouteAddHasClosures(builder, closures)
    FbsRoute.RouteAddHasDeadJams(builder, dead_jams)
    FbsRoute.RouteAddHasTollRoads(builder, toll_roads)
    if fbs_leg:
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
