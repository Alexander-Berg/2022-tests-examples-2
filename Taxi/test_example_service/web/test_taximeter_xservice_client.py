import aiohttp
from aiohttp import web
import pytest

from generated.clients import taximeter_xservice
from generated.models import taximeter_xservice as taximeter_xservice_models


QOS_CONFIG = {'__default__': {'timeout-ms': 1000, 'attempts': 2}}


@pytest.fixture(name='client')
def _client(web_context):
    return web_context.clients.taximeter_xservice


@pytest.mark.config(XSERVICE_CLIENT_QOS=QOS_CONFIG)
async def test_successful_retries(client, mock_taximeter_xservice):
    @mock_taximeter_xservice('/utils/driver-status-check')
    async def handler(request):
        assert len(request.json) == 1
        data = request.json[0]
        assert data['park_id'] == '1'
        assert data['driver_id'] == '2'
        assert data['app_family'] == '3'
        assert data['status'] == '4'

        if handler.times_called > 0:
            return web.json_response(
                [
                    {
                        'park_id': '0',
                        'driver_id': '1',
                        'app_family': '2',
                        'result': '3',
                        'onlycard': False,
                        'providers': 5,
                        'integration_event': True,
                    },
                ],
            )
        return web.Response(status=500)

    response = await client.utils_driver_status_check_post(
        request=[
            taximeter_xservice_models.DriverCheckRequest(
                park_id='1', driver_id='2', app_family='3', status='4',
            ),
        ],
    )

    assert response.status == 200
    assert len(response.body) == 1
    assert response.body[0].park_id == '0'
    assert response.body[0].driver_id == '1'
    assert response.body[0].app_family == '2'
    assert response.body[0].result == '3'
    assert not response.body[0].onlycard
    assert response.body[0].providers == 5
    assert response.body[0].integration_event

    assert handler.times_called == 2


@pytest.mark.config(XSERVICE_CLIENT_QOS=QOS_CONFIG)
async def test_neverending_500(client, mock_taximeter_xservice):
    @mock_taximeter_xservice('/utils/driver-status-check')
    async def handler(request):
        return web.Response(status=500)

    with pytest.raises(taximeter_xservice.NotDefinedResponse) as exc_info:
        await client.utils_driver_status_check_post(
            request=[
                taximeter_xservice_models.DriverCheckRequest(
                    park_id='1', driver_id='2', app_family='3', status='4',
                ),
            ],
        )

    assert exc_info.value.status == 500
    assert handler.times_called == 2


@pytest.mark.parametrize(
    'attempts',
    [
        pytest.param(
            2,
            marks=pytest.mark.config(
                XSERVICE_CLIENT_QOS={
                    '__default__': {'timeout-ms': 1000, 'attempts': 2},
                },
            ),
        ),
        pytest.param(
            3,
            marks=pytest.mark.config(
                XSERVICE_CLIENT_QOS={
                    '/utils/driver-status-check': {
                        'timeout-ms': 1000,
                        'attempts': 3,
                    },
                },
            ),
        ),
        pytest.param(
            4,
            marks=pytest.mark.config(
                XSERVICE_CLIENT_QOS={
                    '/utils/driver-status-check/': {
                        'timeout-ms': 1000,
                        'attempts': 4,
                    },
                },
            ),
        ),
        pytest.param(
            5,
            marks=pytest.mark.config(
                XSERVICE_CLIENT_QOS={
                    '/utils/driver-status-check@post': {
                        'timeout-ms': 1000,
                        'attempts': 5,
                    },
                },
            ),
        ),
    ],
)
async def test_neverending_errors(client, patch, attempts):
    @patch('aiohttp.ClientSession.request')
    async def request(*args, **kwargs):
        raise aiohttp.ClientConnectionError('something bad happened')

    with pytest.raises(taximeter_xservice.ClientException) as exc_info:
        await client.utils_driver_status_check_post(
            request=[
                taximeter_xservice_models.DriverCheckRequest(
                    park_id='1', driver_id='2', app_family='3', status='4',
                ),
            ],
        )

    assert exc_info.value.args == (
        'taximeter-xservice client error: something bad happened',
    )
    assert len(request.calls) == attempts


@pytest.mark.config(XSERVICE_CLIENT_QOS=QOS_CONFIG)
async def test_manual_set_attempts(client, mock_taximeter_xservice):
    @mock_taximeter_xservice('/utils/driver-status-check')
    async def handler(request):
        return web.Response(status=500)

    with pytest.raises(taximeter_xservice.NotDefinedResponse) as exc_info:
        await client.utils_driver_status_check_post(
            request=[
                taximeter_xservice_models.DriverCheckRequest(
                    park_id='1', driver_id='2', app_family='3', status='4',
                ),
            ],
            _attempts=10,
        )

    assert exc_info.value.status == 500
    assert handler.times_called == 10
