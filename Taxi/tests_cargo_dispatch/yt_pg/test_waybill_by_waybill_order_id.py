import os

import pytest


@pytest.mark.pgsql('cargo_dispatch', files=['pg_raw_denorm.sql'])
@pytest.mark.config(
    CARGO_DISPATCH_DENORM_READ_SETTINGS={
        '__default__': {
            'enabled': True,
            'pg-use': True,
            'yt-use': False,
            'ttl-days': 3650,
        },
    },
)
async def test_waybill_denorm_read_pg(taxi_cargo_dispatch, load_json):
    response = await taxi_cargo_dispatch.get(
        '/v1/test/waybills/full',
        params={'waybill_order_id': '2c6176b4-693b-40ff-92d2-084fa707b08a'},
    )
    assert response.status == 200
    assert response.json() == load_json('expected_waybill_response.json')


@pytest.mark.xfail(
    os.getenv('IS_TEAMCITY'),
    strict=False,
    reason='some problems in CI with YT',
)
@pytest.mark.yt(dyn_table_data=['yt_raw_denorm.yaml'])
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.config(
    CARGO_DISPATCH_DENORM_READ_SETTINGS={
        '__default__': {'enabled': True, 'pg-use': False, 'yt-use': True},
    },
)
async def test_waybill_denorm_read_yt(taxi_cargo_dispatch, load_json):
    response = await taxi_cargo_dispatch.get(
        '/v1/test/waybills/full',
        params={'waybill_order_id': '2c6176b4-693b-40ff-92d2-084fa707b08a'},
    )
    assert response.status == 200
    assert response.json() == load_json('expected_waybill_response.json')


@pytest.mark.pgsql('cargo_dispatch', files=['pg_raw_denorm.sql'])
@pytest.mark.usefixtures('yt_apply')
@pytest.mark.config(
    CARGO_DISPATCH_DENORM_READ_SETTINGS={
        '__default__': {'enabled': True, 'pg-use': False, 'yt-use': True},
    },
)
async def test_waybill_denorm_read_updated_ts(taxi_cargo_dispatch):
    response = await taxi_cargo_dispatch.get(
        '/v1/test/waybills/full',
        params={'waybill_order_id': '2c6176b4-693b-40ff-92d2-084fa707b08a'},
    )
    assert response.status == 404
