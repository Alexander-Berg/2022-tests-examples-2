import aiohttp
from aiohttp import web
from aiohttp import web_response
import pytest

from generated.clients import weather


NOWCAST_WEATHER_RESPONSE = {
    'GenTime': 1647003285,
    'Timeline': {
        '1646999400': {
            'PrecType': 0,
            'PrecStrength': 0,
            'Cloudiness': 4,
            'IsSolarDay': True,
            'Icon': 'ovc',
            'GenTime': 1647000419,
        },
        '1647008400': {
            'PrecType': 0,
            'PrecStrength': 0,
            'Cloudiness': 4,
            'IsSolarDay': True,
            'Icon': 'ovc',
            'GenTime': 1647003285,
        },
    },
    'TzInfo': {
        'Name': 'Europe/Volgograd',
        'Abbr': '+03',
        'Dst': False,
        'Offset': 10800,
    },
}

TIMELINE_PARAMS = dict(geoid=213, lat=1, lon=2)
TILE_PARAMS = dict(
    x=1, y=1, z=1, scale=12, encoded=True, nowcast_gen_time=123, for_date=123,
)
TILE_REQ_PARAMS = dict(x=1, y=1, z=1, nowcast_gen_time=123, for_date=123)


@pytest.mark.parametrize(
    'weather_url, method, params',
    [
        (
            '/api/v3/nowcast/timeline',
            'api_v3_nowcast_timeline_get',
            TIMELINE_PARAMS,
        ),
        ('/api/v3/nowcast/tile', 'api_v3_nowcast_tile_get', TILE_PARAMS),
    ],
)
@pytest.mark.parametrize(
    'status_code, ext_response, content_type',
    [
        (400, {'errors': ['error1', 'error2']}, 'application/json'),
        (404, 'some error message', 'text/plain'),
    ],
)
async def test_error_responses_schema(
        web_context,
        mock_weather,
        weather_url,
        method,
        params,
        status_code,
        ext_response,
        content_type,
):
    @mock_weather(weather_url)
    async def handle(request):  # pylint: disable=unused-variable
        return web.json_response(
            ext_response, status=status_code, content_type=content_type,
        )

    try:
        await getattr(web_context.clients.weather, method)(**params)
    except weather.ClientResponse as exc:
        assert exc.status == status_code


@pytest.mark.parametrize(
    'weather_url, proxy_url, params',
    [
        ('/api/v3/nowcast/timeline', '/api/weather/nowcast/timeline', {}),
        ('/api/v3/nowcast/tile', '/api/weather/nowcast/tile', TILE_REQ_PARAMS),
    ],
)
@pytest.mark.parametrize(
    'status_code, ext_response, content_type, expected_message',
    [
        (
            400,
            {'errors': ['error1', 'error2']},
            'application/json',
            'error1\nerror2',
        ),
        (404, 'some error message', 'text/plain', '"some error message"'),
    ],
)
@pytest.mark.usefixtures('atlas_blackbox_mock')
async def test_error_responses_proxy(
        web_app_client,
        mock_weather,
        weather_url,
        proxy_url,
        params,
        status_code,
        ext_response,
        content_type,
        expected_message,
):
    @mock_weather(weather_url)
    async def handle(request):  # pylint: disable=unused-variable
        return web.json_response(
            ext_response, status=status_code, content_type=content_type,
        )

    response = await web_app_client.get(proxy_url, params=params)

    assert response.status == status_code

    content = await response.json()
    assert content['message'] == expected_message


async def test_nowcast_timeline_content_type(web_context, mock_weather):
    @mock_weather('/api/v3/nowcast/timeline')
    async def handle(request):  # pylint: disable=unused-variable
        return web.json_response(NOWCAST_WEATHER_RESPONSE)

    response: aiohttp.ClientResponse = (
        await web_context.clients.weather.api_v3_nowcast_timeline_get(
            **TIMELINE_PARAMS,
        )
    )
    assert response.status == 200


@pytest.mark.usefixtures('atlas_blackbox_mock')
async def test_nowcast_timeline_success_response_proxy(
        web_app_client, mock_weather,
):
    @mock_weather('/api/v3/nowcast/timeline')
    async def handle(request):  # pylint: disable=unused-variable
        return web.json_response(NOWCAST_WEATHER_RESPONSE)

    response: aiohttp.ClientResponse = await web_app_client.get(
        '/api/weather/nowcast/timeline',
    )
    assert response.status == 200
    content = await response.json()

    assert content == NOWCAST_WEATHER_RESPONSE


async def test_nowcast_tile_content_type(web_context, mock_weather):
    @mock_weather('/api/v3/nowcast/tile')
    async def handle(request):  # pylint: disable=unused-variable
        return web_response.Response(
            body=b'1234567qwerty', content_type='image/png',
        )

    response: aiohttp.ClientResponse = (
        await web_context.clients.weather.api_v3_nowcast_tile_get(
            **TILE_PARAMS,
        )
    )
    assert response.status == 200


@pytest.mark.usefixtures('atlas_blackbox_mock')
async def test_nowcast_tile_success_response_proxy(
        web_app_client, mock_weather,
):
    random_pile_of_bytes = b'1234567qwerty'

    @mock_weather('/api/v3/nowcast/tile')
    async def handle(request):  # pylint: disable=unused-variable
        return web_response.Response(
            body=random_pile_of_bytes, content_type='image/png',
        )

    response: aiohttp.ClientResponse = await web_app_client.get(
        '/api/weather/nowcast/tile', params=TILE_REQ_PARAMS,
    )

    assert response.status == 200

    content = await response.read()
    assert content == random_pile_of_bytes
