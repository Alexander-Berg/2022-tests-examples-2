# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import asyncio
import logging
import json
from typing import AsyncGenerator

import grpc
import pytest
from yagr_plugins import *  # noqa: F403 F401

from geobus_tools.redis import (  # noqa: F401
    geobus_redis_getter,  # noqa: F401
)  # noqa: F401 C5521
from geobus_tools.redis import (  # noqa: F401
    geobus_redis_holder,  # noqa: F401
)  # noqa: F401 C5521

YAGR_GRPC_ADDRESS = 'localhost:50051'

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def contractor_transport_request(mockserver):
    @mockserver.json_handler(
        '/contractor-transport/v1/transport-active/updates',
    )
    def _mock_transport_active(request):
        assert request.method == 'GET'
        if request.query.get('cursor') == '123456_6':
            return {'contractors_transport': [], 'cursor': '1234567_6'}
        data = {
            'contractors_transport': [
                {
                    'contractor_id': 'park3_driver2',
                    'is_deleted': False,
                    'revision': '1234567_2',
                    'transport_active': {'type': 'pedestrian'},
                },
                {
                    'contractor_id': 'park3_driver3',
                    'is_deleted': False,
                    'revision': '1234567_3',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car3'},
                },
                {
                    'contractor_id': 'park4_driver4',
                    'is_deleted': False,
                    'revision': '1234567_4',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car4'},
                },
                {
                    'contractor_id': 'dbid_uuidpedestrian',
                    'is_deleted': False,
                    'revision': '1234567_5',
                    'transport_active': {'type': 'pedestrian'},
                },
                {
                    'contractor_id': 'dbid_uuiddriver',
                    'is_deleted': False,
                    'revision': '1234567_6',
                    'transport_active': {'type': 'car', 'vehicle_id': 'car3'},
                },
            ],
            'cursor': '1234567_6',
        }
        return mockserver.make_response(response=json.dumps(data))


# pylint: disable=redefined-outer-name
@pytest.fixture
async def taxi_yagr_adv(taxi_yagr, geopipeline_config):  # noqa: F811
    print('CREATE taxi_yagr_adv')
    return await geopipeline_config(taxi_yagr)


@pytest.fixture(name='grpc_channel')
async def _grpc_channel(taxi_yagr):
    async with grpc.aio.insecure_channel(YAGR_GRPC_ADDRESS) as channel:
        logger.info('gRPC channel opened')

        done, _ = await asyncio.wait(
            [channel.channel_ready()],
            return_when=asyncio.FIRST_COMPLETED,
            timeout=15,
        )

        if not done:
            raise Exception(
                f'Failed to connect to remote gRPC server by '
                f'address {YAGR_GRPC_ADDRESS}',
            )

        logger.info('gRPC channel ready')

        yield channel
    logger.info('gRPC channel closed')
