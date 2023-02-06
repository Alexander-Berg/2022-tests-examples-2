import decimal
import json

import pytest

import tests_contractor_order_history.utils as utils

SUCCESS_STATISTICS_METRIC = (
    'contractor-order-history.order_patch_queue.publisher.shard_0.success'
)
ERROR_STATISTICS_METRIC = (
    'contractor-order-history.order_patch_queue.publisher.shard_0.error'
)


@pytest.mark.parametrize(
    'inject_publish_error, shards_with_workaround',
    [
        pytest.param(False, [], id='no failures'),
        pytest.param(
            True, [], id='failed to publish in logbroker; no workaround',
        ),
        pytest.param(
            True, [0], id='failed to publish in logbroker; with workaround',
        ),
    ],
)
@pytest.mark.redis_store(['set', 'Orders:CurrentNumber:park0', 123])
async def test_insert_logbroker(
        taxi_contractor_order_history,
        testpoint,
        fleet_parks_shard,
        pgsql,
        inject_publish_error,
        shards_with_workaround,
        taxi_config,
        statistics,
):
    @testpoint('logbroker_publish')
    async def _publish(msg):
        response = await taxi_contractor_order_history.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'order-patch-reader-1',
                    'data': msg['data'],
                    'topic': (
                        '/taxi/contractor-order-history/testing/patch-queue'
                    ),
                    'cookie': 'cookie',
                },
            ),
        )
        assert response.status_code == 200

    @testpoint('logbroker_commit')
    def _commit(cookie):
        pass

    # inject logbroker publish error
    @testpoint('order_patch_queue_publish_tp')
    def _inject_failure_tp(data):
        return {'inject_failure': inject_publish_error}

    # enable fallback mechanism
    configs = {
        'CONTRACTOR_ORDER_HISTORY_ENABLE_PATCH_QUEUE_EMERGENCY_WORKAROUND': {
            'shards_enabled': shards_with_workaround,
        },
    }
    taxi_config.set_values(configs)

    req = {
        'park_id': 'park0',
        'alias_id': 'alias0',
        'inserted_ts': 1609448400000,
        'date_booking': 1609448400001,
        'order_fields': [
            # integer
            {'name': 'number_group', 'value': '1337'},
            # numeric(18,6)
            {'name': 'cost_total', 'value': '999999999999.999999'},
            # varchar 32
            {'name': 'agg_id', 'value': 'some agg_id'},
            # text
            {'name': 'category', 'value': 'some category'},
            # json
            {'name': 'price_corrections', 'value': '{"key": "val"}'},
            # jsonb
            {'name': 'home_coord', 'value': '{"key": "val"}'},
            # bit
            {'name': 'sms', 'value': '1'},
            # timestamp
            {'name': 'date_end', 'value': '1609448520000'},
            # flags
            {'name': 'flags', 'value': '{is_freightage,some_flag}'},
            # order_id
            {'name': 'order_id', 'value': 'order_id0'},
        ],
    }

    # invalidate caches even for statistics client
    await taxi_contractor_order_history.invalidate_caches()

    response = None
    async with statistics.capture(taxi_contractor_order_history) as capture:
        response = await taxi_contractor_order_history.post('insert', json=req)

    if not inject_publish_error:
        assert capture.statistics[SUCCESS_STATISTICS_METRIC] == 1
        assert response.status_code == 200
        await _publish.wait_call()
        await _commit.wait_call()
    elif not shards_with_workaround:
        assert capture.statistics[ERROR_STATISTICS_METRIC] == 1
        assert response.status_code == 500
    else:
        assert capture.statistics[ERROR_STATISTICS_METRIC] == 1
        assert response.status_code == 200

    query = """
        SELECT number, date_create, date_booking,
               number_group, cost_total, agg_id, category,
               price_corrections, home_coord, sms, date_end,
               flags, order_id
        FROM orders_0
        WHERE park_id='park0' AND id='alias0';
        """
    cursor = pgsql['orders'].cursor()
    cursor.execute(query)
    row = cursor.fetchone()

    if not inject_publish_error or shards_with_workaround:
        assert row is not None
    else:
        assert row is None
        return

    assert row[0] == 124
    assert utils.with_orders_tz(row[1]) == utils.date_from_ms(
        req['inserted_ts'],
    )
    assert utils.with_orders_tz(row[2]) == utils.date_from_ms(
        req['date_booking'],
    )
    # number_group
    assert row[3] == 1337
    # cost_total
    assert row[4] == decimal.Decimal('999999999999.999999')
    # agg_id
    assert row[5] == 'some agg_id'
    # category
    assert row[6] == 'some category'
    # price_corrections
    assert row[7] == {'key': 'val'}
    # home_coord
    assert row[8] == {'key': 'val'}
    # sms
    assert row[9] == '1'
    # date_end
    assert utils.with_orders_tz(row[10]) == utils.date_from_ms(1609448520000)
    # flags
    assert row[11] == ['is_freightage', 'some_flag']
    # order_id
    assert row[12] == 'order_id0'


