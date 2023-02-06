# flake8: noqa: E501

import re
import uuid

import psycopg2

import pytest

DISTLOCK_NAME = 'scooters-misc-tlog-writer'

DEFAULT_BILLING_ORDERS_RESPONSE = {
    'orders': [
        {'topic': 'topic', 'external_ref': 'external_ref', 'doc_id': 1},
    ],
}


@pytest.mark.config(
    SCOOTERS_MISC_TLOG_WRITER_SETTINGS={
        'sleep-time-ms': 100,
        'enabled': True,
        'billing_client_id': '0000',
        'contract_id': '0000',
        'service_id': 1122,
        'agglomeration': 'MSKc',
        'clears_batch_size': 3,
        'refunds_batch_size': 3,
        'compiled_rides_batch_size': 3,
        'tag_to_mvp_matching': [
            {'scooter_tag': 'scooter', 'mvp': 'MSKc'},
            {'scooter_tag': 'scooter_krasnodar', 'mvp': 'KRRc'},
        ],
    },
)
@pytest.mark.now('2021-06-23T12:00:00+0000')
async def test_simple(taxi_scooters_misc, mockserver, load_json, pgsql):
    @mockserver.json_handler('/billing-orders/v2/process/async')
    def mock_billing_orders(request):
        assert request.json == load_json('billing_orders_request_body.json')

        return mockserver.make_response(
            status=200, json=DEFAULT_BILLING_ORDERS_RESPONSE,
        )

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)
    assert mock_billing_orders.times_called == 1

    cursor = pgsql['scooter_backend'].cursor()
    query = 'SELECT * FROM scooters_misc.drive_tables_cursors;'
    cursor.execute(query)
    cursors_dict = {rec[0]: rec[1] for rec in cursor}
    assert cursors_dict == {
        'compiled_rides': 4,
        'drive_payments': 4,
        'drive_refunds': 4,
    }


@pytest.mark.config(
    SCOOTERS_MISC_TLOG_WRITER_SETTINGS={
        'sleep-time-ms': 100,
        'enabled': True,
        'billing_client_id': '0000',
        'contract_id': '0000',
        'service_id': 1122,
        'agglomeration': 'MSKc',
        'clears_batch_size': 3,
        'refunds_batch_size': 3,
        'compiled_rides_batch_size': 3,
    },
)
async def test_no_new_records(
        taxi_scooters_misc, mockserver, load_json, pgsql,
):
    @mockserver.json_handler('/billing-orders/v2/process/async')
    def mock_billing_orders(request):
        pass

    cursor = pgsql['scooter_backend'].cursor()
    query = """
        UPDATE scooters_misc.drive_tables_cursors
        SET drive_cursor = 100
        WHERE drive_table IN ('drive_payments',
                              'drive_refunds',
                              'compiled_rides');
    """
    cursor.execute(query)

    await taxi_scooters_misc.run_distlock_task(DISTLOCK_NAME)
    assert not mock_billing_orders.has_calls


def get_sql_query(service_source_dir, query):
    with open(service_source_dir / f'src/db/queries/{query}', 'r') as file:
        return re.sub(r'\$\d', '{}', file.read())


def generate_uuid():
    return str(uuid.uuid4())


async def test_sql_get_acutal_compiled_rides(
        taxi_scooters_misc, service_source_dir, pgsql,
):
    krr_scooter_id = generate_uuid()
    krr_session_id = generate_uuid()

    msk_scooter_id = generate_uuid()
    msk_session_id = generate_uuid()

    unknown_session_id = generate_uuid()
    unknown_scooter_id = generate_uuid()

    krr_scooter_tag = 'scooter_krasnodar'
    msk_scooter_tag = 'scooter'

    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    insert_query = f"""
        INSERT INTO compiled_rides
            (history_event_id, history_user_id, history_action, history_timestamp, session_id, object_id, price, duration, start, finish)
        VALUES
            (101, 'stub', 'stub', 0, '{krr_session_id}',     '{krr_scooter_id}',     10000, 250, 0, 100000),
            (102, 'stub', 'stub', 0, '{msk_session_id}',     '{msk_scooter_id}',     10000, 250, 0, 100000),
            (103, 'stub', 'stub', 0, '{unknown_session_id}', '{unknown_scooter_id}', 10000, 250, 0, 100000);

        INSERT INTO car_tags
            (object_id, tag, data)
        VALUES
            ('{krr_scooter_id}', '{krr_scooter_tag}', ''),
            ('{msk_scooter_id}', '{msk_scooter_tag}', '');
    """
    cursor.execute(insert_query)

    query = get_sql_query(service_source_dir, 'get_actual_compiled_rides.sql')
    cursor.execute(query.format(100, 5))
    assert cursor.fetchall() == [
        {
            'finish': 100000,
            'history_event_id': 101,
            'price': 10000,
            'scooter_tag': krr_scooter_tag,
            'session_id': krr_session_id,
        },
        {
            'finish': 100000,
            'history_event_id': 102,
            'price': 10000,
            'scooter_tag': msk_scooter_tag,
            'session_id': msk_session_id,
        },
        {
            'finish': 100000,
            'history_event_id': 103,
            'price': 10000,
            'scooter_tag': (
                # no records for unknown_scooter_id in car_tags table,
                # use default 'scooter' tag
                msk_scooter_tag
            ),
            'session_id': unknown_session_id,
        },
    ]


