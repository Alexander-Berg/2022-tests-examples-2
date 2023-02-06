import asyncio
import grpc
import logging
import pytest

logger = logging.getLogger(__name__)


MAPPINGS_GRPC_ADDRESS = 'localhost:12033'


@pytest.fixture()
async def grpc_mappings_channel(taxi_market_fast_mappings_reader):
    async with grpc.aio.insecure_channel(MAPPINGS_GRPC_ADDRESS) as channel:
        logger.info('gRPC channel opened')

        done, _ = await asyncio.wait(
            [channel.channel_ready()],
            return_when=asyncio.FIRST_COMPLETED,
            timeout=15,
        )

        if not done:
            raise Exception(
                f'Failed to connect to remote gRPC server by '
                f'address {MAPPINGS_GRPC_ADDRESS}',
            )

        logger.info('gRPC channel ready')

        yield channel
    logger.info('gRPC channel closed')