@pytest.mark.redis_store(['set', 'Orders:CurrentNumber:park0', 123])
async def test_empty_fields(
        taxi_contractor_order_history, testpoint, fleet_parks_shard, pgsql,
):
    @testpoint('logbroker_publish')
    async def _publish(msg):
        response = await taxi_contractor_order_history.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': 'order-patch-reader-1',
                    'data': msg['data'],
                    'topic': (
                        '/taxi/contractor-order-history/testing/patch-queue'
                    ),
                    'cookie': 'cookie',
                },
            ),
        )
        assert response.status_code == 200

    @testpoint('logbroker_commit')
    def _commit(cookie):
        pass

    req = {
        'park_id': 'park0',
        'alias_id': 'alias0',
        'inserted_ts': 1609448400000,
        'date_booking': 1609448400001,
        'order_fields': [],
    }
    response = await taxi_contractor_order_history.post('insert', json=req)
    assert response.status_code == 200
    await _publish.wait_call()
    await _commit.wait_call()

    query = """
        SELECT number, date_create, date_booking
        FROM orders_0
        WHERE park_id='park0' AND id='alias0';
        """
    cursor = pgsql['orders'].cursor()
    cursor.execute(query)
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == 124
    assert utils.with_orders_tz(row[1]) == utils.date_from_ms(
        req['inserted_ts'],
    )
    assert utils.with_orders_tz(row[2]) == utils.date_from_ms(
        req['date_booking'],
    )


async def test_duplicate_fields(taxi_contractor_order_history):
    req = {
        'park_id': 'park0',
        'alias_id': 'alias0',
        'inserted_ts': 1609448400000,
        'date_booking': 1609448400000,
        'order_fields': [
            {'name': 'agg_id', 'value': 'some text'},
            {'name': 'agg_id', 'value': 'some other text'},
        ],
    }
    response = await taxi_contractor_order_history.post('insert', json=req)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'req_field_name,req_field_value',
    [
        pytest.param('park_id', 'park0', id='park_id'),
        pytest.param('id', 'order0', id='alias_id'),
        pytest.param('date_create', 1609448400000, id='date_create'),
        pytest.param('date_booking', 1609448400000, id='date_booking'),
    ],
)
async def test_duplicate_required(
        taxi_contractor_order_history, req_field_name, req_field_value,
):
    req = {
        'park_id': 'park0',
        'alias_id': 'alias0',
        'inserted_ts': 1609448400000,
        'date_booking': 1609448400000,
        'order_fields': [{'name': req_field_name, 'value': req_field_value}],
    }
    response = await taxi_contractor_order_history.post('insert', json=req)
    assert response.status_code == 400


