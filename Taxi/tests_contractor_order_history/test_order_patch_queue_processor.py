import datetime
import decimal
import json

import tests_contractor_order_history.utils as utils


def _clean_table(pgsql, tablename):
    query = 'DELETE FROM ' + tablename + ';'
    cursor = pgsql['orders'].cursor()
    cursor.execute(query)


def _check_insert(pgsql, expected):
    query = (
        """
            SELECT park_id, id, number,
                date_create, date_booking, phone_addition,
                cost_total, home_coord, date_drive, category,
                clid, rule_type_name
            FROM {tablename} WHERE park_id='{park_id}' AND id='{alias_id}';
            """.format(
            tablename=expected['destination']['table_name'],
            park_id=expected['body']['park_id'],
            alias_id=expected['body']['alias_id'],
        )
    )
    cursor = pgsql['orders'].cursor()
    cursor.execute(query)
    for row in cursor:
        assert row[0] == expected['body']['park_id']
        assert row[1] == expected['body']['alias_id']
        assert row[2] == expected['body']['number']
        assert utils.with_orders_tz(row[3]) == utils.date_from_ms(
            expected['body']['date_create'],
        )
        assert utils.with_orders_tz(row[4]) == utils.date_from_ms(
            expected['body']['date_booking'],
        )
        for i in range(0, 7):
            value = row[i + 5]
            if isinstance(value, decimal.Decimal):
                assert value == decimal.Decimal(
                    expected['body']['order_fields'][i]['value'],
                )
            elif isinstance(value, int):
                assert value == int(
                    expected['body']['order_fields'][i]['value'],
                )
            elif isinstance(value, (dict, list)):
                assert value == json.loads(
                    expected['body']['order_fields'][i]['value'],
                )
            elif isinstance(value, datetime.datetime):
                assert utils.with_orders_tz(value) == utils.date_from_ms(
                    int(expected['body']['order_fields'][i]['value']),
                )
            else:
                assert value == expected['body']['order_fields'][i]['value']


def _check_update(pgsql, expected):
    query = (
        """
            SELECT park_id, id, number,
                date_create, date_booking, phone_addition
            FROM {tablename} WHERE park_id='{park_id}' AND id='{alias_id}';
            """.format(
            tablename=expected['destination']['table_name'],
            park_id=expected['body']['park_id'],
            alias_id=expected['body']['alias_id'],
        )
    )
    cursor = pgsql['orders'].cursor()
    cursor.execute(query)
    for row in cursor:
        assert row[0] == expected['body']['park_id']
        assert row[1] == expected['body']['alias_id']
        assert row[2] == int(expected['body']['order_fields'][0]['value'])
        assert utils.with_orders_tz(row[3]) == utils.date_from_ms(
            int(expected['body']['order_fields'][1]['value']),
        )
        assert utils.with_orders_tz(row[4]) == utils.date_from_ms(
            int(expected['body']['order_fields'][2]['value']),
        )
        assert row[5] == expected['body']['order_fields'][3]['value']


async def test_queue_basic(taxi_contractor_order_history, testpoint):
    @testpoint('logbroker_commit')
    def _commit(cookie):
        assert cookie == 'cookie'

    @testpoint('order_patch_queue_raw_message_tp')
    def _raw_message_getter(data):
        pass

    @testpoint('order_patch_queue_processed_tp')
    def _store_to_pg(data):
        assert False, 'should not be called'

    await taxi_contractor_order_history.enable_testpoints()
    _raw_message_getter.flush()
    _commit.flush()

    messages = ['message1', 'message2']
    readers = ['order-patch-reader-1', 'order-patch-reader-2']

    messages.sort()

    msg_count = len(messages)
    for idx in range(0, msg_count):
        response = await taxi_contractor_order_history.post(
            'tests/logbroker/messages',
            data=json.dumps(
                {
                    'consumer': readers[idx],
                    'data': messages[idx],
                    'topic': (
                        '/taxi/contractor-order-history/testing/patch-queue'
                    ),
                    'cookie': 'cookie',
                },
            ),
        )
        assert response.status_code == 200
        await _commit.wait_call()

    result_messages = []
    for idx in range(0, len(messages)):
        result = await _raw_message_getter.wait_call()
        result_messages.append(result['data']['message'])
    result_messages.sort()

    assert result_messages == messages


