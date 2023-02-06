import dataclasses
import os
from typing import Optional

from aiohttp import web
import pytest
import yarl


@pytest.fixture(name='create_assert_mock')
def _create_assert_mock(mockserver, web_app_client):
    def _mock(mock):
        async def _create(called: bool, check_env=True):
            if check_env:
                assert called == bool(os.environ.get('HTTP_PROXY'))

            # there might be several requests from caches, so save it
            urls_before = [r.url for r in mock.calls]

            await web_app_client.get(
                '/use_aiohttp', params={'url': mockserver.url('/echo_header')},
            )
            urls_after = [r.url for r in mock.calls]
            for url in urls_before:
                urls_after.remove(url)
            urls_diff = urls_after

            expected_url = yarl.URL(mockserver.url('/echo_header'))
            if called:
                assert urls_diff.count(expected_url) == 1
            else:
                assert urls_diff.count(expected_url) == 0

        return _create

    return _mock


async def change_proxy_config(taxi_config, web_context, url) -> None:
    taxi_config.set_values(
        {'BACKEND_PY3_SERVICES_HTTP_PROXY': {'example-service': url}},
    )
    await web_context.refresh_caches()


async def test_proxy_legacy_client(
        proxy_mock,
        proxy_mock2,
        create_assert_mock,
        taxi_config,
        web_context,
        mockserver,
):
    @mockserver.json_handler('/echo_header')
    async def _endpoint_mock(request):
        return ''

    assert_mock_1 = create_assert_mock(proxy_mock)
    assert_mock_2 = create_assert_mock(proxy_mock2)

    # 0. no proxy
    await assert_mock_1(called=False)

    # 1. no proxy mode -> proxy mode
    await change_proxy_config(taxi_config, web_context, proxy_mock.url)
    await assert_mock_1(called=True)

    # 2. proxy mode -> proxy mode (port change)
    await change_proxy_config(taxi_config, web_context, proxy_mock2.url)
    # disable HTTP_PROXY check as it points to mock2, not mock1
    await assert_mock_1(called=False, check_env=False)
    await assert_mock_2(called=True)

    # 3. proxy mode -> no proxy mode
    await change_proxy_config(taxi_config, web_context, '')
    await assert_mock_1(called=False)

    # 4. no proxy mode -> no proxy mode
    taxi_config.set_values({'BACKEND_PY3_SERVICES_HTTP_PROXY': {}})
    await web_context.refresh_caches()
    await assert_mock_1(called=False)

    # 5. no proxy mode -> proxy mode
    await change_proxy_config(taxi_config, web_context, proxy_mock.url)
    await assert_mock_1(called=True)


# Driver Authorizer - auto generated client, honours proxy settings
async def test_proxy_codegen_client(
        proxy_mock, taxi_config, web_context, mock_driver_authorizer,
):
    await change_proxy_config(taxi_config, web_context, proxy_mock.url)

    @mock_driver_authorizer('/driver/sessions')
    async def handler(_):
        return web.json_response(
            data={'ttl': 3600}, headers={'X-Driver-Session': '100500'},
        )

    response = await web_context.clients.driver_authorizer.driver_sessions_get(
        uuid='1111', _sep_thread_deserialize=True,
    )

    assert any(
        req.method == 'GET'
        and req.path == '/driver-authorizer/driver/sessions'
        for req in proxy_mock.calls
    )

    assert response.status == 200
    assert response.body.ttl == 3600
    assert response.headers.x_driver_session == '100500'

    assert handler.times_called == 1


@pytest.fixture(name='configs_mock')
def _configs_mock():
    pass


@dataclasses.dataclass
class ProxyTestParams:
    proxy_url: Optional[str] = None
    proxy_status_code: Optional[int] = None

    async def reply_with_status_response(self, _):
        return web.Response(
            status=self.proxy_status_code,
            reason=f'This proxy always returns code {self.proxy_status_code}',
        )


# Config - ignores proxy settings
@pytest.mark.parametrize(
    'params',
    [
        pytest.param(ProxyTestParams(), id='working proxy'),
        pytest.param(
            ProxyTestParams(proxy_url='http://bad-proxy:9999'),
            id='unreachable proxy',
        ),
        pytest.param(
            ProxyTestParams(proxy_status_code=400), id='proxy with error 400',
        ),
        pytest.param(
            ProxyTestParams(proxy_status_code=404), id='proxy with error 404',
        ),
        pytest.param(
            ProxyTestParams(proxy_status_code=500), id='proxy with error 500',
        ),
    ],
)
async def test_configs_ignore_proxy(
        monkeypatch,
        configs_mock,
        mockserver,
        proxy_mock,
        taxi_config,
        web_context,
        now,
        params,
):
    proxy_url = params.proxy_url or proxy_mock.url

    monkeypatch.setattr(
        web_context.config,
        'BACKEND_PY3_SERVICES_HTTP_PROXY',
        {'example-service': proxy_url},
    )
    monkeypatch.setattr(
        web_context.client_configs.settings, 'CONFIGS_API_RETRIES_TIMEOUT', 0,
    )
    monkeypatch.setattr(
        web_context.client_configs.settings, 'CONFIGS_API_NUM_RETRIES', 1,
    )

    if params.proxy_status_code:
        monkeypatch.setattr(
            proxy_mock, '_handle_request', params.reply_with_status_response,
        )

    @mockserver.json_handler('/configs-service/configs/values')
    async def mock_configs(_):
        return {
            'configs': {
                'BACKEND_PY3_SERVICES_HTTP_PROXY': {
                    'example-service': params.proxy_url,
                },
            },
            'updated_at': now.strftime('%Y-%m-%dT%H:%M:%SZ'),
        }

    await web_context.client_configs.get_all()

    assert mock_configs.times_called == 1
    assert not proxy_mock.calls


async def test_proxy_disabled(
        proxy_mock, taxi_config, web_context, mock_driver_authorizer,
):
    await web_context.refresh_caches()
    await change_proxy_config(taxi_config, web_context, '')

    @mock_driver_authorizer('/driver/sessions')
    async def handler(_):
        return web.json_response({}, headers={'X-Driver-Session': '100500'})

    await web_context.clients.driver_authorizer.driver_sessions_get(
        uuid='1111', _sep_thread_deserialize=True,
    )

    assert not proxy_mock.calls
    assert handler.times_called == 1
