# -*- coding: utf-8 -*-

import datetime

import pytest

from tests_rider_metrics_storage import util


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 1},
        'type-Z': {'__default__': 22, 'custom': 11},
    },
    RIDER_METRICS_STORAGE_CLEANER_SETTINGS={
        '__default__': {'clean_limit': 60, 'clean_repeat': 1},
        'events::logs': {'clean_limit': 1000, 'clean_repeat': 1},
        'events::tokens': {'clean_limit': 100, 'clean_repeat': 2},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql', 'test.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_service_dist_cleaner(
        taxi_rider_metrics_storage, pgsql, testpoint,
):
    @testpoint('call::service-dist-cleaner')
    def task_testpoint(data):
        pass

    await taxi_rider_metrics_storage.enable_testpoints()

    # Insert manually to be sure that old records is exists in tables
    util.execute_query(
        (
            'INSERT INTO events.tokens (token,deadline) VALUES'
            + '(\'eid-1\',\'2000-01-01T00:00:00\'),'
            + '(\'eid-2\',\'2000-01-01T00:00:00\');'
        ),
        pgsql,
    )
    util.execute_query(
        (
            'INSERT INTO events.logs_64_partitioned (event_id,unique_rider_id,'
            + 'event_type_id,tariff_zone_id,created,'
            + 'deadline,processed,order_id) VALUES'
            + '(1,1001,1,1,\'2000-01-01T00:00:00\',\'2000-01-01T00:00:00\','
            + '\'2000-01-01T00:01:00\',\'order_id\'),'
            + '(2,1002,2,2,\'2000-01-01T00:10:00\',\'2000-01-01T00:00:00\','
            + '\'2000-01-01T00:11:00\',NULL);'
        ),
        pgsql,
    )
    util.execute_query(
        (
            'INSERT INTO events.tickets_64 (unique_rider_id,down_counter,'
            + 'deadline)VALUES'
            + ' (1001,4,\'2000-01-01T00:00:00\'),'
            + ' (1002,4,\'2000-01-01T00:00:00\');'
        ),
        pgsql,
    )

    clear_table_list = ['tokens', 'logs_64_partitioned', 'tickets_64']
    for table in clear_table_list:
        assert (
            (
                table,
                util.select_named(
                    (
                        'SELECT count(*), min(deadline), max(deadline) '
                        + 'FROM events.%s;' % table
                    ),
                    pgsql,
                    table,
                ),
            )
            == (
                table,
                [
                    {
                        'count': 4,
                        'max': datetime.datetime(2100, 1, 1, 0, 0),
                        'min': datetime.datetime(2000, 1, 1, 0, 0),
                    },
                ],
            )
        )

    await taxi_rider_metrics_storage.run_task('service-dist-cleaner')
    await task_testpoint.wait_call()

    checkres = {
        table: util.select_named(
            (
                'SELECT count(*), min(deadline), max(deadline) '
                + 'FROM events.%s' % table
            ),
            pgsql,
        )
        for table in clear_table_list
    }
    expected = {
        table: [
            {
                'count': 2,
                'max': datetime.datetime(2100, 1, 1, 0, 0),
                'min': datetime.datetime(2100, 1, 1, 0, 0),
            },
        ]
        for table in clear_table_list
    }
    assert checkres == expected


@pytest.mark.config(
    RIDER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 1},
        'type-Z': {'__default__': 22, 'custom': 11},
    },
    RIDER_METRICS_STORAGE_CLEANER_SETTINGS={
        '__default__': {'clean_limit': 60, 'clean_repeat': 1},
        'events::logs_64_partitioned': {'clean_limit': 30, 'clean_repeat': 2},
    },
)
@pytest.mark.pgsql('dbridermetrics', files=['common.sql'])
@pytest.mark.now('2019-01-01T00:00:00+0000')
async def test_service_dist_cleaner_logs_partitioned(
        taxi_rider_metrics_storage, pgsql, testpoint,
):
    @testpoint('call::service-dist-cleaner')
    def task_testpoint(data):
        pass

    await taxi_rider_metrics_storage.enable_testpoints()

    # Insert manually to be sure that old records exist in tables
    util.execute_query('CREATE SEQUENCE events_logs_event_id_test_seq;', pgsql)
    util.execute_query(
        'CREATE SEQUENCE events_logs_unique_r_id_seq '
        'MINVALUE 1 MAXVALUE 1000 CYCLE;',
        pgsql,
    )
    util.execute_query(
        (
            'INSERT INTO events.logs_64_partitioned(event_id,'
            'event_type_id,'
            'order_id,'
            'tariff_zone_id,'
            'created,'
            'deadline,'
            'processed,'
            'unique_rider_id)'
            '(select nextval(\'events_logs_event_id_test_seq\'),'
            '1001,1,2,t,t,t,nextval(\'events_logs_unique_r_id_seq\') from('
            'SELECT '
            'generate_series(\'2018-12-31T23:59:00\'::TIMESTAMP,'
            ' \'2019-01-01T00:00:59\'::TIMESTAMP,'
            ' \'1 second\') t) p);'
        ),
        pgsql,
    )
    util.execute_query('DROP SEQUENCE events_logs_event_id_test_seq;', pgsql)
    util.execute_query('DROP SEQUENCE events_logs_unique_r_id_seq;', pgsql)

    clear_table_list = ['logs_64_partitioned']
    for table in clear_table_list:
        assert (
            (
                table,
                util.select_named(
                    (
                        'SELECT count(*), min(deadline), max(deadline) '
                        + 'FROM events.%s;' % table
                    ),
                    pgsql,
                ),
            )
            == (
                table,
                [
                    {
                        'count': 120,
                        'max': datetime.datetime(2019, 1, 1, 0, 0, 59),
                        'min': datetime.datetime(2018, 12, 31, 23, 59, 0),
                    },
                ],
            )
        )

    await taxi_rider_metrics_storage.run_task('service-dist-cleaner')
    await task_testpoint.wait_call()

    checkres = {
        table: util.select_named(
            (
                'SELECT count(*), min(deadline), max(deadline) '
                + 'FROM events.%s' % table
            ),
            pgsql,
        )
        for table in clear_table_list
    }
    expected = {
        table: [
            {
                'count': 60,
                'max': datetime.datetime(2019, 1, 1, 0, 0, 59),
                'min': datetime.datetime(2019, 1, 1, 0, 0, 0),
            },
        ]
        for table in clear_table_list
    }
    assert checkres == expected
