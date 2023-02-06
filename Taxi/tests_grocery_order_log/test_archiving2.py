# pylint: disable=C5521

from datetime import timedelta
from datetime import timezone
import json
import os
import random
import secrets
import string

import pytest

from tests_plugins.userver_client import TestsuiteTaskFailed
from testsuite.utils import matching

ARCHIVING_TESTSUITE_TASK_NAME = 'archiving2'

CREATE_ORDER = """
INSERT INTO
    order_log.order_log (
        order_id,
        updated,
        order_state
    )
VALUES (
    %s,
    %s,
    'closed'
)
"""

GET_ORDERS = """
SELECT
    order_id,
    can_be_archived
FROM
    order_log.order_log
"""

GET_SHARE_ID = """
SELECT
    id,
    created_at,
    operation_info,
    share_id,
    last_status_info
FROM
    order_log.yql_operations
"""


@pytest.mark.skip(reason='For local use only')
async def test_periodic_archiving_task_proxy(
        taxi_grocery_order_log, taxi_config, yql,
):
    yql.token = os.environ['YQL_TOKEN']

    taxi_config.set(
        GROCERY_ORDER_LOG_PERIODIC_ARCHIVING_TASK2={
            'enabled': True,
            'cleanup_period': 1,
            'expiration_interval': 2400,  # hours
            'chunk_size': 1000,  # rows to update per pg request
            'verbose_periodic': True,
            'max_order_ids_to_log': 1000,
            'page_limit': 20,
            'disabled_queries': [],
            'status_polling_delay': 1000,  # milliseconds
            'status_polling_total_wait': 3600,  # seconds
            'fetch_delay': 0,  # milliseconds
            'apply_delay': 0,  # milliseconds
        },
    )
    await taxi_grocery_order_log.invalidate_caches()

    await taxi_grocery_order_log.run_task(ARCHIVING_TESTSUITE_TASK_NAME)

    assert yql.proxy_handlers.times_called > 0


