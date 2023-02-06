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
import geobus.fbs.EdgePosition as FbsEdgePosition
import geobus.fbs.EdgePositions as FbsEdgePositions
import geobus.fbs.GeoPosition as FbsGeoPosition
import geobus.fbs.Message as FbsMessage
import geobus.fbs.Position as FbsPosition
import geobus.fbs.Positions as FbsPositions
import geobus.fbs.ProbableEdgePosition as FbsProbableEdgePosition
import geobus.fbs.channel_position_v2.Position as FbsPositionV2
import geobus.fbs.channel_position_v2.Positions as FbsPositionsV2
import geobus.fbs.channel_edge_position_v2.EdgePosition as FbsEdgePositionV2
import geobus.fbs.channel_edge_position_v2.EdgePositions as FbsEdgePositionsV2
import geobus.fbs.channel_edge_position_v2.ProbableEdgePosition as FbsProbableEdgePositionV2
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


def _convert_drivers_to_canonical(drivers):
    """
    Convert shortcut form drivers
    [
        {
            'driver_id': 'dbid_uuid',
            'edge_id': 255,
            'position': [55, 37],
            'position_on_edge': 1.0,
            'probability': 1.0,
            'speed': 300.0,
            'timestamp': 1500000,
            'log_likelihood': -3.0,
        },
    ]
    to canonical form
    [
        {
            'driver_id': 'dbid_uuid',
            'positions': [
                {
                    'position': [55, 37],
                    'edge_id': 255,
                    'position_on_edge': 1.0,
                    'probability': 1.0,
                    'speed': 300.0,
                    'timestamp': 1500000,
                    'log_likelihood': -3.0,
                },
            ]
        },
    ]
    :param drivers:
    :return: canonical form of drivers list
    """
    driver_fields = ['driver_id', 'timestamp']
    position_fields = [
        'edge_id',
        'position',
        'position_on_edge',
        'probability',
        'speed',
        'direction',
        'log_likelihood',
    ]

    new_drivers = []
    for driver in drivers:
        new_driver = {
            field: driver[field] for field in driver_fields if field in driver
        }
        new_driver['positions'] = [
            {
                field: driver[field]
                for field in position_fields
                if field in driver
            },
        ]
        new_drivers.append(new_driver)

    return new_drivers


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


# Call StartXXXDriverIdVector before calling this method
def _fill_and_finish_driver_id(builder, driver_id):
    driver_id_raw = bytearray(driver_id, 'ascii')
    for i in reversed(driver_id_raw):
        builder.PrependByte(i)
    return builder.EndVector(len(driver_id_raw))


## ================ Edge positions V2 channel


def serialize_edge_positions_v2(drivers, now):
    data = serialize_edge_positions_v2_message_data(drivers)

    return gen_gzipped_channel_message(
        data, now, FbsProtocol.Protocol.EdgePositionsV1,
    )


def serialize_edge_positions_v2_message_data(drivers):
    if drivers and 'position' in drivers[0]:
        drivers = _convert_drivers_to_canonical(drivers)

    builder = flatbuffers.Builder(0)

    positions = [_gen_edge_position_v2(builder, driver) for driver in drivers]

    positions_count = len(positions)
    FbsEdgePositionsV2.EdgePositionsStartPositionsVector(
        builder, positions_count,
    )
    for pos in reversed(positions):
        builder.PrependUOffsetTRelative(pos)
    positions_offset = builder.EndVector(positions_count)

    FbsEdgePositionsV2.EdgePositionsStart(builder)
    FbsEdgePositionsV2.EdgePositionsAddPositions(builder, positions_offset)
    obj = FbsEdgePositionsV2.EdgePositionsEnd(builder)

    builder.Finish(obj)

    return _gzip_builder(builder)


