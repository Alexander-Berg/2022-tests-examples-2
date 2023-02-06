# pylint: disable=unused-argument,too-many-locals,unused-variable
from stall.client.weather import client as weather_client


async def test_by_point(tap, api, ext_api, tvm_ticket):
    with tap.plan(7):
        async def handler(response):
            return 200, {
                'condition': 'clear',
                'icon': 'skc',
                'temp': -5,
                'text': 'В ближайшие 2 часа осадков не ожидается'
            }

        async with await ext_api(weather_client, handler):
            t = await api()
            await t.post_ok('api_admin_weather_get',
                            json={
                                'lat': 56.838011,
                                'lon': 60.597465
                            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('weather.condition', 'clear', 'condition')
            t.json_is('weather.temperature', -5, 'temperature')
            t.json_is('weather.icon', 'skc', 'icon')
            t.json_is('weather.text',
                      'В ближайшие 2 часа осадков не ожидается', 'text')


async def test_without_text(tap, api, ext_api, tvm_ticket):
    with tap.plan(7):
        async def handler(response):
            return 200, {
                'condition': 'clear',
                'icon': 'skc',
                'temp': -5,
            }

        async with await ext_api(weather_client, handler):
            t = await api()
            await t.post_ok('api_admin_weather_get',
                            json={
                                'lat': 56.838011,
                                'lon': 60.597465,
                                'lang': 'EN'
                            })

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('weather.condition', 'clear', 'condition')
            t.json_is('weather.temperature', -5, 'temperature')
            t.json_is('weather.icon', 'skc', 'icon')
            t.json_is('weather.text', None, 'no text')


async def test_error(tap, api, ext_api, tvm_ticket):
    with tap.plan(4):
        async def handler(response):
            return 400, {
                'errors': [
                    'schema: error converting value for "geoid"'
                ]
            }

        async with await ext_api(weather_client, handler):
            t = await api()
            await t.post_ok('api_admin_weather_get',
                            json={
                                'lat': 56.838011,
                                'lon': 60.597465,
                                'lang': 'fr'
                            })

            t.status_is(400, diag=True)
            t.json_is('code', 'ER_BAD_REQUEST')
            t.json_is('message', 'Request to weather failed: 400, Bad Request')

