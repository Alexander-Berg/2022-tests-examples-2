# pylint: disable=protected-access, redefined-outer-name
import aiohttp
import pytest

from taxi.clients import translate


@pytest.fixture
async def test_app(test_taxi_app):
    test_taxi_app.translate_client = translate.TranslateAPIClient(
        session=test_taxi_app.session, settings=test_taxi_app.settings,
    )
    return test_taxi_app


@pytest.fixture
def mock_translate_request(monkeypatch, mock):
    def _create_dummy_request(response):
        @mock
        async def _dummy_request(*args, **kwargs):
            return response

        monkeypatch.setattr(
            translate.TranslateAPIClient, '_request', _dummy_request,
        )
        return _dummy_request

    return _create_dummy_request


@pytest.mark.parametrize(
    'network_ok,method,url,data,params,expected_result,expected_exception',
    [
        # All OK
        (True, 'POST', 'some_url', {'some': 'data'}, None, {}, None),
        (True, 'GET', 'some_url', None, {'some': 'params'}, {}, None),
        # Wrong URL
        (
            True,
            'GET',
            'wrong_url',
            {'some': 'data'},
            None,
            None,
            translate.ClientError,
        ),
        # Cannot connect
        (
            False,
            'POST',
            'some_url',
            {'some': 'data'},
            None,
            None,
            translate.NetworkError,
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

            async def json(self):
                return {}

            async def text(self):
                return '{}'

        if not network_ok:
            raise aiohttp.ClientConnectionError('Cannot connect')
        if kwargs['url'] != 'http://test-translate-url/some_url':
            return _DummyResponse(404)

        return _DummyResponse(200)

    monkeypatch.setattr(
        test_app.translate_client._session, 'request', _dummy_request,
    )

    exception = None
    result = None
    try:
        result = await test_app.translate_client._request(
            url, method=method, data=data, params=params,
        )
    except translate.BaseError as _e:
        exception = type(_e)

    assert exception == expected_exception
    assert result == expected_result

    if expected_exception is None:
        request_calls = _dummy_request.calls
        assert request_calls[0]['kwargs'] == {
            'url': 'http://test-translate-url/some_url',
            'json': data,
            'method': method,
            'params': params,
        }
