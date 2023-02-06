# pylint: disable=invalid-name
import logging

from aiohttp import web
import pytest

from taxi import opentracing
from taxi.opentracing import tracer as tracer_
from taxi.opentracing.ext import http_client
from taxi.opentracing.ext import middleware


@pytest.fixture
def mongodb_collections():
    return ['localizations_meta']


@pytest.mark.config(TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}})
async def test_app_without_base_integration_with_initializing_and_middleware(
        aiohttp_client, test_taxi_app, caplog, tracer_custom_config,
):
    caplog.set_level(logging.INFO, logger='taxi.opentracing.reporter')
    with tracer_custom_config(report_span_enabled=True):

        async def ping(request):
            return web.json_response({})

        test_taxi_app.middlewares.append(middleware.opentracing_integration)
        test_taxi_app.router.add_get('/ping', ping)
        client = await aiohttp_client(test_taxi_app)

        async with client.get('/ping') as resp:
            data = await resp.json()
            assert data == {}

        record = caplog.records[1]
        assert record.levelname == 'INFO'
        assert record.extdict['_type'] == 'span'


@pytest.mark.config(TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}})
async def test_app_without_base_integration_with_middleware_usage(
        aiohttp_client, test_taxi_app,
):
    assert isinstance(opentracing.global_tracer(), tracer_.NoOpTracer)

    async def ping(request):
        return web.json_response({})

    test_taxi_app.middlewares.append(middleware.opentracing_integration)
    test_taxi_app.router.add_get('/ping', ping)
    client = await aiohttp_client(test_taxi_app)

    async with client.get('/ping') as resp:
        data = await resp.json()
        assert data == {}


@pytest.mark.config(TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}})
async def test_app_without_base_integration_with_custom_client_usage(
        aiohttp_client, test_taxi_app,
):
    assert isinstance(opentracing.global_tracer(), tracer_.NoOpTracer)

    async def ping(request):
        return web.json_response({})

    test_taxi_app.router.add_get('/ping', ping)
    client = await aiohttp_client(test_taxi_app)
    await client.session.close()
    # pylint: disable=protected-access
    client._session = http_client.OpentracingClientSession()

    async with client.get('/ping') as resp:
        data = await resp.json()
        assert data == {}


@pytest.mark.config(TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}})
def test_app_with_base_app_integration(test_opentracing_app):
    assert not isinstance(opentracing.global_tracer(), tracer_.NoOpTracer)
    assert isinstance(
        test_opentracing_app.session, http_client.OpentracingClientSession,
    )

    assert (
        opentracing.global_tracer().service_name
        == test_opentracing_app.service_name
    )


@pytest.mark.config(TRACING_SAMPLING_PROBABILITY={'testing': {'es': 1}})
async def test_app_with_base_app_integration_and_middleware(
        test_opentracing_app, aiohttp_client,
):
    assert not isinstance(opentracing.global_tracer(), tracer_.NoOpTracer)

    async def ping(request):
        return web.json_response({})

    test_opentracing_app.middlewares.append(middleware.opentracing_integration)
    test_opentracing_app.router.add_get('/ping', ping)
    client = await aiohttp_client(test_opentracing_app)

    async with client.get('/ping') as resp:
        data = await resp.json()
        assert data == {}
