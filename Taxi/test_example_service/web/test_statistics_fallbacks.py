import asyncio

from aiohttp import web
import pytest

from generated.clients import yet_another_service as client_module

DATE = '2019-12-10T17:56:15+03:00'


@pytest.fixture(name='client')
def yas_fixture(web_context):
    return web_context.clients.yet_another_service


class Statistics:
    def __init__(self, context, mock_statistics):
        self._dumped = []
        self._context = context

        @mock_statistics('/v1/metrics/store')
        async def _handler(request):
            self._dumped.append(request.json)
            return {}

        self.handler = _handler

    async def dump(self):
        # pylint: disable=protected-access
        await self._context.clients.statistics._send()
        result = self._dumped
        self._dumped = []
        return result


@pytest.fixture(name='statistics', autouse=True)
async def _statictics(mock_statistics, statistics, web_context):
    return Statistics(web_context, mock_statistics)


def _generate_metrics(metrics):
    return _sort_metrics(
        [{'name': name, 'value': value} for name, value in metrics],
    )


def _sort_metrics(metrics: list) -> list:
    return sorted(metrics, key=lambda x: (x['name'], x['value']))


@pytest.mark.now(DATE)
async def test_happy_path(mock_yet_another_service, client, statistics):
    @mock_yet_another_service('/ping')
    async def good_ping_handler(request):
        return None

    @mock_yet_another_service('/test_inline/ping')
    async def another_handler(request):
        return None

    resp = await client.ping()
    assert resp.status == 200

    resp = await client.ping()
    assert resp.status == 200

    @mock_yet_another_service('/ping')
    async def bad_ping_handler(request):
        return web.Response(status=500)

    with pytest.raises(client_module.NotDefinedResponse) as exc_info:
        await client.ping()
    assert exc_info.value.status == 500

    resp = await client.test_inline_ping_get()
    assert resp.status == 200

    assert good_ping_handler.times_called == 2
    assert bad_ping_handler.times_called == 3  # retries
    assert another_handler.times_called == 1

    dumped = await statistics.dump()
    assert len(dumped) == 1
    dumped = dumped[0]
    assert dumped.pop('service') == 'example_service_web'
    assert dumped.pop('time_bucket') == DATE
    assert _sort_metrics(dumped.pop('metrics')) == _generate_metrics(
        [
            ['handler.yet-another-service./ping-GET.success', 2],
            ['handler.yet-another-service./ping-GET.error', 1],
        ],
    )


async def test_fallback_fired(
        client, mock_statistics, web_context, mock_yet_another_service,
):
    @mock_statistics('/v1/service/health')
    async def _health_handler(request):
        assert request.args['service']
        return {
            'fallbacks': ['handler.yet-another-service./ping-GET.fallback'],
        }

    await web_context.refresh_caches()

    @mock_yet_another_service('/ping')
    async def bad_ping_handler(request):
        return web.Response(status=500)

    with pytest.raises(client_module.NotDefinedResponse) as exc_info:
        await client.ping()
    assert exc_info.value.status == 500

    assert bad_ping_handler.times_called == 1


@pytest.mark.config(
    STATISTICS_FALLBACK_OVERRIDES=[
        {
            'service': 'example_service_web',
            'enabled': True,
            'fallbacks': ['handler.yet-another-service./ping-GET.fallback'],
        },
    ],
)
@pytest.mark.parametrize('manual_attempts', [True, False])
async def test_enabled_override(
        client, mock_yet_another_service, web_context, manual_attempts,
):
    @mock_yet_another_service('/ping')
    async def bad_ping_handler(request):
        return web.Response(status=500)

    await web_context.refresh_caches()

    with pytest.raises(client_module.NotDefinedResponse) as exc_info:
        if manual_attempts:
            await client.ping(_attempts=2)
        else:
            await client.ping()
    assert exc_info.value.status == 500

    assert bad_ping_handler.times_called == 1


@pytest.mark.config(
    STATISTICS_FALLBACK_OVERRIDES=[
        {
            'service': 'example_service_web',
            'enabled': False,
            'fallbacks': ['handler.yet-another-service./ping-GET.fallback'],
        },
    ],
)
@pytest.mark.parametrize('manual_attempts', [True, False])
async def test_disabled_override(
        client, mock_yet_another_service, web_context, manual_attempts,
):
    @mock_yet_another_service('/ping')
    async def bad_ping_handler(request):
        return web.Response(status=500)

    await web_context.refresh_caches()

    with pytest.raises(client_module.NotDefinedResponse) as exc_info:
        if manual_attempts:
            await client.ping(_attempts=2)
        else:
            await client.ping()
    assert exc_info.value.status == 500

    if manual_attempts:
        assert bad_ping_handler.times_called == 2
    else:
        assert bad_ping_handler.times_called == 3


@pytest.mark.now(DATE)
async def test_bad_exception(client, patch, statistics):
    @patch(
        'generated.clients.yet_another_service.'
        'YetAnotherServiceClient._session_request',
    )
    async def session_request(*args, **kwargs):
        raise asyncio.TimeoutError

    with pytest.raises(client_module.ClientException):
        await client.ping()

    assert len(session_request.calls) == 3

    dumped = await statistics.dump()
    assert len(dumped) == 1
    dumped = dumped[0]
    assert dumped.pop('service') == 'example_service_web'
    assert dumped.pop('time_bucket') == DATE
    assert _sort_metrics(dumped.pop('metrics')) == _generate_metrics(
        [['handler.yet-another-service./ping-GET.error', 1]],
    )


async def test_disabled_in_client(
        client, monkeypatch, statistics, mock_yet_another_service, patch,
):
    monkeypatch.setattr(client, '_statistics_fallbacks_enabled', False)

    @mock_yet_another_service('/ping')
    async def good_ping_handler(request):
        return None

    @mock_yet_another_service('/test_inline/ping')
    async def bad_ping_handler(request):
        return web.Response(status=500)

    resp = await client.ping()
    assert resp.status == 200

    with pytest.raises(client_module.NotDefinedResponse) as exc_info:
        await client.test_inline_ping_get()
    assert exc_info.value.status == 500

    @patch(
        'generated.clients.yet_another_service.'
        'YetAnotherServiceClient._session_request',
    )
    async def session_request(*args, **kwargs):
        raise asyncio.TimeoutError

    with pytest.raises(client_module.ClientException):
        await client.ping()

    assert len(session_request.calls) == 3

    assert await statistics.dump() == []
    assert good_ping_handler.times_called == 1
    assert bad_ping_handler.times_called == 3
