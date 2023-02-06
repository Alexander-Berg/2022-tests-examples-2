# pylint: disable=W0212
import json

from aiohttp import web
import pytest

from driver_referrals.common import urls as urls_models


@pytest.mark.config(
    DRIVER_REFERRALS_PROXY_URLS_COUNTRY={
        '__default__': {
            'cargo': 'https://cargo',
            'eda': 'https://eda',
            'lavka': (
                'https://lavka?code={code}&orders_provider={orders_provider}'
            ),
            'retail': 'https://retail',
            'taxi': 'https://taxi?code={code}',
            'taxi_walking_courier': 'https://taxi_walking_courier',
        },
    },
)
@pytest.mark.pgsql(
    'driver_referrals',
    queries=[
        """INSERT INTO referral_profiles (
            id, park_id, driver_id, promocode, status
        ) VALUES ('test', 'p', 'd', 'ПРОМОКОДЕ','completed')""",
    ],
    files=['pg_driver_referrals.sql'],
)
async def test_urls(web_context, mockserver):
    @mockserver.json_handler('/ya-cc/--')
    def _(request):
        request_data = request._data.decode()
        text = 'https://ya.cc/t/pwwkT5JaDBUEP'
        if 'eda' in request_data:
            text = 'https://ya.cc/t/EDA'
        elif 'lavka' in request_data:
            text = 'https://ya.cc/t/LAVKA'
        elif 'taxi' in request_data:
            text = 'https://ya.cc/t/TAXI'

        return web.Response(
            headers={'Content-Type': 'text/javascript; charset=utf-8'},
            text=text,
        )

    park_id = 'p'
    driver_id = 'd'

    urls = urls_models.Urls(
        web_context,
        park_id=park_id,
        driver_id=driver_id,
        country_id='test',
        code='ПРОМОКОДЕ',
        urls=None,
    )
    assert await urls.get_short_url('eda') == 'https://ya.cc/t/EDA'
    assert await urls.get_short_url('taxi') == 'https://ya.cc/t/TAXI'
    assert await urls.get_short_url('lavka') == 'https://ya.cc/t/LAVKA'
    await urls.update_db()

    async with web_context.pg.master_pool.acquire() as connection:
        await connection.set_type_codec(
            'jsonb',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog',
        )
        row = await connection.fetchrow(
            'SELECT * FROM referral_profiles'
            ' WHERE park_id = $1 AND driver_id = $2',
            park_id,
            driver_id,
        )
    assert row['referral_urls'] == {
        'eda': {'url': 'https://eda', 'short_url': 'https://ya.cc/t/EDA'},
        'taxi': {
            'url': 'https://taxi?code=ПРОМОКОДЕ',
            'short_url': 'https://ya.cc/t/TAXI',
        },
        'lavka': {
            'url': 'https://lavka?code=ПРОМОКОДЕ&orders_provider=lavka',
            'short_url': 'https://ya.cc/t/LAVKA',
        },
    }
