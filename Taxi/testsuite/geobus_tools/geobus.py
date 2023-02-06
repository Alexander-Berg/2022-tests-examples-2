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

from tests_plugins import utils
from testsuite.utils import callinfo

from .channels import timelefts
from .channels import positions
from .channels.positions import serialize_positions_v2
from .channels.positions import deserialize_positions_v2
from .channels.edge_positions import serialize_edge_positions_v2
from .channels.signal_v2 import serialize_signal_v2
from .channels.signal_v2 import deserialize_signal_v2_message
from .channels.signal_v2 import SignalSource
from .channels.universal_signals import (
    serialize_message as serialize_universal_signal,
)
from .channels.universal_signals import (
    deserialize_message as deserialize_universal_signal,
)


@pytest.fixture
def geobus_publisher_extender(testpoint, redis_store):
    """Extends given service with functions to publish to geobus channel"""

    class GeobusExtender(object):
        def __init__(self, base):
            self.base = base

        async def sync_send_to_channel(self, channel, message, max_tries=5):
            # Attention: that relies on service using geobus listener queue
            @testpoint('/geobus/queue/finished/{}'.format(channel))
            def handler(data):
                assert data['success']

            await self.base.enable_testpoints()

            for _ in range(max_tries):
                redis_store.publish(channel, message)

                try:
                    await handler.wait_call(2)
                    return
                except callinfo.CallQueueTimeoutError:
                    pass

            # if failed to receive message
            assert False

        def __getattr__(self, attr):
            if attr in self.__dict__:
                return getattr(self, attr)
            return getattr(self.base, attr)

    def create_extender(service_fixture):
        return GeobusExtender(service_fixture)

    return create_extender
