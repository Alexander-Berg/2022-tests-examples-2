import datetime

import pytest

from atlas_etl.generated.cron import run_cron


NOW = datetime.datetime(2021, 3, 10, 6, 15, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.weather': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_weather(
        clickhouse_client_mock,
        fix_ch_insert_data,
        load_json,
        patch,
        patch_aiohttp_session,
        response_mock,
):
    weather_response = load_json('weather_response.json')

    @patch_aiohttp_session('http://api.weather.yandex.ru/v2/forecast', 'GET')
    def _weather_response(*args, **kwargs):
        if 'lat=55.798551&lon=49.106324' in args[1]:
            city_name = 'Казань'
        elif 'geoid=213' in args[1]:
            city_name = 'Москва'
        elif 'geoid=75' in args[1]:
            city_name = 'Владивосток'
        else:
            raise RuntimeError('Unknown query!')
        headers = kwargs['headers']
        assert headers == {
            'X-Yandex-API-Key': 123,
            'User-Agent': 'yandex-taxi-atlas',
        }
        return response_mock(
            json={'fact': weather_response[city_name]}, status=200,
        )

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        data = kwargs.get('params')
        data = fix_ch_insert_data(data)
        expected_ch_insert = load_json('weather_ch_insert.json')
        assert data == expected_ch_insert
        return len(data)

    await run_cron.main(['atlas_etl.crontasks.weather', '-t', '0'])
