# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from fts_client_testsuite_plugins import *  # noqa: F403 F401

import asyncio
import grpc
import pytest
import sys
import logging

from fleet_tracking_system.proto import fts_pb2_grpc as fts_grpc
from fleet_tracking_system.proto import fts_pb2 as fts
from google.protobuf import empty_pb2

logger = logging.getLogger(__name__)

FTS_GRPC_ADDRESS = 'localhost:50051'
FTS_CHANNEL_BACKOFF_SECONDS = 0.1


class FtsServiceMock(fts_grpc.FleetTrackingSystemServicer):
    class Handler:
        def __init__(self, user_handler):
            self._handler = user_handler
            self.times_called = 0

        def __call__(self, request, context):
            self.times_called += 1
            return self._handler(request, context)

    def __init__(self) -> None:
        super().__init__()
        self._grpc_server = None
        self._version = '1'
        self._on_version_changed = asyncio.Event()
        self._mock_send_positions = lambda r, c: empty_pb2.Empty()

    async def stop(self) -> None:
        if self._grpc_server:
            await self._grpc_server.stop(grace=None)
            self._grpc_server = None

    async def restart(self) -> None:
        await self.stop()

        self._grpc_server = grpc.aio.server()
        assert self._grpc_server

        self._grpc_server.add_insecure_port(FTS_GRPC_ADDRESS)
        fts_grpc.add_FleetTrackingSystemServicer_to_server(
            self, self._grpc_server,
        )
        await self._grpc_server.start()

        # If scout mock was purposely shut down during a previous test
        # (to check exa fallback behavior), scout grpc channel will start
        # asynchronous reconnection attempts, see
        # https://github.com/grpc/grpc/blob/master/doc/connection-backoff.md
        #
        # Until reconnection succeeds, all RPCs from exa to scout will fail.
        # So we need to wait for reconnection before exa starts making
        # requests to scout mock.
        max_estimated_reconnection_time_seconds = (
            FTS_CHANNEL_BACKOFF_SECONDS + 1.0
        )
        await asyncio.sleep(max_estimated_reconnection_time_seconds)

    def mock_send_positions(self, user_handler):
        """ Use this method as decorator to mock SendPositions response"""
        handler = FtsServiceMock.Handler(user_handler)
        self._mock_send_positions = handler

        return handler

    async def SendPositions(self, request, context):
        # check that TVM is enable. leave only TVM headers and check that length of
        # resulting array is > 0. A very python way to do this. See how readable it is :)
        assert [
            x
            for x in context.invocation_metadata()
            if x[0] == 'x-ya-service-ticket'
        ]
        return self._mock_send_positions(request, context)


@pytest.fixture(name='fts_mock')
async def _fts_mock():
    mock = FtsServiceMock()
    await mock.restart()
    logger.info('FTS mock restarted')

    try:
        yield mock
    finally:
        await mock.stop()
        logger.info('FTS mock stopped')
