import pytest

# Testpoints
PREFIX = 'eats_place_rating::sync-place-predefined-comments-'
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


def check_stats_count(pgsql, count):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT count(*) ' 'FROM eats_place_rating.predefined_comments_stats;',
    )
    assert cursor.fetchone()[0] == count


def check_place_ids(pgsql, ids):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT DISTINCT(place_id) '
        'FROM eats_place_rating.predefined_comments_stats '
        'ORDER BY place_id;',
    )
    db_ids = [db_id[0] for db_id in cursor.fetchall()]
    assert db_ids == ids


def check_stats(pgsql, stat):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT place_id, predefined_comment, '
        'comments_count, comment_type '
        'FROM eats_place_rating.predefined_comments_stats '
        f'WHERE place_id = {stat[0]} AND predefined_comment = \'{stat[1]}\';',
    )
    assert cursor.fetchone() == stat


def check_no_stats(pgsql, place_id):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT * '
        'FROM eats_place_rating.predefined_comments_stats '
        f'WHERE place_id = {place_id};',
    )
    assert not cursor.fetchall()


@pytest.mark.config(
    EATS_PLACE_RATING_PREDEFINED_COMMENTS_SYNC_CONFIGS=DEPRECATED_SYNC_CONFIG,
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
        'sync-place-predefined-comments-periodic',
    )

    check_stats_count(pgsql, 3)
    check_place_ids(pgsql, [1, 2])
    check_stats(pgsql, (1, 'predefined comment 1', 4, 'dislike'))
    check_stats(pgsql, (2, 'predefined comment 2', 6, 'like'))
    check_stats(pgsql, (2, 'predefined comment 21', 7, 'dislike'))
    # removed because in new data there are no weights for place 3
    check_no_stats(pgsql, 3)

    assert point_process_deprecated_start.times_called == 1
    assert point_process_deprecated.times_called == 1
    assert point_insert_green_plum_data.times_called == 1
    assert point_process_start.times_called == 0


@pytest.mark.config(
    EATS_PLACE_RATING_PREDEFINED_COMMENTS_SYNC_CONFIGS=SYNC_CONFIG,
)
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
        'sync-place-predefined-comments-periodic',
    )

    check_stats_count(pgsql, 3)
    check_place_ids(pgsql, [1, 2])
    check_stats(pgsql, (1, 'predefined comment 1', 4, 'dislike'))
    check_stats(pgsql, (2, 'predefined comment 2', 6, 'like'))
    check_stats(pgsql, (2, 'predefined comment 21', 7, 'dislike'))
    # removed because in new data there are no weights for place 3
    check_no_stats(pgsql, 3)

    assert point_process_deprecated_start.times_called == 0
    assert point_process_start.times_called == 1
    assert point_process.times_called == 1
    assert point_insert_green_plum_data.times_called == 1
