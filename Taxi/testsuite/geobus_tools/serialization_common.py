# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module,wildcard-import,import-only-modules
# flake8: noqa F501 F401 F841 F821
import datetime
import math

import geometry.fbs.Position as FbsGeometryPosition
import geobus.fbs.PositionOnEdge as FbsPositionOnEdge


def _round_away_from_zero(x):
    a = abs(x)
    r = math.floor(a) + math.floor(2 * (a % 1))
    return r if x >= 0.0 else -r


def serialize_string(data, builder):
    return builder.CreateString(data)


def serialize_int(data, builder):
    return data


def serialize_double(data, builder):
    return data


def serialize_distance_int(data, builder):
    return int(data)


def serialize_dbid_uuid(driver_id, builder, start_method):
    start_method(builder, len(driver_id))
    driver_id_raw = bytearray(driver_id, 'ascii')
    for i in reversed(driver_id_raw):
        builder.PrependByte(i)
    return builder.EndVector(len(driver_id_raw))


def _int_coordinate(value):
    return int(_round_away_from_zero(value * 1000000))


def serialize_position(position, builder):
    assert position is not None
    return FbsGeometryPosition.CreatePosition(
        builder, _int_coordinate(position[0]), _int_coordinate(position[1]),
    )


def serialize_position_as_obj(position, builder):
    assert position is not None
    print(position)
    return FbsGeometryPosition.CreatePosition(
        builder,
        _int_coordinate(position['lon']),
        _int_coordinate(position['lat']),
    )


def serialize_seconds_int(data, builder):
    return int(data)


def serialize_time_point_in_ms(time_point, builder):
    if isinstance(time_point, int):
        return time_point

    if isinstance(time_point, datetime.datetime):
        # Who the hell said that working with datetime in python is convinient?
        epoch = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
        td = time_point - epoch
        # convert to milliseconds
        return int(td / datetime.timedelta(milliseconds=1))

    raise NotImplementedError(
        (
            'Converting from {} to milliseconds(int)' 'is not supported yet'
        ).format(time_point),
    )


def serialize_time_point_in_mcs(time_point, builder):
    if isinstance(time_point, int):
        return time_point

    if isinstance(time_point, datetime.datetime):
        # Who the hell said that working with datetime in python is convinient?
        epoch = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
        td = time_point - epoch
        # convert to microseconds
        return int(td / datetime.timedelta(mocroseconds=1))

    raise NotImplementedError(
        (
            'Converting from {} to microseconds(int)' 'is not supported yet'
        ).format(time_point),
    )


def serialize_double_in_ubyte(data, builder):
    return int(data * 255)


def serialize_byte_array(raw_data, builder, start_method):
    start_method(builder, len(raw_data))
    data = bytearray(raw_data, 'ascii')
    for i in reversed(data):
        builder.PrependByte(i)
    return builder.EndVector(len(raw_data))


def deserialize_distance_int(fbs_data):
    return int(fbs_data)


def deserialize_string(fbs_data):
    return fbs_data.decode()


def deserialize_int(fbs_data):
    return int(fbs_data)


def deserialize_double(fbs_data):
    return float(fbs_data)


def deserialize_dbid_uuid(fbs_data):
    return fbs_data.tostring().decode()


def deserialize_byte_array(fbs_data):
    return fbs_data.tostring().decode()


def deserialize_position(fbs_data):
    return [fbs_data.Longitude() / 1e6, fbs_data.Latitude() / 1e6]


def deserialize_seconds_int(fbs_data):
    return int(fbs_data)


def deserialize_time_point_in_ms(fbs_data):
    dev = fbs_data % 1000
    mod = fbs_data // 1000
    time = datetime.datetime.utcfromtimestamp(mod)
    time = datetime.datetime(
        time.year,
        time.month,
        time.day,
        time.hour,
        time.minute,
        time.second,
        dev * 1000,
    )
    return time


def deserialize_time_point_in_mcs(fbs_data):
    dev = fbs_data % 1000000
    mod = fbs_data // 1000000
    time = datetime.datetime.utcfromtimestamp(mod)
    time = datetime.datetime(
        time.year,
        time.month,
        time.day,
        time.hour,
        time.minute,
        time.second,
        dev * 1000000,
    )
    return time


def deserialize_timepoint_in_sec(fbs_data):
    return datetime.datetime.utcfromtimestamp(fbs_data)


def deserialize_double_in_ubyte(fbs_data):
    return fbs_data / 255.0


def gen_position_on_edge(builder, edge_id, displacement):
    """
    @param edge_id - graph persistent edge_id
    @param displacement - position on edge [0, 1.0]
    """
    encoded_displacement = int(displacement * 0xFFFF)
    return FbsPositionOnEdge.CreatePositionOnEdge(
        builder, edge_id, encoded_displacement,
    )