async def test_sql_get_actual_clears(
        taxi_scooters_misc, service_source_dir, pgsql,
):
    krr_scooter_id = generate_uuid()
    krr_session_id = generate_uuid()
    krr_payment_id = generate_uuid()

    msk_scooter_id = generate_uuid()
    msk_session_id = generate_uuid()
    msk_payment_id = generate_uuid()

    unknown_session_id = generate_uuid()
    unknown_payment_id = generate_uuid()

    krr_scooter_tag = 'scooter_krasnodar'
    msk_scooter_tag = 'scooter'

    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    insert_query = f"""
        INSERT INTO drive_payments
            (id, billing_type, payment_type, pay_method, payment_id, session_id, status, cleared, created_at_ts, last_update_ts)
        VALUES
            (101, 'car_usage', 'yandex_account', 'yandex_account_w/001', '{krr_payment_id}',     '{krr_session_id}',     'cleared', 12000, 0, 0),
            (102, 'car_usage', 'yandex_account', 'yandex_account_w/001', '{msk_payment_id}',     '{msk_session_id}',     'cleared', 12000, 0, 0),
            (103, 'car_usage', 'yandex_account', 'yandex_account_w/001', '{unknown_payment_id}', '{unknown_session_id}', 'cleared', 12000, 0, 0);

        INSERT INTO compiled_rides
            (history_event_id, history_user_id, history_action, history_timestamp, session_id, object_id, price, duration, start, finish)
        VALUES
            (2001, 'stub', 'stub', 0, '{krr_session_id}', '{krr_scooter_id}', 10000, 250, 0, 100000),
            (2002, 'stub', 'stub', 0, '{msk_session_id}', '{msk_scooter_id}', 10000, 250, 0, 100000);

        INSERT INTO car_tags
            (object_id, tag, data)
        VALUES
            ('{krr_scooter_id}', '{krr_scooter_tag}', ''),
            ('{msk_scooter_id}', '{msk_scooter_tag}', '');
    """
    cursor.execute(insert_query)

    query = get_sql_query(service_source_dir, 'get_actual_clears.sql')
    cursor.execute(query.format('\'{yandex_account}\'', 100, 5))
    assert cursor.fetchall() == [
        {
            'cleared': 12000,
            'finish_ts': 100000,
            'id': 101,
            'payment_id': krr_payment_id,
            'payment_type': 'yandex_account',
            'scooter_tag': krr_scooter_tag,
            'session_id': krr_session_id,
        },
        {
            'cleared': 12000,
            'finish_ts': 100000,
            'id': 102,
            'payment_id': msk_payment_id,
            'payment_type': 'yandex_account',
            'scooter_tag': msk_scooter_tag,
            'session_id': msk_session_id,
        },
        {
            'cleared': 12000,
            'finish_ts': (
                # no records for unknown_session_id in compiled_rides table,
                # use value from drive_payments
                0
            ),
            'id': 103,
            'payment_id': unknown_payment_id,
            'payment_type': 'yandex_account',
            'scooter_tag': (
                # no records for unknown_session_id in compiled_rides table,
                # use default 'scooter' tag
                msk_scooter_tag
            ),
            'session_id': unknown_session_id,
        },
    ]


async def test_sql_get_actual_refunds(
        taxi_scooters_misc, service_source_dir, pgsql,
):
    krr_scooter_id = generate_uuid()
    krr_session_id = generate_uuid()
    krr_payment_id = generate_uuid()

    msk_scooter_id = generate_uuid()
    msk_session_id = generate_uuid()
    msk_payment_id = generate_uuid()

    unknown_session_id = generate_uuid()
    unknown_payment_id = generate_uuid()

    krr_scooter_tag = 'scooter_krasnodar'
    msk_scooter_tag = 'scooter'

    cursor = pgsql['scooter_backend'].cursor(
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
    insert_query = f"""
        INSERT INTO public.drive_refunds
            (id, payment_id, session_id, status, sum, created_at_ts, last_update_ts, payment_type)
        VALUES
            (101, '{krr_payment_id}',     '{krr_session_id}',     'success', 12000, 0, 100000, 'card'),
            (102, '{msk_payment_id}',     '{msk_session_id}',     'success', 12000, 0, 100000, 'card'),
            (103, '{unknown_payment_id}', '{unknown_session_id}', 'success', 12000, 0, 100000, 'card');

        INSERT INTO compiled_rides
            (history_event_id, history_user_id, history_action, history_timestamp, session_id, object_id, price, duration, start, finish)
        VALUES
            (3001, 'stub', 'stub', 0, '{krr_session_id}', '{krr_scooter_id}', 10000, 250, 0, 100000),
            (3002, 'stub', 'stub', 0, '{msk_session_id}', '{msk_scooter_id}', 10000, 250, 0, 100000);

        INSERT INTO car_tags
            (object_id, tag, data)
        VALUES
            ('{krr_scooter_id}', '{krr_scooter_tag}', ''),
            ('{msk_scooter_id}', '{msk_scooter_tag}', '');
    """
    cursor.execute(insert_query)

    query = get_sql_query(service_source_dir, 'get_actual_refunds.sql')
    cursor.execute(query.format(100, 5))
    assert cursor.fetchall() == [
        {
            'id': 101,
            'last_update_ts': 100000,
            'payment_id': krr_payment_id,
            'payment_type': 'card',
            'scooter_tag': krr_scooter_tag,
            'session_id': krr_session_id,
            'sum': 12000,
        },
        {
            'id': 102,
            'last_update_ts': 100000,
            'payment_id': msk_payment_id,
            'payment_type': 'card',
            'scooter_tag': msk_scooter_tag,
            'session_id': msk_session_id,
            'sum': 12000,
        },
        {
            'id': 103,
            'last_update_ts': 100000,
            'payment_id': unknown_payment_id,
            'payment_type': 'card',
            'scooter_tag': msk_scooter_tag,
            'session_id': unknown_session_id,
            'sum': 12000,
        },
    ]
