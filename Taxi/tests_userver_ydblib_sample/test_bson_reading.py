import bson
import pytest


@pytest.mark.ydb(files=['fill_orders.sql'])
async def test_bson_reading(taxi_userver_ydblib_sample):
    response = await taxi_userver_ydblib_sample.post(
        'ydblib/bson-reading', json={'id': 'id1'},
    )
    assert response.status_code == 200
    raw_bson = bson.BSON(response.content).decode()
    res = raw_bson['doc']
    assert res == {
        'h': {'e': {'l': {'l': '0'}}},
        'w': {'o': {'r': {'l': 'd'}}},
    }
