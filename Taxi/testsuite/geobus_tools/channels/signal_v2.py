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
import geobus.fbs.Position as FbsPosition
import geobus.fbs.Positions as FbsPositions
import geobus.fbs.ProbableEdgePosition as FbsProbableEdgePosition
import geobus.fbs.SignalSource as SignalSource
import geobus.fbs.TrackPoint as FbsTrackPoint
import geobus.fbs.SignalV2 as FbsSignalV2
import geobus.fbs.SignalV2Source as FbsSignalV2Source
import geobus.fbs.SignalV2Message as SignalV2Message
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


## ================ signal v2 channel

signal_v2_source_to_fbs_enum_constant = {
    'AndroidGps': FbsSignalV2Source.SignalV2Source.AndroidGps,
    'AndroidNetwork': FbsSignalV2Source.SignalV2Source.AndroidNetwork,
    'AndroidFused': FbsSignalV2Source.SignalV2Source.AndroidFused,
    'AndroidPassive': FbsSignalV2Source.SignalV2Source.AndroidPassive,
    'YandexLbsWifi': FbsSignalV2Source.SignalV2Source.YandexLbsWifi,
    'YandexLbsGsm': FbsSignalV2Source.SignalV2Source.YandexLbsGsm,
    'YandexLbsIp': FbsSignalV2Source.SignalV2Source.YandexLbsIp,
    'YandexMapkit': FbsSignalV2Source.SignalV2Source.YandexMapkit,
    'YandexNavi': FbsSignalV2Source.SignalV2Source.YandexNavi,
    'Unknown': FbsSignalV2Source.SignalV2Source.Unknown,
    'Verified': FbsSignalV2Source.SignalV2Source.Verified,
    'Realtime': FbsSignalV2Source.SignalV2Source.Realtime,
    'Camera': FbsSignalV2Source.SignalV2Source.Camera,
}


def _gen_signal_v2(builder, driver_info):
    driver_id = driver_info['driver_id']
    FbsSignalV2.SignalV2StartDriverIdVector(builder, len(driver_id))
    driver_id_offset = _fill_and_finish_driver_id(builder, driver_id)

    FbsSignalV2.SignalV2Start(builder)
    FbsSignalV2.SignalV2AddDriverId(builder, driver_id_offset)

    position_offset = _serialize_geometry_position(
        builder, driver_info['position'],
    )
    FbsSignalV2.SignalV2AddPosition(builder, position_offset)
    FbsSignalV2.SignalV2AddUnixTime(builder, driver_info['unix_time'])
    FbsSignalV2.SignalV2AddSource(
        builder, signal_v2_source_to_fbs_enum_constant[driver_info['source']],
    )

    if 'altitude' in driver_info:
        FbsSignalV2.SignalV2AddAltitude(builder, driver_info['altitude'])
    if 'direction' in driver_info:
        FbsSignalV2.SignalV2AddDirection(builder, driver_info['direction'])
    if 'speed' in driver_info:
        FbsSignalV2.SignalV2AddSpeed(builder, driver_info['speed'])
    if 'accuracy' in driver_info:
        FbsSignalV2.SignalV2AddAccuracy(builder, driver_info['accuracy'])

    return FbsSignalV2.SignalV2End(builder)


def serialize_signal_v2_message_data(drivers):
    """Return serialized driver positions in geobus format

    @param drivers: list of dicts. see example
    @param now: datetime timestamp
    @return: fbs-encoded buffer
    @example
    drivers = [
        {
            'driver_id': 'dbid_uuid_0',
            'position': [37, 55],
            'unix_time': 100500,
            'source': AndroidGps,
            'altitude': 1
            'direction': 45,
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

    positions_offsets = [_gen_signal_v2(builder, driver) for driver in drivers]

    positions_count = len(positions_offsets)
    SignalV2Message.SignalV2MessageStartPayloadVector(builder, positions_count)
    for pos in reversed(positions_offsets):
        builder.PrependUOffsetTRelative(pos)
    payload_offset = builder.EndVector(positions_count)

    SignalV2Message.SignalV2MessageStart(builder)
    SignalV2Message.SignalV2MessageAddPayload(builder, payload_offset)
    obj = SignalV2Message.SignalV2MessageEnd(builder)

    builder.Finish(obj)

    return _gzip_builder(builder)


def serialize_signal_v2(drivers, now):
    data = serialize_signal_v2_message_data(drivers)

    result = gen_gzipped_channel_message(
        data, now, FbsProtocol.Protocol.PositionsV2,
    )
    return result


def _gen_signal(builder, signal):
    GeoPositionSignal.GeoPositionSignalStart(builder)
    GeoPositionSignal.GeoPositionSignalAddPos(
        builder,
        FbsGeometryPosition.CreatePosition(
            builder, signal['position'][0], signal['position'][1],
        ),
    )
    GeoPositionSignal.GeoPositionSignalAddSource(builder, signal['source'])
    GeoPositionSignal.GeoPositionSignalAddAltitude(builder, signal['altitude'])
    GeoPositionSignal.GeoPositionSignalAddUnixTimestamp(
        builder, signal['unix_timestamp'],
    )
    GeoPositionSignal.GeoPositionSignalAddRtcTimestamp(
        builder, signal['rtc_timestamp'],
    )
    GeoPositionSignal.GeoPositionSignalAddDirection(
        builder, signal['direction'],
    )
    GeoPositionSignal.GeoPositionSignalAddSpeed(builder, signal['speed'])
    GeoPositionSignal.GeoPositionSignalAddAccuracy(builder, signal['accuracy'])
    return GeoPositionSignal.GeoPositionSignalEnd(builder)


def deserialize_signal_v2_message(binary_data):
    # first we should decompress the message (if it is needed)
    fbs_message = FbsMessage.Message.GetRootAsMessage(binary_data, 0)
    potentially_compressed_data = fbs_message.DataAsNumpy()
    data_format = fbs_message.DataFormat()
    if data_format == FbsDataFormat.DataFormat.Gzip:
        decompressed_data = bytearray(
            _gzip_decompress(potentially_compressed_data),
        )
    if data_format == FbsDataFormat.DataFormat.NoCompression:
        decompressed_data = potentially_compressed_data

    positions = []
    msg = SignalV2Message.SignalV2Message.GetRootAsSignalV2Message(
        decompressed_data, 0,
    )
    for j in range(msg.PayloadLength()):
        position_fbs = msg.Payload(j)
        position = {}
        position['driver_id'] = (
            position_fbs.DriverIdAsNumpy().tostring().decode()
        )
        position['position'] = [
            position_fbs.Position().Longitude() / 1e6,
            position_fbs.Position().Latitude() / 1e6,
        ]
        position['unix_time'] = position_fbs.UnixTime()
        position['source'] = position_fbs.Source()
        position['altitude'] = position_fbs.Altitude()
        position['direction'] = position_fbs.Direction()
        position['speed'] = position_fbs.Speed()
        position['accuracy'] = position_fbs.Accuracy()
        positions.append(position)

    return positions


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
