# pylint: disable=redefined-outer-name,unused-variable
import asyncio
import typing

import aiohttp
import pytest

from taxi import discovery
from taxi.clients import driver_photos
from taxi.clients.helpers import errors as client_errors
from taxi.models import image_typing


DRIVER_PHOTOS_SERVICE = discovery.Service(
    url='driver-photos.taxi.tst.yandex.net', name='taxi_driver_photos-photos',
)


class ConfigMock(typing.NamedTuple):
    retry_settings: driver_photos.RetrySettings


def client_with_settings(
        loop,
        retries: int = 1,
        timeout: float = 1,
        wait_between_retries: float = 1,
        retry_multiplier: float = 1,
        max_random_retry_delay: float = 1,
):
    factory = driver_photos.ClientFactory(
        DRIVER_PHOTOS_SERVICE, aiohttp.ClientSession(loop=loop),
    )
    return factory.client_with_settings(
        driver_photos.RetrySettings(
            retries=retries,
            timeout=timeout,
            wait_between_retries=wait_between_retries,
            retry_multiplier=retry_multiplier,
            max_random_retry_delay=max_random_retry_delay,
        ),
    )


@pytest.fixture
def client(loop):
    return client_with_settings(loop)


@pytest.mark.parametrize(
    ('response_json', 'expected_result'),
    [
        (
            {
                'photos': [
                    {'type': 'avatar', 'url': 'avatar_url'},
                    {'type': 'portrait', 'url': 'portrait_url'},
                ],
            },
            [
                driver_photos.Photo('avatar_url', image_typing.ImageType.AVA),
                driver_photos.Photo(
                    'portrait_url', image_typing.ImageType.PORTRAIT,
                ),
            ],
        ),
        ({'photos': []}, []),
    ],
)
async def test_get_photos(
        client,
        patch_aiohttp_session,
        response_mock,
        response_json: dict,
        expected_result: typing.List[driver_photos.Photo],
):
    @patch_aiohttp_session('http://' + DRIVER_PHOTOS_SERVICE.url, 'GET')
    def patch_request(method, url, *args, **kwargs):
        assert method == 'get'
        assert '/photos' in url
        return response_mock(json=response_json)

    result = await client.get_driver_photos('park_id', 'driver_profile_id')
    assert result == expected_result


@pytest.mark.parametrize(
    ('response_json', 'expected_error'),
    [
        ({}, driver_photos.ResponseFormatError),
        (
            {'photos': [{'type': 'bad_type', 'url': 'url'}]},
            driver_photos.ResponseFormatError,
        ),
    ],
)
async def test_client_exception(
        client,
        patch_aiohttp_session,
        response_mock,
        response_json: dict,
        expected_error: typing.Type[client_errors.BaseError],
):
    @patch_aiohttp_session('http://' + DRIVER_PHOTOS_SERVICE.url, 'GET')
    def patch_request(method, url, *args, **kwargs):
        assert method == 'get'
        assert '/photos' in url
        return response_mock(json=response_json)

    with pytest.raises(expected_error):
        await client.get_driver_photos('park_id', 'driver_profile_id')


@pytest.mark.parametrize(
    ('request_error', 'expected_error'),
    [
        (asyncio.TimeoutError, client_errors.BaseError),
        (aiohttp.ClientError, client_errors.BaseError),
    ],
)
async def test_aiohttp_exceptions(
        client,
        patch_aiohttp_session,
        response_mock,
        request_error: typing.Type[aiohttp.ClientError],
        expected_error: typing.Type[client_errors.BaseError],
):
    @patch_aiohttp_session('http://' + DRIVER_PHOTOS_SERVICE.url, 'GET')
    def patch_request(*args, **kwargs):
        raise request_error()

    with pytest.raises(expected_error):
        await client.get_driver_photos('park_id', 'driver_profile_id')
        assert False


@pytest.mark.parametrize(
    ('retry_settings', 'fails_before_response', 'expected_calls'),
    [(1, 0, 1), (2, 1, 2), (2, 2, 2), (2, 0, 1)],
)
async def test_client_retries(
        loop,
        patch_aiohttp_session,
        response_mock,
        retry_settings: int,
        fails_before_response: int,
        expected_calls: int,
):
    call_counter = 0

    @patch_aiohttp_session('http://' + DRIVER_PHOTOS_SERVICE.url, 'GET')
    def patch_request(*args, **kwargs):
        nonlocal call_counter
        call_counter += 1

        if call_counter <= fails_before_response:
            raise aiohttp.ClientError()

        return response_mock(json={'photos': []})

    client = client_with_settings(loop, retries=retry_settings)
    try:
        await client.get_driver_photos('park_id', 'driver_profile_id')
    except client_errors.BaseError:
        assert fails_before_response >= retry_settings

    assert call_counter == expected_calls


@pytest.mark.parametrize(
    ('retries_count', 'delay_count'),
    [
        pytest.param(0, 0, id='no_delays_without_retries'),
        pytest.param(1, 0, id='no_delays_for_single_request'),
        pytest.param(2, 1, id='delay_between_two_requests'),
        pytest.param(3, 2, id='delays_between_three_requests'),
    ],
)
async def test_retry_delays(
        loop,
        monkeypatch,
        patch_aiohttp_session,
        response_mock,
        retries_count,
        delay_count,
):
    delay_counter = 0

    async def patch_delay(*args, **kwargs):
        nonlocal delay_counter
        delay_counter += 1

    monkeypatch.setattr('asyncio.sleep', patch_delay)

    @patch_aiohttp_session('http://' + DRIVER_PHOTOS_SERVICE.url, 'GET')
    def patch_request(*args, **kwargs):
        raise aiohttp.ClientError()

    client = client_with_settings(loop, retries=retries_count)
    try:
        await client.get_driver_photos('park_id', 'driver_profile_id')
        assert False
    except client_errors.BaseError:
        assert delay_counter == delay_count
