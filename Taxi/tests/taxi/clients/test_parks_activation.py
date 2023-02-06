# pylint: disable=redefined-outer-name,protected-access
import datetime

import aiohttp
import pytest

from taxi import config as taxi_config
from taxi.clients import parks_activation
from taxi.clients import tvm


@pytest.fixture
async def client(db, loop, simple_secdist):
    session = aiohttp.ClientSession(loop=loop)
    config = taxi_config.Config(db)
    yield parks_activation.ParksActivationClient(
        config=config,
        session=session,
        tvm_client=tvm.TVMClient(
            service_name=parks_activation.TVM_SERVICE_NAME,
            secdist=simple_secdist,
            config=config,
            session=session,
        ),
    )
    await session.close()


async def test_retrieve(mockserver, client):
    @mockserver.json_handler('/parks_activation/v1/parks/activation/retrieve')
    def _retrieve_handler(request):
        return {
            'parks_activation': [
                {'park_id': 1, 'last_modified': '2019-09-10T10:00:00.000'},
            ],
        }

    parks = await client.retrieve(park_ids=[1])
    assert _retrieve_handler.times_called == 1
    assert parks[0]['last_modified'] == datetime.datetime(2019, 9, 10, 10)