async def test_enqueueing(taxi_contractor_order_history, testpoint, pgsql):
    alias_1 = {
        'method': 'insert',
        'received_ts': utils.date_to_ms(datetime.datetime.now(tz=None)),
        'destination': {'table_name': 'orders_0', 'shard_number': 0},
        'body': {
            'park_id': 'park_1',
            'alias_id': 'alias_1',
            'number': 1,
            'date_create': utils.date_to_ms(datetime.datetime.now(tz=None)),
            'date_booking': utils.date_to_ms(datetime.datetime.now(tz=None)),
            'order_fields': [
                {'name': 'phone_addition', 'value': '1'},
                {'name': 'cost_total', 'value': '12345.678'},
                {
                    'name': 'home_coord',
                    'value': '{"arbitrary_key2": "arbitrary_value2"}',
                },
                {'name': 'date_drive', 'value': '1355314332000'},
                {'name': 'category', 'value': 'some other text'},
                {'name': 'clid', 'value': '1234567'},
                {'name': 'rule_type_name', 'value': 'Яндекс.Корпоративный'},
                {'name': 'flags', 'value': r'{test,test1}'},
                {'name': 'order_id', 'value': 'order_id0'},
            ],
        },
    }
    alias_2 = {
        'method': 'insert',
        'received_ts': 100500,
        'destination': {'table_name': 'orders_0', 'shard_number': 0},
        'body': {
            'park_id': 'park_1',
            'alias_id': 'alias_2',
            'number': 2,
            'date_create': utils.date_to_ms(datetime.datetime.now(tz=None)),
            'date_booking': utils.date_to_ms(datetime.datetime.now(tz=None)),
            'order_fields': [
                {'name': 'phone_addition', 'value': '1'},
                {'name': 'cost_total', 'value': '12345.678'},
                {
                    'name': 'home_coord',
                    'value': '{"arbitrary_key2": "arbitrary_value2"}',
                },
                {'name': 'date_drive', 'value': '1355314332000'},
                {'name': 'category', 'value': 'some other text'},
                {'name': 'clid', 'value': '1234567'},
                {'name': 'rule_type_name', 'value': 'Яндекс.Корпоративный'},
                {'name': 'flags', 'value': r'{}'},
            ],
        },
    }
    alias_3 = {
        'method': 'insert',
        'received_ts': utils.date_to_ms(datetime.datetime.now(tz=None)),
        'destination': {'table_name': 'orders_0', 'shard_number': 0},
        'body': {
            'park_id': 'park_1',
            'alias_id': 'alias_3',
            'number': 3,
            'date_create': utils.date_to_ms(datetime.datetime.now(tz=None)),
            'date_booking': utils.date_to_ms(datetime.datetime.now(tz=None)),
            'order_fields': [
                {'name': 'phone_addition', 'value': '1'},
                {'name': 'cost_total', 'value': '12345.678'},
                {
                    'name': 'home_coord',
                    'value': '{"arbitrary_key2": "arbitrary_value2"}',
                },
                {'name': 'date_drive', 'value': '1355314332000'},
                {'name': 'category', 'value': 'some other text'},
                {'name': 'clid', 'value': '1234567'},
                {'name': 'rule_type_name', 'value': 'Яндекс.Корпоративный'},
            ],
        },
    }
    alias_1_new = {
        'method': 'update',
        'received_ts': utils.date_to_ms(datetime.datetime.now(tz=None)),
        'destination': {'table_name': 'orders_0', 'shard_number': 0},
        'body': {
            'park_id': 'park_1',
            'alias_id': 'alias_1',
            'order_fields': [
                {'name': 'number', 'value': '3'},
                {
                    'name': 'date_create',
                    'value': str(
                        utils.date_to_ms(datetime.datetime.now(tz=None)),
                    ),
                },
                {
                    'name': 'date_booking',
                    'value': str(
                        utils.date_to_ms(datetime.datetime.now(tz=None)),
                    ),
                },
                {'name': 'phone_addition', 'value': '1'},
            ],
        },
    }

    readers = ['order-patch-reader-1', 'order-patch-reader-2']

    @testpoint('logbroker_commit')
    def _commit(cookie):
        assert cookie == 'cookie'

    @testpoint('order_patch_queue_raw_message_tp')
    def _raw_message_getter(data):
        pass

    @testpoint('order_patch_queue_store_to_pg_tp')
    def _store_to_pg(data):
        pass

    async def _expect_all():
        await _raw_message_getter.wait_call()
        result = await _store_to_pg.wait_call()
        await _commit.wait_call()
        return result['data']['body']['alias_id']

    def _flush_all_tps():
        _commit.flush()
        _raw_message_getter.flush()
        _store_to_pg.flush()

    await taxi_contractor_order_history.enable_testpoints()
    _flush_all_tps()

    _clean_table(pgsql, 'orders_0')

    await taxi_contractor_order_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': readers[0],
                'data': json.dumps(alias_1),
                'topic': '/taxi/contractor-order-history/testing/patch-queue',
                'cookie': 'cookie',
            },
        ),
    )
    result = await _expect_all()
    assert result == alias_1['body']['alias_id']
    _check_insert(pgsql, alias_1)

    await taxi_contractor_order_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': readers[1],
                'data': json.dumps(alias_2),
                'topic': '/taxi/contractor-order-history/testing/patch-queue',
                'cookie': 'cookie',
            },
        ),
    )
    result = await _expect_all()
    assert result == alias_2['body']['alias_id']
    _check_insert(pgsql, alias_2)

    await taxi_contractor_order_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': readers[0],
                'data': json.dumps(alias_3),
                'topic': '/taxi/contractor-order-history/testing/patch-queue',
                'cookie': 'cookie',
            },
        ),
    )
    result = await _expect_all()
    assert result == alias_3['body']['alias_id']
    _check_insert(pgsql, alias_3)

    await taxi_contractor_order_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': readers[0],
                'data': json.dumps(alias_1_new),
                'topic': '/taxi/contractor-order-history/testing/patch-queue',
                'cookie': 'cookie',
            },
        ),
    )
    result = await _expect_all()
    assert result == alias_1_new['body']['alias_id']
    _check_update(pgsql, alias_1_new)


