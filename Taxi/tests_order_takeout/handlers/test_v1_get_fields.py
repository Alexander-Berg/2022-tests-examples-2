import bson
import pytest


async def test_404(taxi_order_takeout):
    response = await taxi_order_takeout.post(
        '/v1/get-fields', json={'order_id': 'not_found'},
    )
    assert response.status == 404


@pytest.mark.ydb(files=['fill_fields.sql'])
async def test_fields(taxi_order_takeout):
    response = await taxi_order_takeout.post(
        '/v1/get-fields', json={'order_id': 'order_1'},
    )
    assert response.status == 200
    doc = bson.BSON(response.content).decode()
    assert doc == {
        'fields': [
            {
                'anonymized_value': {},
                'json_path': 'candidates.0.driver',
                'original_value': {
                    'driver': {
                        'id': bson.ObjectId('5e00b661954de74d8a6af7c7'),
                    },
                },
            },
            {
                'json_path': 'order.user_id',
                'anonymized_value': 'fake_user',
                'original_value': 'original_user',
            },
        ],
    }
