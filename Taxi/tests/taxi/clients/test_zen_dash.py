# pylint: disable=protected-access, redefined-outer-name
import aiohttp
import pytest

from taxi.clients import zen_dash


@pytest.fixture
async def test_app(test_taxi_app):
    test_taxi_app.zen_dash_client = zen_dash.ZenDashAPIClient(
        session=test_taxi_app.session,
        settings=test_taxi_app.settings,
        config=test_taxi_app.config,
    )
    return test_taxi_app


@pytest.fixture
def mock_zen_dash_request(monkeypatch, mock):
    def _create_dummy_request(response):
        @mock
        async def _dummy_request(*args, **kwargs):
            return response

        monkeypatch.setattr(
            zen_dash.ZenDashAPIClient, '_request', _dummy_request,
        )
        return _dummy_request

    return _create_dummy_request


@pytest.mark.parametrize(
    'network_ok,method,url,data,params,expected_result,expected_exception',
    [
        # All OK
        (
            True,
            'POST',
            'http://test-zen-dash-url/some_url',
            {'some': 'data'},
            None,
            {},
            None,
        ),
        (
            True,
            'GET',
            'http://test-zen-dash-url/some_url',
            None,
            {'some': 'params'},
            {},
            None,
        ),
        # Wrong URL
        (
            True,
            'GET',
            'http://test-zen-dash-url/wrong_url',
            {'some': 'data'},
            None,
            None,
            zen_dash.ClientError,
        ),
        # Cannot connect
        (
            False,
            'POST',
            'http://test-zen-dash-url/some_url',
            {'some': 'data'},
            None,
            None,
            zen_dash.NetworkError,
        ),
    ],
)
async def test_request(
        test_app,
        monkeypatch,
        mock,
        network_ok,
        method,
        url,
        data,
        params,
        expected_result,
        expected_exception,
):
    @mock
    async def _dummy_request(**kwargs):
        class _DummyResponse:
            def __init__(self, status):
                self.status = status
                self.method = kwargs['method']
                self.url = kwargs['url']

            async def json(self, *args, **kwargs):
                return {}

            async def text(self):
                return '{}'

        if not network_ok:
            raise aiohttp.ClientConnectionError('Cannot connect')
        if kwargs['url'] != 'http://test-zen-dash-url/some_url':
            return _DummyResponse(404)

        return _DummyResponse(200)

    monkeypatch.setattr(
        test_app.zen_dash_client._session, 'request', _dummy_request,
    )

    exception = None
    result = None
    try:
        result = await test_app.zen_dash_client._request(
            url, method=method, data=data, params=params,
        )
    except zen_dash.BaseError as _e:
        exception = type(_e)

    assert exception == expected_exception
    assert result == expected_result

    if expected_exception is None:
        request_calls = _dummy_request.calls
        assert request_calls[0]['kwargs'] == {
            'url': 'http://test-zen-dash-url/some_url',
            'json': data,
            'method': method,
            'params': params,
        }


@pytest.mark.config(ZEN_DASH_PROFILE='sp')
async def test_profle(test_app, monkeypatch, mock):
    @mock
    async def _dummy_request(**kwargs):
        class _DummyResponse:
            def __init__(self, status):
                self.status = status
                self.method = kwargs['method']
                self.url = kwargs['url']

            async def json(self, *args, **kwargs):
                return {}

            async def text(self):
                return '{}'

        return _DummyResponse(200)

    monkeypatch.setattr(
        test_app.zen_dash_client._session, 'request', _dummy_request,
    )
    data = {'some': 'data'}
    await test_app.zen_dash_client.autoreply(data=data)
    request_calls = _dummy_request.calls
    assert request_calls[0]['kwargs'] == {
        'url': 'http://test-sp-taxi-url/clients/autoreply',
        'json': data,
        'method': 'POST',
        'params': None,
    }


@pytest.mark.config(ZEN_DASH_PROFILE='sp')
@pytest.mark.parametrize(
    'zen_dash_action_profiles,expected_autoreply_url',
    [
        ({}, 'http://test-sp-taxi-url/clients/autoreply'),
        (
            {'autoreply': {'profile': 'plotva', 'percentage': 0}},
            'http://test-sp-taxi-url/clients/autoreply',
        ),
        (
            {'autoreply': {'profile': 'plotva', 'percentage': 100}},
            'http://test-plotva-url/autoreply/v1',
        ),
    ],
)
async def test_action_profle(
        test_app,
        monkeypatch,
        mock,
        zen_dash_action_profiles,
        expected_autoreply_url,
):
    test_app.config.ZEN_DASH_ACTION_PROFILES = zen_dash_action_profiles

    @mock
    async def _dummy_request(**kwargs):
        class _DummyResponse:
            def __init__(self, status):
                self.status = status
                self.method = kwargs['method']
                self.url = kwargs['url']

            async def json(self, *args, **kwargs):
                return {}

            async def text(self):
                return '{}'

        return _DummyResponse(200)

    monkeypatch.setattr(
        test_app.zen_dash_client._session, 'request', _dummy_request,
    )
    data = {'some': 'data'}
    await test_app.zen_dash_client.autoreply(data=data)
    request_calls = _dummy_request.calls
    assert request_calls[0]['kwargs'] == {
        'url': expected_autoreply_url,
        'json': data,
        'method': 'POST',
        'params': None,
    }