async def test_double_insert(taxi_contractor_order_history, testpoint, pgsql):
    @testpoint('logbroker_commit')
    def _commit(cookie):
        assert cookie == 'cookie'

    @testpoint('order_patch_queue_store_to_pg_tp')
    def _store_to_pg(data):
        pass

    await taxi_contractor_order_history.enable_testpoints()
    _commit.flush()
    _store_to_pg.flush()

    _clean_table(pgsql, 'orders_0')

    msg = {
        'method': 'insert',
        'received_ts': utils.date_to_ms(datetime.datetime.now(tz=None)),
        'destination': {'table_name': 'orders_0', 'shard_number': 0},
        'body': {
            'park_id': 'park_1',
            'alias_id': 'alias_1',
            'number': 1,
            'date_create': utils.date_to_ms(datetime.datetime.now(tz=None)),
            'date_booking': utils.date_to_ms(datetime.datetime.now(tz=None)),
            'order_fields': [{'name': 'cost_total', 'value': '12345.678'}],
        },
    }

    await taxi_contractor_order_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-patch-reader-1',
                'data': json.dumps(msg),
                'topic': '/taxi/contractor-order-history/testing/patch-queue',
                'cookie': 'cookie',
            },
        ),
    )

    await _commit.wait_call()
    await _store_to_pg.wait_call()

    # put the same msg again
    await taxi_contractor_order_history.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'order-patch-reader-1',
                'data': json.dumps(msg),
                'topic': '/taxi/contractor-order-history/testing/patch-queue',
                'cookie': 'cookie',
            },
        ),
    )

    await _commit.wait_call()
    # we don't expect the same msg cause an error
    await _store_to_pg.wait_call()
