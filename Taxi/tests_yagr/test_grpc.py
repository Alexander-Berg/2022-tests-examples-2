# pylint: disable=import-error,too-many-lines

import datetime

import pytest
import grpc

from fleet_tracking_system.proto import fts_pb2_grpc as receiver_grpc
from fleet_tracking_system.proto import fts_pb2 as receiver
from fleet_tracking_system.proto import geometry_pb2 as geometry

from geobus_tools import (
    geobus,
)  # noqa: F401 C5521 from tests_plugins import utils


@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_grpc_position_store_wrong_pipeline(
        grpc_channel, redis_store, testpoint,
):

    receiver_stub = receiver_grpc.FleetTrackingSystemStub(grpc_channel)
    data = geometry.IncomingSignal()
    data.timestamp = 1000
    data.source = 'test'
    positions_request = receiver.SendPositionsRequest()
    positions_request.pipeline = 'non_existent'
    positions_request.uuid = 'berty_qwerty'
    positions_request.positions.append(data)
    try:
        request = receiver_stub.SendPositions(positions_request)
        await request
    except Exception as e:
        assert e.code() == grpc.StatusCode.INVALID_ARGUMENT
