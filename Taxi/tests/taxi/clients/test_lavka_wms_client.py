# pylint: disable=redefined-outer-name, protected-access
import pytest

from taxi import discovery
from taxi.clients import lavka_wms


@pytest.fixture
def mock_lavka_wms(patch_aiohttp_session, response_mock):
    lavka_wms_service = discovery.find_service('lavka-wms')

    def _wrapper(expected_url, expected_kwargs, response=None):
        if response is None:
            response = {}

        @patch_aiohttp_session(lavka_wms_service.url)
        def _request(method, url, **kwargs):
            assert url == lavka_wms_service.url + expected_url
            assert kwargs == expected_kwargs
            return response_mock(json=response)

        return _request

    return _wrapper


@pytest.fixture
def lavka_client(test_taxi_app):
    lavka_wms_service = discovery.find_service('lavka-wms')

    client = lavka_wms.LavkaWmsClient(
        lavka_wms_service,
        session=test_taxi_app.session,
        tvm_client=test_taxi_app.tvm,
    )
    return client


@pytest.mark.parametrize(
    'method, url, expected_kwargs, lavka_response',
    [
        (
            'get',
            '/some_url',
            {
                'headers': {'Content-Type': 'application/json'},
                'json': None,
                'params': None,
            },
            {},
        ),
        (
            'post',
            '/other_url',
            {
                'headers': {'Content-Type': 'application/json'},
                'json': None,
                'params': None,
            },
            {'some': 'value'},
        ),
    ],
)
async def test_request(
        mock_lavka_wms,
        lavka_client,
        method,
        url,
        expected_kwargs,
        lavka_response,
):
    lavka_mock = mock_lavka_wms(url, expected_kwargs, lavka_response)
    response = await lavka_client._request(url, method=method)
    assert response == lavka_response
    assert lavka_mock.calls


@pytest.mark.parametrize(
    'store_ids, expected_kwargs',
    [
        (
            ['test_id'],
            {
                'headers': {'Content-Type': 'application/json'},
                'json': {'store_id': ['test_id']},
                'params': None,
            },
        ),
        (
            ['test_id', 'test_id_2'],
            {
                'headers': {'Content-Type': 'application/json'},
                'json': {'store_id': ['test_id', 'test_id_2']},
                'params': None,
            },
        ),
    ],
)
async def test_load_stores(
        mock_lavka_wms, lavka_client, store_ids, expected_kwargs,
):
    lavka_mock = mock_lavka_wms('/v1/load', expected_kwargs)
    await lavka_client.load_stores(store_ids=store_ids)
    assert lavka_mock.calls


@pytest.mark.parametrize(
    ('store_id', 'count_change', 'token', 'expected_kwargs'),
    [
        (
            'increase',
            42,
            'increase_token',
            {
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'count_change': 42,
                    'store_id': 'increase',
                    'token': 'increase_token',
                },
                'params': None,
            },
        ),
        (
            'decrease',
            -42,
            'decrease_token',
            {
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'count_change': -42,
                    'store_id': 'decrease',
                    'token': 'decrease_token',
                },
                'params': None,
            },
        ),
        (
            'zero',
            0,
            'zero_token',
            {
                'headers': {'Content-Type': 'application/json'},
                'json': {
                    'count_change': 0,
                    'store_id': 'zero',
                    'token': 'zero_token',
                },
                'params': None,
            },
        ),
    ],
)
async def test_set_messages_count(
        mock_lavka_wms,
        lavka_client,
        store_id,
        count_change,
        token,
        expected_kwargs,
):
    lavka_mock = mock_lavka_wms('/v1/set_messages_count', expected_kwargs)
    await lavka_client.set_messages_count(
        store_id=store_id, count_change=count_change, token=token,
    )
    assert lavka_mock.calls
