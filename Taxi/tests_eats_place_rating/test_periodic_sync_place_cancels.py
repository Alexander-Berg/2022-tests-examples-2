import pytest

# Testpoints
PREFIX = 'eats_place_rating::sync-place-cancels-from-greenplum-'
TESTPOINT_PROCESS_DEPRECATED_START = PREFIX + 'process-deprecated-start'
TESTPOINT_PROCESS_DEPRECATED = PREFIX + 'process-deprecated'
TESTPOINT_PROCESS_START = PREFIX + 'process-start'
TESTPOINT_PROCESS = PREFIX + 'process'
TESTPOINT_INSERT_GREEN_PLUM_DATA = PREFIX + 'insert-green-plum-data'

DEPRECATED_SYNC_CONFIG = {
    'enabled': True,
    'period': 3600,
    'greenplum_fetch': {'batch_size': 100},
    'transaction_timings': {
        'statement_timeout': 2000,
        'network_timeout': 3000,
    },
    'use_active_places_table': False,
}
SYNC_CONFIG = {
    'enabled': True,
    'period': 3600,
    'greenplum_fetch': {'batch_size': 100},
    'transaction_timings': {
        'statement_timeout': 2000,
        'network_timeout': 3000,
    },
    'use_active_places_table': True,
}


def check_cancels_count(pgsql, count):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute('SELECT count(*) FROM eats_place_rating.place_cancels;')
    assert cursor.fetchone()[0] == count


def check_place_ids(pgsql, ids):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT DISTINCT(place_id) FROM eats_place_rating.place_cancels '
        'ORDER BY place_id;',
    )
    db_ids = [db_id[0] for db_id in cursor.fetchall()]
    assert db_ids == ids


def check_place_cancel(pgsql, cancel):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT place_id, order_nr, '
        'canceled_by_place, canceled_by_place_reason '
        'FROM eats_place_rating.place_cancels '
        f'WHERE place_id = {cancel[0]} AND order_nr = \'{cancel[1]}\';',
    )
    assert cursor.fetchone() == cancel


def check_no_cancel(pgsql, place_id, order_nr):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT place_id, order_nr, '
        'canceled_by_place, canceled_by_place_reason '
        'FROM eats_place_rating.place_cancels '
        f'WHERE place_id = {place_id} AND order_nr = \'{order_nr}\';',
    )
    assert not cursor.fetchall()


@pytest.mark.config(
    EATS_PLACE_RATING_PLACE_CANCELS_SYNC_CONFIGS=DEPRECATED_SYNC_CONFIG,
)
@pytest.mark.pgsql(
    'eats_place_rating',
    files=('pg_eats_place_rating_process_deprecated.sql',),
)
async def test_process_deprecated(taxi_eats_place_rating, pgsql, testpoint):
    @testpoint(TESTPOINT_PROCESS_DEPRECATED_START)
    def point_process_deprecated_start(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_DEPRECATED)
    def point_process_deprecated(arg):
        pass

    @testpoint(TESTPOINT_INSERT_GREEN_PLUM_DATA)
    def point_insert_green_plum_data(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_START)
    def point_process_start(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(
        'sync-place-cancels-from-greenplum-periodic',
    )

    check_cancels_count(pgsql, 2)
    check_place_ids(pgsql, [1, 2])
    check_place_cancel(pgsql, (1, '100-200', True, 'reason for 100-200'))
    check_place_cancel(pgsql, (2, '100-300', True, None))
    # removed because in new data there are no weights for place 3
    check_no_cancel(pgsql, 3, '100-400')
    # removed because this order is not used in new data
    check_no_cancel(pgsql, 1, '100-100')

    assert point_process_deprecated_start.times_called == 1
    assert point_process_deprecated.times_called == 1
    assert point_insert_green_plum_data.times_called == 1
    assert point_process_start.times_called == 0


@pytest.mark.config(EATS_PLACE_RATING_PLACE_CANCELS_SYNC_CONFIGS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_process.sql',),
)
async def test_process(taxi_eats_place_rating, pgsql, testpoint):
    @testpoint(TESTPOINT_PROCESS_DEPRECATED_START)
    def point_process_deprecated_start(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_START)
    def point_process_start(arg):
        pass

    @testpoint(TESTPOINT_PROCESS)
    def point_process(arg):
        pass

    @testpoint(TESTPOINT_INSERT_GREEN_PLUM_DATA)
    def point_insert_green_plum_data(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(
        'sync-place-cancels-from-greenplum-periodic',
    )

    check_cancels_count(pgsql, 2)
    check_place_ids(pgsql, [1, 2])
    check_place_cancel(pgsql, (1, '100-200', True, 'reason for 100-200'))
    check_place_cancel(pgsql, (2, '100-300', True, None))
    # removed because in new data there are no weights for place 3
    check_no_cancel(pgsql, 3, '100-400')
    # removed because this order is not used in new data
    check_no_cancel(pgsql, 1, '100-100')

    assert point_process_deprecated_start.times_called == 0
    assert point_process_start.times_called == 1
    assert point_process.times_called == 1
    assert point_insert_green_plum_data.times_called == 1
