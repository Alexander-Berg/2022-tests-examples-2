# pylint: disable=import-error
import flatbuffers
import pointslist_entry.fbs.PointProperty as PointProperty
import pointslist_entry.fbs.PointslistEntry as PointslistEntry

import tests_driver_route_watcher.position_fbs as PositionFbs


def to_point_list(points, compact=False):
    ret = [{'point': point} for point in points]
    if not compact:
        ret = [{**x, 'wait_time': 0, 'park_time': 0} for x in ret]
    return ret


def serialize_point_property(builder, point_property):
    order_id = point_property.get('order_id')
    point_id = point_property.get('point_id')
    wait_time = point_property.get('wait_time', 0)
    park_time = point_property.get('park_time', 0)
    fbs_order_id = (
        builder.CreateString(order_id) if order_id is not None else None
    )
    fbs_point_id = (
        builder.CreateString(point_id) if point_id is not None else None
    )

    PointProperty.PointPropertyStart(builder)
    PointProperty.PointPropertyAddWaitTime(builder, wait_time)
    PointProperty.PointPropertyAddParkTime(builder, park_time)
    if fbs_order_id:
        PointProperty.PointPropertyAddOrderId(builder, fbs_order_id)
    if fbs_point_id:
        PointProperty.PointPropertyAddPointId(builder, fbs_point_id)
    return PointProperty.PointPropertyEnd(builder)


def deserialize_point_property(fbs_property):
    fbs_order_id = fbs_property.OrderId()
    fbs_point_id = fbs_property.PointId()
    ret = {
        'wait_time': fbs_property.WaitTime(),
        'park_time': fbs_property.ParkTime(),
    }
    if fbs_order_id:
        ret.update({'order_id': fbs_order_id.decode()})
    if fbs_point_id:
        ret.update({'point_id': fbs_point_id.decode()})
    return ret


def serialize_pointslist_fbs(builder, points):
    PointslistEntry.PointslistEntryStartPointsVector(builder, len(points))
    for point in reversed(points):
        PositionFbs.serialize_position(builder, point['point'])
    points_fbs = builder.EndVector(len(points))

    fbs_properties = [serialize_point_property(builder, x) for x in points]
    PointslistEntry.PointslistEntryStartPropertiesVector(builder, len(points))
    for fbs_property in reversed(fbs_properties):
        builder.PrependUOffsetTRelative(fbs_property)
    fbs_properties = builder.EndVector(len(points))

    PointslistEntry.PointslistEntryStart(builder)
    PointslistEntry.PointslistEntryAddPoints(builder, points_fbs)
    if fbs_properties:
        PointslistEntry.PointslistEntryAddProperties(builder, fbs_properties)
    return PointslistEntry.PointslistEntryEnd(builder)


def serialize_pointslist(points):
    builder = flatbuffers.Builder(0)
    obj = serialize_pointslist_fbs(builder, points)
    builder.Finish(obj)
    return bytes(builder.Output())


def deserialize_pointslist_fbs(fbs_entry):
    if fbs_entry is None:
        return None

    points = [
        PositionFbs.deserialize_position(fbs_entry.Points(i))
        for i in range(fbs_entry.PointsLength())
    ]
    properties = [
        deserialize_point_property(fbs_entry.Properties(i))
        for i in range(fbs_entry.PropertiesLength())
    ]
    ret = [{'point': point} for point in points]
    if properties:
        assert len(points) == len(properties)
        for i in range(len(points)):
            ret[i].update(properties[i])
    return ret


def deserialize_pointslist(data):
    fbs_entry = PointslistEntry.PointslistEntry.GetRootAsPointslistEntry(
        data, 0,
    )
    return deserialize_pointslist_fbs(fbs_entry)