def _gen_edge_position_v2(builder, driver):
    driver_id = driver['driver_id']
    FbsEdgePositionV2.EdgePositionStartIdVector(builder, len(driver_id))
    driver_id_offset = _fill_and_finish_driver_id(builder, driver_id)

    probable_positions = [
        _gen_probable_edge_position_v2(builder, probable_edge_position)
        for probable_edge_position in driver['positions']
    ]
    FbsEdgePositionV2.EdgePositionStartPossiblePositionsVector(
        builder, len(probable_positions),
    )
    for pos in reversed(probable_positions):
        builder.PrependUOffsetTRelative(pos)
    probable_positions_offset = builder.EndVector(len(probable_positions))

    FbsEdgePositionV2.EdgePositionStart(builder)
    FbsEdgePositionV2.EdgePositionAddId(builder, driver_id_offset)
    FbsEdgePositionV2.EdgePositionAddTimestamp(builder, driver['timestamp'])
    FbsEdgePositionV2.EdgePositionAddPossiblePositions(
        builder, probable_positions_offset,
    )
    return FbsEdgePositionV2.EdgePositionEnd(builder)


def _gen_probable_edge_position_v2(builder, pos):
    FbsProbableEdgePositionV2.ProbableEdgePositionStart(builder)

    FbsProbableEdgePositionV2.ProbableEdgePositionAddPosition(
        builder, _serialize_geometry_position(builder, pos['position']),
    )

    edge_id = pos.get('edge_id', 255)
    displacement = pos.get('position_on_edge', 0.5)
    FbsProbableEdgePositionV2.ProbableEdgePositionAddEdgePosition(
        builder, gen_position_on_edge(builder, edge_id, displacement),
    )

    direction = pos.get('direction', 0)
    FbsProbableEdgePositionV2.ProbableEdgePositionAddDirection(
        builder, direction,
    )

    probability = int(pos.get('probability', 1.0) * 0xFF)
    FbsProbableEdgePositionV2.ProbableEdgePositionAddProbability(
        builder, probability,
    )

    log_likelihood = pos.get('log_likelihood', 0)
    FbsProbableEdgePositionV2.ProbableEdgePositionAddLogLikelihood(
        builder, log_likelihood,
    )

    speed = pos.get('speed', 0)
    FbsProbableEdgePositionV2.ProbableEdgePositionAddSpeed(builder, speed)

    return FbsProbableEdgePositionV2.ProbableEdgePositionEnd(builder)


def _gen_fbs_edge_positions(builder, driver):
    driver_id = driver['driver_id']
    timestamp = driver['timestamp']

    driver_id_offset = builder.CreateString(driver_id)

    fbs_probable_positions = [
        _gen_fbs_probable_edge_position(builder, probable_edge_position)
        for probable_edge_position in driver['positions']
    ]
    FbsEdgePosition.EdgePositionStartProbablePositionsVector(
        builder, len(fbs_probable_positions),
    )
    for pos in reversed(fbs_probable_positions):
        builder.PrependUOffsetTRelative(pos)
    options_offset = builder.EndVector(len(fbs_probable_positions))

    FbsEdgePosition.EdgePositionStart(builder)
    FbsEdgePosition.EdgePositionAddId(builder, driver_id_offset)
    FbsEdgePosition.EdgePositionAddTimestamp(builder, timestamp)
    FbsEdgePosition.EdgePositionAddProbablePositions(builder, options_offset)
    return FbsEdgePosition.EdgePositionEnd(builder)


