import pytest

# Testpoints
PREFIX = 'eats_place_rating::sync-place-cancels-stats-'
TESTPOINT_PROCESS_DEPRECATED_START = PREFIX + 'process-deprecated-start'
TESTPOINT_PROCESS_DEPRECATED = PREFIX + 'process-deprecated'
TESTPOINT_PROCESS_START = PREFIX + 'process-start'
TESTPOINT_PROCESS = PREFIX + 'process'
TESTPOINT_INSERT_GREEN_PLUM_DATA = PREFIX + 'insert-green-plum-data'

DEFAULT_PERIOD = 3600
DEFAULT_GREENPLUM_FETCH = {'batch_size': 100}
DEFAULT_TRANSACTION_TIMINGS = {
    'statement_timeout': 2000,
    'network_timeout': 3000,
}
DEPRECATED_SYNC_CONFIG = {
    'enabled': True,
    'period': DEFAULT_PERIOD,
    'greenplum_fetch': DEFAULT_GREENPLUM_FETCH,
    'transaction_timings': DEFAULT_TRANSACTION_TIMINGS,
    'use_active_places_table': False,
}
SYNC_CONFIG = {
    'enabled': True,
    'period': DEFAULT_PERIOD,
    'greenplum_fetch': DEFAULT_GREENPLUM_FETCH,
    'transaction_timings': DEFAULT_TRANSACTION_TIMINGS,
    'use_active_places_table': True,
}


def check_stats_count(pgsql, count):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT count(*) ' 'FROM eats_place_rating.place_cancels_stats;',
    )
    assert cursor.fetchone()[0] == count


def check_place_ids(pgsql, ids):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT DISTINCT(place_id) '
        'FROM eats_place_rating.place_cancels_stats '
        'ORDER BY place_id;',
    )
    db_ids = [db_id[0] for db_id in cursor.fetchall()]
    assert db_ids == ids


def check_stats(pgsql, stat):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT place_id, cancel_reason, '
        'cancel_count '
        'FROM eats_place_rating.place_cancels_stats '
        f'WHERE place_id = {stat[0]} AND cancel_reason = \'{stat[1]}\';',
    )
    assert cursor.fetchone() == stat


def check_no_stats(pgsql, place_id):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT * '
        'FROM eats_place_rating.place_cancels_stats '
        f'WHERE place_id = {place_id};',
    )
    assert not cursor.fetchall()


@pytest.mark.config(
    EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS={
        'enabled': False,
        'period': DEFAULT_PERIOD,
        'greenplum_fetch': DEFAULT_GREENPLUM_FETCH,
        'transaction_timings': DEFAULT_TRANSACTION_TIMINGS,
        'use_active_places_table': False,
    },
)
async def test_process_deprecated_disabled(taxi_eats_place_rating, testpoint):
    @testpoint(TESTPOINT_PROCESS_DEPRECATED_START)
    def point_process_deprecated_start(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_START)
    def point_process_start(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(
        'sync-place-cancels-stats-periodic',
    )

    assert point_process_deprecated_start.times_called == 0
    assert point_process_start.times_called == 0


@pytest.mark.config(
    EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS=DEPRECATED_SYNC_CONFIG,
)
async def test_process_deprecated_empty_place_ids(
        taxi_eats_place_rating, testpoint,
):
    @testpoint(TESTPOINT_PROCESS_DEPRECATED_START)
    def point_process_deprecated_start(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_DEPRECATED)
    def point_process_deprecated(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_START)
    def point_process_start(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(
        'sync-place-cancels-stats-periodic',
    )

    assert point_process_deprecated_start.times_called == 1
    assert point_process_deprecated.times_called == 0
    assert point_process_start.times_called == 0


@pytest.mark.config(
    EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS=DEPRECATED_SYNC_CONFIG,
)
@pytest.mark.pgsql(
    'eats_place_rating',
    files=('pg_eats_place_rating_process_deprecated.sql',),
)
async def test_process_deprecated_empty_gp(
        taxi_eats_place_rating, pgsql, testpoint,
):
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
        'sync-place-cancels-stats-periodic',
    )

    check_stats_count(pgsql, 0)

    assert point_process_deprecated_start.times_called == 1
    assert point_process_deprecated.times_called == 1
    assert point_insert_green_plum_data.times_called == 0
    assert point_process_start.times_called == 0


@pytest.mark.config(
    EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS=DEPRECATED_SYNC_CONFIG,
)
@pytest.mark.pgsql(
    'eats_place_rating',
    files=('pg_eats_place_rating_process_deprecated.sql',),
)
@pytest.mark.pgsql(
    'eats_place_rating_gp',
    files=('pg_eats_place_rating_cancel_reasons_stats_gp.sql',),
)
async def test_process_deprecated_simple(
        taxi_eats_place_rating, pgsql, testpoint,
):
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
        'sync-place-cancels-stats-periodic',
    )

    check_stats_count(pgsql, 2)
    check_place_ids(pgsql, [1, 2])
    check_stats(pgsql, (1, 'reason 1', 4))
    check_stats(pgsql, (2, 'reason 2', 6))
    # removed because in new data there are no weights for place 3
    check_no_stats(pgsql, 3)

    assert point_process_deprecated_start.times_called == 1
    assert point_process_deprecated.times_called == 1
    assert point_insert_green_plum_data.times_called == 1
    assert point_process_start.times_called == 0