@pytest.mark.parametrize('interrupt', [None, 'fetching', 'share_id'])
async def test_periodic_archiving_task(
        taxi_grocery_order_log,
        taxi_config,
        mockserver,
        now,
        load_json,
        pgsql,
        interrupt,
):
    expiration_interval = 2400  # hours
    chunk_size = 1000  # rows to update per pg request
    max_order_ids_to_log = 1000
    page_limit = 20
    disabled_queries = []

    expiration_timepoint = now.replace(tzinfo=timezone.utc) - timedelta(
        hours=expiration_interval,
    )

    taxi_config.set(
        GROCERY_ORDER_LOG_PERIODIC_ARCHIVING_TASK2={
            'enabled': True,
            'cleanup_period': 1,
            'expiration_interval': expiration_interval,
            'chunk_size': chunk_size,
            'verbose_periodic': True,
            'max_order_ids_to_log': max_order_ids_to_log,
            'page_limit': page_limit,
            'disabled_queries': disabled_queries,
            'status_polling_delay': 0,  # milliseconds
            'status_polling_total_wait': 3600,  # seconds
            'fetch_delay': 0,  # milliseconds
            'apply_delay': 0,  # milliseconds
        },
    )
    await taxi_grocery_order_log.invalidate_caches()

    operation_id = secrets.token_hex(12)

    @mockserver.json_handler('/yql/api/v2/operations')
    def operation_handler(request):
        assert request.method == 'POST'
        assert request.json == {
            'content': matching.any_string,
            'action': 'RUN',
            'type': 'SQLv1',
            'parameters': {
                '$input_table': matching.any_string,
                '$older_than': matching.any_string,
                '$page_limit': matching.any_string,
                '$disabled_queries': matching.any_string,
                '$results_limit': matching.any_string,
            },
            'queryTitle': matching.RegexString(r'^YQL: '),
        }
        parameters = request.json['parameters']
        assert json.loads(parameters['$input_table']) == {
            'Data': (
                'home/lavka/testing/replica/postgres'
                '/order_log/raw/grocery_order_log_by_id'
            ),
        }
        assert json.loads(parameters['$older_than']) == {
            'Data': str(int(expiration_timepoint.timestamp() * 1000000)),
        }
        assert json.loads(parameters['$page_limit']) == {
            'Data': str(page_limit),
        }
        assert json.loads(parameters['$disabled_queries']) == {'Data': []}
        assert json.loads(parameters['$results_limit']) == {'Data': '1000000'}
        response = {'id': operation_id, 'status': 'PENDING'}
        return mockserver.make_response(json=response, status=200)

    if interrupt == 'share_id':
        # https://postgrespro.ru/list/thread-id/2151567 since 2012
        share_id = ''
    else:
        charset = string.ascii_letters + string.digits + '_-'
        random_part = ''.join(random.choice(charset) for _ in range(42))
        share_id = f'Yo{random_part}='

    @mockserver.handler(
        r'/yql/api/v2/operations/(?P<op_id>\w+)/share_id', regex=True,
    )
    def share_id_handler(request, op_id):
        assert request.method == 'GET'
        assert op_id == operation_id

        if interrupt == 'share_id':
            return mockserver.make_response(status=200)

        return mockserver.make_response(response=share_id, status=200)

    operation_statuses = ['PENDING', 'RUNNING']

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<op_id>\w+)', regex=True,
    )
    def status_handler(request, op_id):
        assert request.method == 'GET'
        assert op_id == operation_id

        if operation_statuses:
            status = operation_statuses.pop(0)
        else:
            status = 'COMPLETED'

        response = {'id': operation_id, 'status': status}
        return mockserver.make_response(json=response, status=200)

    def gen_order_id():
        return f'{secrets.token_hex(16)}-grocery'

    db = pgsql['grocery_order_log']
    cursor = db.cursor()

    def create_order(order_id, updated=None):
        if updated is None:
            updated = now.replace(tzinfo=timezone.utc)

        cursor.execute(CREATE_ORDER, [order_id, updated])

    results_response = load_json('yql_results_response.json')
    results_response['id'] = operation_id

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<op_id>\w+)/results', regex=True,
    )
    def results_handler(request, op_id):
        assert request.method == 'GET'
        assert op_id == operation_id
        assert request.query_string == b'filters=DATA'

        return mockserver.make_response(json=results_response, status=200)

    table_data = {}
    table_data_call_count = 0

    not_expired_orders = set()
    not_first_page_orders = set()

    data = results_response['data'][0]
    assert data['Label'] == 'not_first_page'
    write = data['Write'][0]
    ref = write['Ref'][0]
    reference = '.'.join(ref['Reference'][1:])  # cluster.table_path
    assert reference not in table_data
    count = 3 * len(write['Data']) + 0
    order_ids = [gen_order_id() for _ in range(count)]
    for order_id in order_ids:
        create_order(order_id)
        not_first_page_orders.add(order_id)
    table_data_call_count += 3 + 1
    table_data[reference] = order_ids

    expired_orders = not_first_page_orders.copy()

    data = results_response['data'][1]
    assert data['Label'] == 'old_market_orders'
    write = data['Write'][0]
    ref = write['Ref'][0]
    reference = '.'.join(ref['Reference'][1:])  # cluster.table_path
    assert reference not in table_data
    count = 2 * len(write['Data']) + 1
    order_ids = [gen_order_id() for _ in range(count)]
    for order_id in order_ids:
        if (len(expired_orders) + len(not_expired_orders)) % 2 == 0:
            create_order(order_id, expiration_timepoint - timedelta(minutes=1))
            expired_orders.add(order_id)
        else:
            create_order(order_id, expiration_timepoint + timedelta(minutes=1))
            not_expired_orders.add(order_id)
    table_data_call_count += 2 + 1
    table_data[reference] = order_ids

    fetched_orders = set()

    @mockserver.json_handler('/yql/api/v2/table_data_post')
    def table_data_handler(request):
        assert request.method == 'POST'

        if interrupt == 'fetching':
            if all(
                    [
                        s & fetched_orders
                        for s in [
                            expired_orders,
                            not_expired_orders,
                            not_first_page_orders,
                        ]
                    ],
            ):
                return mockserver.make_response(status=500)

        reference = request.json['cluster'] + '.' + request.json['path']
        offset = request.json['offset']
        limit = request.json['limit']
        span = table_data[reference][offset : offset + limit]
        fetched_orders.update(set(span))

        response = load_json('yql_table_data_post_response.json')
        response[0]['Data'] = [[order_id] for order_id in span]
        return mockserver.make_response(json=response, status=200)

    try:
        await taxi_grocery_order_log.run_task(ARCHIVING_TESTSUITE_TASK_NAME)
    except TestsuiteTaskFailed:
        assert interrupt == 'fetching'

    cursor.execute(GET_SHARE_ID)
    rows = cursor.fetchall()
    operation_info = {'id': operation_id, 'status': 'PENDING'}
    last_status_info = {'id': operation_id, 'status': 'COMPLETED'}
    assert rows == [
        (
            operation_id,
            now.replace(tzinfo=timezone.utc),
            operation_info,
            share_id,
            last_status_info,
        ),
    ]

    assert not operation_statuses

    assert operation_handler.times_called == 1
    assert share_id_handler.times_called == 1
    assert status_handler.times_called == 3
    assert results_handler.times_called == 1
    if interrupt == 'fetching':
        assert table_data_handler.times_called > 2
        assert table_data_handler.times_called < table_data_call_count

        assert fetched_orders

        cursor.execute(GET_ORDERS)
        rows = cursor.fetchall()
        assert (
            set(row[0] for row in rows if row[1])
            == expired_orders & fetched_orders
        )
        assert set(
            row[0] for row in rows if not row[1]
        ) == not_expired_orders | (expired_orders - fetched_orders)
    else:
        assert table_data_handler.times_called == table_data_call_count

        assert fetched_orders == expired_orders | not_expired_orders

        cursor.execute(GET_ORDERS)
        rows = cursor.fetchall()
        assert set(row[0] for row in rows if row[1]) == expired_orders
        assert set(row[0] for row in rows if not row[1]) == not_expired_orders
