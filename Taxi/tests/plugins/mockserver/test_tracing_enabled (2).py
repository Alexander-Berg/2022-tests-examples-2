import aiohttp.web
import pytest

from taxi_tests.plugins import mockserver as mockserver_module
from taxi_tests.utils import tracing


# pylint: disable=invalid-name
async def test_mockserver_responds_with_handler_to_current_test(
        mockserver, create_service_client, trace_id,
):
    @mockserver.handler('/arbitrary/path')
    def handler(request):
        return aiohttp.web.Response(text='arbitrary text', status=200)

    client = create_service_client(
        mockserver.base_url,
        service_headers={tracing.TRACE_ID_HEADER: trace_id},
    )

    response = await client.post('arbitrary/path')

    assert response.status_code == 200
    assert response.text == 'arbitrary text'


async def test_mockserver_responds_with_json_handler_to_current_test(
        mockserver, create_service_client, trace_id,
):
    @mockserver.json_handler('/arbitrary/path')
    def json_handler(request):
        return {'arbitrary_key': True}

    client = create_service_client(
        mockserver.base_url,
        service_headers={tracing.TRACE_ID_HEADER: trace_id},
    )

    response = await client.post('arbitrary/path')

    assert response.status_code == 200
    assert response.json() == {'arbitrary_key': True}


async def test_mockserver_skips_handler_and_responds_500_to_other_test(
        mockserver, create_service_client,
):
    @mockserver.handler('/arbitrary/path')
    def handler(request):
        return aiohttp.web.Response(text='arbitrary text', status=200)

    client = create_service_client(
        mockserver.base_url,
        service_headers={tracing.TRACE_ID_HEADER: tracing.generate_trace_id()},
    )

    response = await client.post('arbitrary/path')
    assert response.status_code == 500
    assert response.text == mockserver_module.REQUEST_FROM_ANOTHER_TEST_ERROR


async def test_mockserver_skips_json_handler_and_responds_500_to_other_test(
        mockserver, create_service_client,
):
    @mockserver.json_handler('/arbitrary/path')
    def json_handler(request):
        return {'arbitrary_key': True}

    client = create_service_client(
        mockserver.base_url,
        service_headers={tracing.TRACE_ID_HEADER: tracing.generate_trace_id()},
    )

    response = await client.post('arbitrary/path')
    assert response.status_code == 500
    assert response.text == mockserver_module.REQUEST_FROM_ANOTHER_TEST_ERROR


@pytest.mark.parametrize(
    'http_headers',
    [
        {},  # no trace_id in http headers
        {tracing.TRACE_ID_HEADER: ''},
        {tracing.TRACE_ID_HEADER: 'id_without_testsuite-_prefix'},
    ],
)
async def test_mockserver_responds_500_on_unhandled_request_from_other_sources(
        mockserver, http_headers, create_service_client,
):
    client = create_service_client(
        mockserver.base_url, service_headers=http_headers,
    )

    response = await client.post('arbitrary/path')
    assert response.status_code == 500
