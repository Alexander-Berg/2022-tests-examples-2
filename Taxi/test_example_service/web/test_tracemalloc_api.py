# pylint: disable=redefined-outer-name
import tracemalloc

import aiohttp
import pytest

from taxi.pytest_plugins.blacksuite import service_client
import tracemalloc_api


@pytest.fixture()
async def tracing_client(
        taxi_example_service_web: service_client.AiohttpClientTestsControl,
):
    class TestTracingClient(tracemalloc_api.TracingClient):
        async def _request(
                self, method, path, json=None,
        ) -> aiohttp.ClientResponse:
            response = await taxi_example_service_web.request(
                method, path, json=json,
            )
            response.raise_for_status()
            return response

    client = TestTracingClient('dummy')
    yield client
    await client.session.close()


async def test_tracing_flow(tracing_client: tracemalloc_api.TracingClient):
    tracing = await tracing_client.get_status()
    assert tracing.status == 'disabled'

    await tracing_client.start_tracing(5)

    tracing = await tracing_client.get_status()
    assert tracing.status == 'enabled'
    assert tracing.traceback_limit == 5

    snapshot = await tracing_client.take_snapshot()
    assert isinstance(snapshot, tracemalloc.Snapshot)

    await tracing_client.stop_tracing()
    tracing = await tracing_client.get_status()
    assert tracing.status == 'disabled'

    await tracing_client.start_tracing()
    tracing = await tracing_client.get_status()
    assert tracing.status == 'enabled'
    assert tracing.traceback_limit == 1

    await tracing_client.stop_tracing()
