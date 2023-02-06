# pylint: disable=import-error,invalid-name,useless-object-inheritance
# pylint: disable=undefined-variable,unused-variable,too-many-lines
# pylint: disable=no-name-in-module
# pylint: disable=C5521
# flake8: noqa F501 F401 F841 F821 F403
import gzip
import io
import math

import flatbuffers
import geometry.fbs.Position as FbsGeometryPosition
import pytest

import geobus.fbs.DataFormat as FbsDataFormat
import geobus.fbs.GeoPosition as FbsGeoPosition
import geobus.fbs.GeoPositionSignal as GeoPositionSignal
import geobus.fbs.Message as FbsMessage
import geobus.fbs.MultiGeoPositionSignal as MultiGeoPositionSignal
import geobus.fbs.MultiGeoPositionSignalsMessage as MultiGeoPositionSignalsMessage
import geobus.fbs.Position as FbsPosition
import geobus.fbs.Positions as FbsPositions
import geobus.fbs.SignalSource as SignalSource
import geobus.fbs.TrackPoint as FbsTrackPoint
import geobus.fbs.channel_position_v2.Position as FbsPositionV2
import geobus.fbs.channel_position_v2.Positions as FbsPositionsV2
import geobus.fbs.Protocol as FbsProtocol
from tests_plugins import utils
from testsuite.utils import callinfo

from ..serialization_common import (
    gen_position_on_edge,
    _int_coordinate,
)  # pylint: disable=C5521
from ..helpers import (
    gen_gzipped_channel_message,
    parse_and_decompress_message,
    gzip_builder,
)

# ==== Common functions


def _serialize_geometry_position(builder, position):
    assert position is not None
    return FbsGeometryPosition.CreatePosition(
        builder, _int_coordinate(position[0]), _int_coordinate(position[1]),
    )


def _deserialize_geometry_position(fbs_position):
    assert fbs_position is not None
    longitude = fbs_position.Longitude() / 1e6
    latitude = fbs_position.Latitude() / 1e6

    return [longitude, latitude]


def _serialize_geo_position_signal(builder, signal):
    assert signal is not None
    GeoPositionSignal.GeoPositionSignalStart(builder)
    GeoPositionSignal.GeoPositionSignalAddPos(
        builder, _serialize_geometry_position(builder, signal['position']),
    )
    GeoPositionSignal.GeoPositionSignalAddSource(
        builder, signal.get('source', SignalSource.SignalSource.AndroidGps),
    )
    GeoPositionSignal.GeoPositionSignalAddAltitude(
        builder, signal.get('altitude', 0),
    )
    GeoPositionSignal.GeoPositionSignalAddUnixTimestamp(
        builder, signal['unix_timestamp'],
    )
    GeoPositionSignal.GeoPositionSignalAddRtcTimestamp(
        builder, signal.get('rtc_timestamp', signal['unix_timestamp']),
    )
    GeoPositionSignal.GeoPositionSignalAddDirection(
        builder, signal['direction'],
    )
    GeoPositionSignal.GeoPositionSignalAddSpeed(builder, signal['speed'])
    GeoPositionSignal.GeoPositionSignalAddAccuracy(builder, signal['accuracy'])
    return GeoPositionSignal.GeoPositionSignalEnd(builder)


def _deserialize_geo_position_signal(signal):
    assert signal is not None
    point = _deserialize_geometry_position(signal.Pos())
    unix_timestamp = signal.UnixTimestamp()
    rtc_timestamp = signal.RtcTimestamp()
    direction = signal.Direction()
    speed = signal.Speed()
    accuracy = signal.Accuracy()
    source = signal.Source()

    return {
        'position': point,
        'direction': direction,
        'unix_timestamp': unix_timestamp,
        'rtc_timestamp': rtc_timestamp,
        'speed': speed,
        'accuracy': accuracy,
        'source': source,
    }


# Call StartXXXDriverIdVector before calling this method
def _fill_and_finish_driver_id(builder, driver_id):
    driver_id_raw = bytearray(driver_id, 'ascii')
    for i in reversed(driver_id_raw):
        builder.PrependByte(i)
    return builder.EndVector(len(driver_id_raw))


## ============== Positions V2 channel