@pytest.mark.parametrize(
    'name,value,expected',
    [
        # smallint
        pytest.param('closed_by', '0', 200, id='smallint zero'),
        pytest.param('closed_by', '32767', 200, id='smallint max'),
        pytest.param('closed_by', '-32768', 200, id='smallint min'),
        pytest.param('closed_by', '32768', 400, id='smallint max+1'),
        pytest.param('closed_by', '-32769', 400, id='smallint min-1'),
        pytest.param('closed_by', 'str', 400, id='smallint not number'),
        pytest.param('closed_by', 'x123', 400, id='smallint leading trash'),
        pytest.param('closed_by', '123x', 400, id='smallint trailing trash'),
        # integer
        pytest.param('status', '0', 200, id='integer zero'),
        pytest.param('status', '2147483647', 200, id='integer max'),
        pytest.param('status', '-2147483648', 200, id='integer min'),
        pytest.param('status', '2147483648', 400, id='integer max+1'),
        pytest.param('status', '-2147483649', 400, id='integer min-1'),
        pytest.param('status', 'str', 400, id='integer not number'),
        pytest.param('status', 'x123', 400, id='integer leading trash'),
        pytest.param('status', '123x', 400, id='integer trailing trash'),
        # bigint
        pytest.param('clid', '0', 200, id='bigint zero'),
        pytest.param('clid', '9223372036854775807', 200, id='bigint max'),
        pytest.param('clid', '-9223372036854775808', 200, id='bigint min'),
        pytest.param('clid', '9223372036854775808', 400, id='bigint max+1'),
        pytest.param('clid', '-9223372036854775809', 400, id='bigint min-1'),
        pytest.param('clid', 'str', 400, id='bigint not number'),
        pytest.param('clid', 'x123', 400, id='bigint leading trash'),
        pytest.param('clid', '123x', 400, id='bigint trailing trash'),
        # numeric(10,5)
        pytest.param('cost_coupon_percent', '0', 200, id='numeric(10,5) zero'),
        pytest.param(
            'cost_coupon_percent',
            '123.456',
            200,
            id='numeric(10,5) valid value',
        ),
        pytest.param(
            'cost_coupon_percent', '99999.99999', 200, id='numeric(10,5) max',
        ),
        pytest.param(
            'cost_coupon_percent', '-99999.99999', 200, id='numeric(10,5) min',
        ),
        pytest.param(
            'cost_coupon_percent', '100000', 400, id='numeric(10,5) above max',
        ),
        pytest.param(
            'cost_coupon_percent',
            '-100000',
            400,
            id='numeric(10,5) below min',
        ),
        # numeric(18,6)
        pytest.param('cost_total', '0', 200, id='numeric(18,6) zero'),
        pytest.param(
            'cost_total', '123.456', 200, id='numeric(18,6) valid value',
        ),
        pytest.param(
            'cost_total', '999999999999.999999', 200, id='numeric(18,6) max',
        ),
        pytest.param(
            'cost_total', '-999999999999.999999', 200, id='numeric(18,6) min',
        ),
        pytest.param(
            'cost_total', '1000000000000', 400, id='numeric(18,6) above max',
        ),
        pytest.param(
            'cost_total', '-1000000000000', 400, id='numeric(18,6) below min',
        ),
        # bit
        pytest.param('car_franchise', '0', 200, id='bit 0'),
        pytest.param('car_franchise', '1', 200, id='bit 1'),
        pytest.param('car_franchise', '00', 400, id='bit 00'),
        pytest.param('car_franchise', '01', 400, id='bit 01'),
        pytest.param('car_franchise', '', 400, id='bit empty'),
        pytest.param('car_franchise', 't', 400, id='bit t'),
        pytest.param('car_franchise', 'f', 400, id='bit f'),
        pytest.param('car_franchise', 'true', 400, id='bit true'),
        pytest.param('car_franchise', 'false', 400, id='bit false'),
        # varchar(9)
        pytest.param('rule_type_color', '', 200, id='varchar(9) empty'),
        pytest.param('rule_type_color', 'test', 200, id='varchar(9) len 4'),
        pytest.param(
            'rule_type_color', 'some text', 200, id='varchar(9) len 9',
        ),
        pytest.param(
            'rule_type_color', '1234567890', 400, id='varchar(9) len 10',
        ),
        # varchar(16)
        pytest.param('car_number', '', 200, id='varchar(16) empty'),
        pytest.param('car_number', 'some text', 200, id='varchar(16) len 9'),
        pytest.param(
            'car_number', '1234567890123456', 200, id='varchar(16) len 16',
        ),
        pytest.param(
            'car_number', '12345678901234567', 400, id='varchar(16) len 17',
        ),
        # varchar(32), unicode
        pytest.param(
            'rule_type_name',
            'Яндекс.Корпоративный',
            200,
            id='varchar(32) utf-8',
        ),
        # json
        pytest.param('price_corrections', '', 400, id='json empty'),
        pytest.param('price_corrections', 'null', 200, id='json null'),
        pytest.param('price_corrections', '""', 200, id='json empty string'),
        pytest.param(
            'price_corrections', '"just string"', 200, id='json just string',
        ),
        pytest.param('price_corrections', '123', 200, id='json just number'),
        pytest.param('price_corrections', 'false', 200, id='json just false'),
        pytest.param('price_corrections', '[]', 200, id='json empty array'),
        pytest.param('price_corrections', '{}', 200, id='json empty object'),
        pytest.param(
            'price_corrections', '{"key": "value"}', 200, id='json correct',
        ),
        pytest.param(
            'price_corrections', '{"key": "value}', 400, id='json incorrect',
        ),
        # text
        pytest.param('category', '', 200, id='text empty'),
        pytest.param('category', 'some text', 200, id='text non-empty'),
        # timestamp
        pytest.param('date_drive', '', 400, id='timestamp empty'),
        pytest.param('date_drive', '0', 200, id='timestamp zero'),
        pytest.param(
            'date_drive', '1609448400000', 200, id='timestamp 2021-01-01',
        ),
        pytest.param(
            'date_drive', '4765122000000', 200, id='timestamp 2121-01-01',
        ),
        pytest.param('flags', '', 400, id='empty_but_expected_array'),
        pytest.param('flags', 'some_text', 400, id='strng but expected array'),
        pytest.param('flags', r'{}', 200, id='empty array'),
        pytest.param('flags', r'{item1}', 200, id='array with one item'),
        pytest.param(
            'flags',
            r'{item_1, item2, item3}',
            200,
            id='array with some items',
        ),
    ],
)
async def test_validate(
        taxi_contractor_order_history,
        name,
        value,
        expected,
        fleet_parks_shard,
):
    req = {
        'park_id': 'park0',
        'alias_id': 'alias0',
        'inserted_ts': 1609448400000,
        'date_booking': 1609448400000,
        'order_fields': [{'name': name, 'value': value}],
    }
    response = await taxi_contractor_order_history.post('insert', json=req)
    assert response.status_code == expected


@pytest.mark.parametrize(
    'number_in_fields',
    [
        pytest.param(True, id='number specified in order_fields'),
        pytest.param(
            False, id='number absent in order_fields, get from redis',
        ),
    ],
)
@pytest.mark.redis_store(['set', 'Orders:CurrentNumber:park0', 123])
async def test_order_number(
        taxi_contractor_order_history,
        redis_store,
        number_in_fields,
        fleet_parks_shard,
):
    req = {
        'park_id': 'park0',
        'alias_id': 'alias0',
        'inserted_ts': 1609448400000,
        'date_booking': 1609448400000,
        'order_fields': [],
    }
    if number_in_fields:
        req['order_fields'].append({'name': 'number', 'value': '321'})
    response = await taxi_contractor_order_history.post('insert', json=req)
    assert response.status_code == 200
    assert json.loads(redis_store.get('Orders:CurrentNumber:park0')) == (
        123 if number_in_fields else 124
    )
