import pytest

SYNC_CONFIG = {
    'enabled': True,
    'period': 3600,
    'greenplum_fetch': {'batch_size': 100},
    'transaction_timings': {
        'statement_timeout': 2000,
        'network_timeout': 3000,
    },
}

WATCHDOG_CONFIG = {'interval': 86400}


def check_weights_count(pgsql, count):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute('SELECT count(*) FROM eats_place_rating.feedback_weight;')
    assert cursor.fetchone()[0] == count


def check_place_ids(pgsql, ids):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT DISTINCT(place_id) FROM eats_place_rating.feedback_weight '
        'ORDER BY place_id;',
    )
    db_ids = [db_id[0] for db_id in cursor.fetchall()]
    assert db_ids == ids


def check_feedback_weight(pgsql, weight):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT place_id, order_nr, rating, rating_weight '
        'FROM eats_place_rating.feedback_weight '
        f'WHERE place_id = {weight[0]} AND order_nr = \'{weight[1]}\';',
    )
    assert cursor.fetchone() == weight


@pytest.mark.config(
    EATS_PLACE_RATING_FEEDBACK_WEIGHTS_SYNC_CONFIGS=SYNC_CONFIG,
    EATS_PLACE_RATING_WATCHDOG=WATCHDOG_CONFIG,
)
async def test_eats_place_rating_watchdog(taxi_eats_place_rating, pgsql):
    await taxi_eats_place_rating.run_periodic_task('watchdog-periodic')
    check_weights_count(pgsql, 4)
    check_place_ids(pgsql, [1, 2, 4, 7])
    check_feedback_weight(pgsql, (1, '100-200', 5, 200))
    check_feedback_weight(pgsql, (2, '100-300', 4, 150))
    check_feedback_weight(pgsql, (4, '100-100', 5, 200))
    check_feedback_weight(pgsql, (7, '100-400', 2, 1))