@pytest.mark.config(
    EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS={
        'enabled': True,
        'period': DEFAULT_PERIOD,
        'greenplum_fetch': {'batch_size': 1},
        'transaction_timings': DEFAULT_TRANSACTION_TIMINGS,
        'use_active_places_table': False,
    },
)
@pytest.mark.pgsql(
    'eats_place_rating',
    files=('pg_eats_place_rating_process_deprecated.sql',),
)
@pytest.mark.pgsql(
    'eats_place_rating_gp',
    files=('pg_eats_place_rating_cancel_reasons_stats_gp.sql',),
)
async def test_process_deprecated_complex(
        taxi_eats_place_rating, pgsql, testpoint,
):
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
        'sync-place-cancels-stats-periodic',
    )

    check_stats_count(pgsql, 2)
    check_place_ids(pgsql, [1, 2])
    check_stats(pgsql, (1, 'reason 1', 4))
    check_stats(pgsql, (2, 'reason 2', 6))
    # removed because in new data there are no weights for place 3
    check_no_stats(pgsql, 3)

    assert point_process_deprecated_start.times_called == 1
    assert point_process_deprecated.times_called == 3
    assert point_insert_green_plum_data.times_called == 2
    assert point_process_start.times_called == 0


@pytest.mark.config(
    EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS={
        'enabled': False,
        'period': DEFAULT_PERIOD,
        'greenplum_fetch': DEFAULT_GREENPLUM_FETCH,
        'transaction_timings': DEFAULT_TRANSACTION_TIMINGS,
        'use_active_places_table': True,
    },
)
async def test_process_disabled(taxi_eats_place_rating, testpoint):
    @testpoint(TESTPOINT_PROCESS_DEPRECATED_START)
    def point_process_deprecated_start(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_START)
    def point_process_start(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(
        'sync-place-cancels-stats-periodic',
    )

    assert point_process_deprecated_start.times_called == 0
    assert point_process_start.times_called == 0


@pytest.mark.config(EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS=SYNC_CONFIG)
async def test_process_empty_place_ids(taxi_eats_place_rating, testpoint):
    @testpoint(TESTPOINT_PROCESS_DEPRECATED_START)
    def point_process_deprecated_start(arg):
        pass

    @testpoint(TESTPOINT_PROCESS_START)
    def point_process_start(arg):
        pass

    @testpoint(TESTPOINT_PROCESS)
    def point_process(arg):
        pass

    await taxi_eats_place_rating.run_periodic_task(
        'sync-place-cancels-stats-periodic',
    )

    assert point_process_deprecated_start.times_called == 0
    assert point_process_start.times_called == 1
    assert point_process.times_called == 0


@pytest.mark.config(EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_process.sql',),
)
async def test_process_empty_gp(taxi_eats_place_rating, pgsql, testpoint):
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
        'sync-place-cancels-stats-periodic',
    )

    check_stats_count(pgsql, 0)

    assert point_process_deprecated_start.times_called == 0
    assert point_process_start.times_called == 1
    assert point_process.times_called == 1
    assert point_insert_green_plum_data.times_called == 0


@pytest.mark.config(EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_process.sql',),
)
@pytest.mark.pgsql(
    'eats_place_rating_gp',
    files=('pg_eats_place_rating_cancel_reasons_stats_gp.sql',),
)
async def test_process_simple(taxi_eats_place_rating, pgsql, testpoint):
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
        'sync-place-cancels-stats-periodic',
    )

    check_stats_count(pgsql, 2)
    check_place_ids(pgsql, [1, 2])
    check_stats(pgsql, (1, 'reason 1', 4))
    check_stats(pgsql, (2, 'reason 2', 6))
    # removed because in new data there are no weights for place 3
    check_no_stats(pgsql, 3)

    assert point_process_deprecated_start.times_called == 0
    assert point_process_start.times_called == 1
    assert point_process.times_called == 1
    assert point_insert_green_plum_data.times_called == 1


@pytest.mark.config(
    EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS={
        'enabled': True,
        'period': DEFAULT_PERIOD,
        'greenplum_fetch': {'batch_size': 1},
        'transaction_timings': DEFAULT_TRANSACTION_TIMINGS,
        'use_active_places_table': True,
    },
)
@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_process.sql',),
)
@pytest.mark.pgsql(
    'eats_place_rating_gp',
    files=('pg_eats_place_rating_cancel_reasons_stats_gp.sql',),
)
async def test_process_complex(taxi_eats_place_rating, pgsql, testpoint):
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
        'sync-place-cancels-stats-periodic',
    )

    check_stats_count(pgsql, 2)
    check_place_ids(pgsql, [1, 2])
    check_stats(pgsql, (1, 'reason 1', 4))
    check_stats(pgsql, (2, 'reason 2', 6))
    # removed because in new data there are no weights for place 3
    check_no_stats(pgsql, 3)

    assert point_process_deprecated_start.times_called == 0
    assert point_process_start.times_called == 1
    assert point_process.times_called == 3
    assert point_insert_green_plum_data.times_called == 2