def _gen_fbs_probable_edge_position(builder, probable_edge_position):
    FbsProbableEdgePosition.ProbableEdgePositionStart(builder)
    direction = probable_edge_position.get('direction', 0)
    log_likelihood = probable_edge_position.get('log_likelihood', 0)
    speed = int(probable_edge_position.get('speed', 300) / 300 * 0xFFFF)
    probability = int(probable_edge_position.get('probability', 1.0) * 0xFF)
    edge_id = probable_edge_position.get('edge_id', 255)
    displacement = probable_edge_position.get('position_on_edge', 0.5)
    longitude = _int_coordinate(probable_edge_position['position'][0])
    latitude = _int_coordinate(probable_edge_position['position'][1])

    FbsProbableEdgePosition.ProbableEdgePositionAddPosition(
        builder,
        FbsGeoPosition.CreateGeoPosition(builder, longitude, latitude),
    )
    FbsProbableEdgePosition.ProbableEdgePositionAddEdgePosition(
        builder, gen_position_on_edge(builder, edge_id, displacement),
    )  # edge displacement (encoded) and edge persistent id
    FbsProbableEdgePosition.ProbableEdgePositionAddDirection(
        builder, direction,
    )
    FbsProbableEdgePosition.ProbableEdgePositionAddProbability(
        builder, probability,
    )  # encoded probability
    FbsProbableEdgePosition.ProbableEdgePositionAddLogLikelihood(
        builder, log_likelihood,
    )  # ignore it,
    FbsProbableEdgePosition.ProbableEdgePositionAddSpeed(
        builder, speed,
    )  # speed, encoded

    return FbsProbableEdgePosition.ProbableEdgePositionEnd(builder)


def deserialize_edge_positions(message):
    """
    Deserialize EdgePositions message to dict like this:
    {
        timestamp: 15000000,
        positions:
            [
                {
                    'driver_id': 'dbid_uuid',
                    'timestamp': 1500000,
                    'positions': [
                        {
                            'position': [55, 37],
                            'edge_id': 255,
                            'position_on_edge': 1.0,
                            'probability': 0.6,
                            'speed': 300.0,
                            'log_likelihood': -1.5
                        },
                        {
                            'position': [52, 40],
                            'edge_id': 25,
                            'position_on_edge': 0.8,
                            'probability': 0.4,
                            'speed': 300.0,
                            'log_likelihood': -3.0
                        }
                    ]
                },
            ]
    }
    """
    data = bytearray(_gzip_decompress(message))
    fbs_positions = FbsEdgePositions.EdgePositions.GetRootAsEdgePositions(
        data, 0,
    )
    # timestamp = fbs_positions.Timestamp()
    positions_count = fbs_positions.PositionsLength()
    positions = [
        _deserialize_fbs_edge_position(fbs_positions.Positions(i))
        for i in range(positions_count)
    ]
    timestamp = fbs_positions.Timestamp()
    return {'timestamp': timestamp, 'positions': positions}


def _deserialize_fbs_edge_position(fbs_edge_position):
    driver_id = fbs_edge_position.Id().decode()
    timestamp = fbs_edge_position.Timestamp()
    positions = fbs_edge_position.ProbablePositionsLength()
    probable_positions = [
        _deserialize_probable_edge_position(
            fbs_edge_position.ProbablePositions(i),
        )
        for i in range(positions)
    ]
    return {
        'driver_id': driver_id,
        'timestamp': timestamp,
        'positions': probable_positions,
    }


def _deserialize_probable_edge_position(fbs_probable_edge_position):
    point = fbs_probable_edge_position.Position()
    longitude = point.Longitude() / 1000000
    latitude = point.Latitude() / 1000000
    poe = fbs_probable_edge_position.EdgePosition()
    edge_id = poe.PersistentEdge()
    displacement = poe.EdgeDisplacement() / 0xFFFF
    direction = fbs_probable_edge_position.Direction()
    probability = fbs_probable_edge_position.Probability() / 0xFF
    # likelyhood = fbs_probable_edge_position.LogLikelihood()
    log_likelihood = fbs_probable_edge_position.LogLikelihood()
    speed = fbs_probable_edge_position.Speed() * 300 / 0xFFFF
    return {
        'position': [longitude, latitude],
        'direction': direction,
        'speed': speed,
        'probability': probability,
        'edge_id': edge_id,
        'position_on_edge': displacement,
        'log_likelihood': log_likelihood,
    }


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