def _deserialize_position_v2(position):
    driver_id_chars = []
    for i in range(position.IdLength()):
        driver_id_chars.append(chr(position.Id(i)))
    driver_id = ''.join(driver_id_chars)

    geo_signal = _deserialize_geo_position_signal(position.Point())

    # in this channel we convert timestamp to seconds precision
    geo_signal['timestamp'] = int(geo_signal['unix_timestamp'] / 1000)

    # merge two
    result = geo_signal
    result['driver_id'] = driver_id

    return result


def _deserialize_positions_v2_message_data(message):
    fbs_positions = FbsPositionsV2.Positions.GetRootAsPositions(message, 0)
    positions_count = fbs_positions.PositionsLength()
    positions = [
        _deserialize_position_v2(fbs_positions.Positions(i))
        for i in range(positions_count)
    ]
    return {'positions': positions}


def _deserialize_positions_v2_message_data_gzipped(message):
    data = bytearray(_gzip_decompress(message))
    return _deserialize_positions_v2_message_data(data)


def deserialize_positions_v2(message):
    """Return deserialized driver positions from geobus positions channel,
       version 2

    @param message: message to decode
    drivers = [
        {
            'driver_id': 'dbid_uuid_0',
            'position': [37, 55],
            'direction': 45,
            'timestamp': 100500,
            'speed': 42,
            'accuracy': 0,
        }
    ]
    """
    fbs_message = FbsMessage.Message.GetRootAsMessage(message, 0)

    fbs_data = fbs_message.DataAsNumpy()
    fbs_data_format = fbs_message.DataFormat()
    if fbs_data_format == FbsDataFormat.DataFormat.Gzip:
        return _deserialize_positions_v2_message_data_gzipped(fbs_data)
    if fbs_data_format == FbsDataFormat.DataFormat.NoCompression:
        return _deserialize_positions_v2_message_data(fbs_data)
    raise Exception('Invalid fbs_data_format')


def _gen_position_v2(builder, driver_info):
    driver_id = driver_info['driver_id']
    FbsPositionV2.PositionStartIdVector(builder, len(driver_id))
    driver_id_offset = _fill_and_finish_driver_id(builder, driver_id)

    # Force source to Gps
    driver_info_copy = dict(driver_info)
    driver_info_copy['source'] = SignalSource.SignalSource.AndroidGps
    # and rename timestamp
    driver_info_copy['unix_timestamp'] = driver_info_copy['timestamp'] * 1000
    point_offset = _serialize_geo_position_signal(builder, driver_info_copy)

    FbsPositionV2.PositionStart(builder)
    FbsPositionV2.PositionAddId(builder, driver_id_offset)
    FbsPositionV2.PositionAddPoint(builder, point_offset)
    return FbsPositionV2.PositionEnd(builder)


def serialize_positions_v2_message_data(drivers):
    """Return serialized driver positions in geobus format

    @param drivers: list of dicts. see example
    @param now: datetime timestamp
    @return: fbs-encoded buffer
    @example
    drivers = [
        {
            'driver_id': 'dbid_uuid_0',
            'position': [37, 55],
            'direction': 45,
            'timestamp': 100500,
            'speed': 42,
            'accuracy': 0,
        }
    ]
    """
    builder = flatbuffers.Builder(0)
    # Our version of python flatbuffers doesn't support forceDefaults mode
    # Which is required for this channel to operate.
    # Do not pass '0' as values for members
    # builder.forceDefaults = True

    positions = [_gen_position_v2(builder, driver) for driver in drivers]

    positions_count = len(positions)
    FbsPositionsV2.PositionsStartPositionsVector(builder, positions_count)
    for pos in reversed(positions):
        builder.PrependUOffsetTRelative(pos)
    positions_offset = builder.EndVector(positions_count)

    FbsPositionsV2.PositionsStart(builder)
    FbsPositionsV2.PositionsAddPositions(builder, positions_offset)
    obj = FbsPositions.PositionsEnd(builder)

    builder.Finish(obj)

    return _gzip_builder(builder)


def serialize_positions_v2(drivers, now):
    data = serialize_positions_v2_message_data(drivers)

    result = gen_gzipped_channel_message(
        data, now, FbsProtocol.Protocol.PositionsV1,
    )
    return result


def _gzip_builder(builder):
    object_bytes = bytes(builder.Output())

    data = io.BytesIO()
    with gzip.GzipFile(mode='wb', fileobj=data) as zfle:
        zfle.write(object_bytes)
    return data.getvalue()


def _gzip_decompress(message):
    data = io.BytesIO(message)
    with gzip.GzipFile(mode='rb', fileobj=data) as zfle:
        return zfle.read()
