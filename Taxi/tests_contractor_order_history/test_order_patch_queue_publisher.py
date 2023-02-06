import json

import pytest


def _fields_cmp(field):
    return field['name']


@pytest.mark.parametrize(
    'req',
    [
        pytest.param(
            {
                'park_id': 'park0',
                'alias_id': 'alias0',
                'inserted_ts': 1609448400000,
                'date_booking': 1609448400001,
                'order_fields': [
                    {'name': 'closed_by', 'value': '12345'},
                    {'name': 'number_group', 'value': '123456'},
                    {'name': 'clid', 'value': '1234567'},
                    {'name': 'cost_total', 'value': '999999999999.999999'},
                    {'name': 'cost_coupon_percent', 'value': '99999.99999'},
                    {'name': 'agg_id', 'value': 'some text'},
                    {'name': 'category', 'value': 'some other text'},
                    {
                        'name': 'price_corrections',
                        'value': '{"arbitrary_key1": "arbitrary_value1"}',
                    },
                    {
                        'name': 'home_coord',
                        'value': '{"arbitrary_key2": "arbitrary_value2"}',
                    },
                    {'name': 'phone_addition', 'value': '1'},
                    {'name': 'date_drive', 'value': '1355314332000'},
                ],
            },
        ),
    ],
)
@pytest.mark.redis_store(['set', 'Orders:CurrentNumber:park0', 123])
async def test_insert(
        taxi_contractor_order_history, testpoint, fleet_parks_shard, req,
):
    @testpoint('logbroker_publish')
    def _commit(msg):
        assert msg['name'] == 'order-patch-publisher'
        data = json.loads(msg['data'])
        assert data['method'] == 'insert'
        assert data['destination'] == {
            'shard_number': 0,
            'table_name': 'orders_0',
        }
        assert data['received_ts'] == req['inserted_ts']
        assert data['body']['park_id'] == req['park_id']
        assert data['body']['alias_id'] == req['alias_id']
        assert data['body']['number'] == 124
        assert data['body']['date_booking'] == req['date_booking']
        assert data['body']['date_create'] == req['inserted_ts']

        assert data['body']['order_fields'].sort(key=_fields_cmp) == req[
            'order_fields'
        ].sort(key=_fields_cmp)

    response = await taxi_contractor_order_history.post('insert', json=req)
    assert response.status_code == 200

    await _commit.wait_call()


@pytest.mark.parametrize(
    'req',
    [
        pytest.param(
            {
                'park_id': 'park0',
                'alias_id': 'alias0',
                'updated_ts': 1609448400000,
                'order_fields': [
                    {'name': 'closed_by', 'value': '12345'},
                    {'name': 'number_group', 'value': '123456'},
                    {'name': 'clid', 'value': '1234567'},
                    {'name': 'cost_total', 'value': '12345.678'},
                    {'name': 'cost_coupon_percent', 'value': '12345.678'},
                    {'name': 'agg_id', 'value': 'some text'},
                    {'name': 'category', 'value': 'some other text'},
                    {
                        'name': 'price_corrections',
                        'value': '{"arbitrary_key1": "arbitrary_value1"}',
                    },
                    {
                        'name': 'home_coord',
                        'value': '{"arbitrary_key2": "arbitrary_value2"}',
                    },
                    {'name': 'phone_addition', 'value': '1'},
                    {'name': 'date_drive', 'value': '1355314332000'},
                ],
                'condition_fields': [
                    {'name': 'status', 'op': 'lte', 'value': '70'},
                    {'name': 'driver_id', 'op': 'eq', 'value': 'driver0'},
                ],
            },
        ),
    ],
)
async def test_update(
        taxi_contractor_order_history, testpoint, fleet_parks_shard, req,
):
    @testpoint('logbroker_publish')
    def _commit(msg):
        assert msg['name'] == 'order-patch-publisher'
        data = json.loads(msg['data'])
        assert data['method'] == 'update'
        assert data['destination'] == {
            'shard_number': 0,
            'table_name': 'orders_0',
        }
        assert data['received_ts'] == req['updated_ts']
        assert data['body']['park_id'] == req['park_id']
        assert data['body']['alias_id'] == req['alias_id']

        assert data['body']['order_fields'].sort(key=_fields_cmp) == req[
            'order_fields'
        ].sort(key=_fields_cmp)

        assert data['body']['conditions'].sort(key=_fields_cmp) == req[
            'condition_fields'
        ].sort(key=_fields_cmp)

    response = await taxi_contractor_order_history.post('update', json=req)
    assert response.status_code == 200

    await _commit.wait_call()
