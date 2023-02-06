# -*- coding: utf-8 -*-

import datetime

import pytest

from tests_driver_metrics_storage import util

# Generated via `tvmknife unittest service -s 111 -d 2001716`
MOCK_TICKET = (
    '3:serv:CBAQ__________9_IgYIbxC0lno:Mq_Uxj0_0uU3TVGgtA9c9sSWyCryh9ngXRS76'
    'Hk0'
    'cKlf1Tx7SPDgwKbB8Wji18-jCGYwCf8kh-hXDiiWUaV2p9hZ5GovU_dTYXiDfnNxzLDL848P'
    'W-V'
    'FYJ-YMi3DFjwA08njKnRQEnzzllwqPN_1aUBM3W6lbgQZ4RaODfkH'
    'R3s'
)


@pytest.mark.now('2019-01-01T00:00:00+0000')
@pytest.mark.config(
    DRIVER_METRICS_STORAGE_CLEANER_SETTINGS={
        'wallet_logs_expire_days': 43,
        'wallet_logs_clean_limit': 500,
        'wallet_logs_clean_repeat': 1,
        'events_expire_days': 7,
        'events_clean_limit': 30,
        'events_clean_repeat': 2,
        'events_logs_partitioned_clean_limit': 30,
        'events_logs_partitioned_clean_repeat': 2,
    },
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 1},
        'type-Z': {'__default__': 22, 'custom': 11},
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_service_dist_cleaner_logs_partitioned(
        taxi_driver_metrics_storage, pgsql, testpoint,
):
    @testpoint('call::service-dist-cleaner')
    def task_testpoint(data):
        pass

    await taxi_driver_metrics_storage.enable_testpoints()

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
            'udid_id)'
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

    await taxi_driver_metrics_storage.run_task('service-dist-cleaner')
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


@pytest.mark.now('2019-03-01T00:00:00+0000')
@pytest.mark.config(
    DRIVER_METRICS_STORAGE_CLEANER_SETTINGS={
        'wallet_logs_expire_days': 43,
        'wallet_logs_clean_limit': 500,
        'wallet_logs_clean_repeat': 1,
        'events_expire_days': 7,
        'events_clean_limit': 30,
        'events_clean_repeat': 2,
        'data_logs_partitioned_clean_limit': 20,
        'data_logs_partitioned_clean_repeat': 2,
    },
    DRIVER_METRICS_STORAGE_EVENTS_TTL={
        '__default__': {'__default__': 1},
        'type-Z': {'__default__': 22, 'custom': 11},
    },
)
@pytest.mark.pgsql('drivermetrics', files=['test.sql'])
async def test_service_dist_cleaner_data_logs_partitioned(
        taxi_driver_metrics_storage, pgsql, testpoint,
):
    @testpoint('call::service-dist-cleaner')
    def task_testpoint(data):
        pass

    await taxi_driver_metrics_storage.enable_testpoints()

    # Insert manually to be sure that old records exist in tables
    util.execute_query('CREATE SEQUENCE data_logs_event_id_test_seq;', pgsql)
    util.execute_query(
        'CREATE SEQUENCE data_logs_unique_r_id_seq '
        'MINVALUE 1 MAXVALUE 1000 CYCLE;',
        pgsql,
    )
    util.execute_query(
        (
            'INSERT INTO data.logs_64_partitioned('
            'event_id,'
            'udid_id,'
            'created,'
            'loyalty_increment,'
            'activity_increment'
            ')'
            '(select nextval(\'data_logs_event_id_test_seq\'),'
            'nextval(\'data_logs_unique_r_id_seq\'),t,10,10 from('
            'SELECT '
            'generate_series(\'2018-12-31T23:59:00\'::TIMESTAMP,'
            ' \'2019-01-01T00:00:59\'::TIMESTAMP,'
            ' \'1 second\') t) p);'
        ),
        pgsql,
    )
    util.execute_query('DROP SEQUENCE data_logs_event_id_test_seq;', pgsql)
    util.execute_query('DROP SEQUENCE data_logs_unique_r_id_seq;', pgsql)

    clear_table_list = ['logs_64_partitioned']
    for table in clear_table_list:
        assert (
            (
                table,
                util.select_named(
                    (
                        'SELECT count(*), min(created), max(created) '
                        + 'FROM data.%s;' % table
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

    await taxi_driver_metrics_storage.run_task('service-dist-cleaner')
    await task_testpoint.wait_call()

    checkres = {
        table: util.select_named(
            (
                'SELECT count(*), min(created), max(created) '
                + 'FROM data.%s' % table
            ),
            pgsql,
        )
        for table in clear_table_list
    }
    expected = {
        table: [
            {
                'count': 80,
                'max': datetime.datetime(2019, 1, 1, 0, 0, 59),
                'min': datetime.datetime(2018, 12, 31, 23, 59, 40),
            },
        ]
        for table in clear_table_list
    }
    assert checkres == expected
