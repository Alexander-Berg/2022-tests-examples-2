import datetime
import math

import pytest

SYNC_CONFIG = {
    'enabled': True,
    'greenplum_fetch': {'batch_size': 10000, 'max_age_days': 1},
    'sync_to_catalog_storage': {'enabled': True, 'check_value_changed': False},
}

SYNC_CONFIG_DISABLED_PLACE = {
    'enabled': True,
    'greenplum_fetch': {'batch_size': 10000, 'max_age_days': 1},
    'sync_to_catalog_storage': {'enabled': True, 'check_value_changed': False},
    'excluded_place_ids': [10],
}


def check_synchronization_date(pgsql, date):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT last_known_date FROM eats_place_rating.greenplum_sync;',
    )
    assert cursor.fetchone()[0] == date


def check_ratings_count(pgsql, count):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute('SELECT * FROM eats_place_rating.place_rating_info;')
    ratings = cursor.fetchall()
    assert len(ratings) == count


def check_deltas(pgsql, place_id, deltas, rating=None):
    rating = rating or 'final_rating'
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        f'SELECT {rating}_delta '
        'FROM eats_place_rating.place_rating_info '
        f'WHERE place_id={place_id} '
        'ORDER BY calculated_at;',
    )
    db_deltas = cursor.fetchall()
    assert len(db_deltas) == len(deltas)
    for i, delta in enumerate(deltas):
        assert math.isclose(float(db_deltas[i][0]), delta)


def check_disbled_rating(pgsql, place_id, expected_rating):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        f'SELECT final_rating '
        'FROM eats_place_rating.place_rating_info '
        f'WHERE place_id={place_id} '
        'ORDER BY calculated_at;',
    )
    rating = cursor.fetchone()[0]
    assert math.isclose(float(rating), expected_rating)


def check_stats(pgsql, new, updated, imported):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute('SELECT stats FROM eats_place_rating.greenplum_sync;')

    result = cursor.fetchone()[0]
    assert result['imported_places_num'] == imported
    assert result['new_places_num'] == new
    assert result['updated_places_num'] == updated


def check_cancels_rating_cnt(pgsql, place_id, rating_counts):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        f'SELECT cancel_in_cancel_rating_count '
        'FROM eats_place_rating.place_rating_info '
        f'WHERE place_id={place_id} '
        'ORDER BY calculated_at;',
    )
    db_rating_counts = cursor.fetchall()
    assert len(db_rating_counts) == len(rating_counts)
    for i, count in enumerate(rating_counts):
        assert db_rating_counts[i][0] == count


def check_virtual_rating_cnt(pgsql, place_id, rating_counts):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        f'SELECT virtual_rating_in_user_rating_count '
        'FROM eats_place_rating.place_rating_info '
        f'WHERE place_id={place_id} '
        'ORDER BY calculated_at;',
    )
    db_rating_counts = cursor.fetchall()
    assert len(db_rating_counts) == len(rating_counts)
    for i, count in enumerate(rating_counts):
        assert db_rating_counts[i][0] == count


@pytest.mark.config(EATS_PLACE_RATING_RATINGS_SYNC_CONFIGS=SYNC_CONFIG)
async def test_eats_place_rating_periodic(taxi_eats_place_rating, pgsql):
    await taxi_eats_place_rating.run_periodic_task(
        'sync-rating-from-greenplum-periodic',
    )
    check_synchronization_date(pgsql, datetime.date.today())
    check_deltas(pgsql, 10, [4.9, -0.1], rating='final_rating')
    check_deltas(pgsql, 10, [5.0, 0], rating='user_rating')
    check_deltas(pgsql, 10, [4.5, -0.1], rating='cancel_rating')
    check_cancels_rating_cnt(pgsql, 10, [100, 120])
    check_virtual_rating_cnt(pgsql, 10, [100, 120])


@pytest.mark.config(
    EATS_PLACE_RATING_RATINGS_SYNC_CONFIGS=SYNC_CONFIG_DISABLED_PLACE,
)
@pytest.mark.pgsql(
    'eats_place_rating_gp', files=('pg_eats_place_rating_gp_disabled.sql',),
)
@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_disabled.sql',),
)
async def test_eats_place_rating_periodic_disabled(
        taxi_eats_place_rating, pgsql,
):
    await taxi_eats_place_rating.run_periodic_task(
        'sync-rating-from-greenplum-periodic',
    )
    check_synchronization_date(pgsql, datetime.date.today())
    check_ratings_count(pgsql, 3)
    check_disbled_rating(pgsql, 10, 4.0)
    check_deltas(pgsql, 2, [4.8], rating='final_rating')


@pytest.mark.config(EATS_PLACE_RATING_RATINGS_SYNC_CONFIGS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_place_rating_gp', files=('pg_eats_place_rating_gp_3days.sql',),
)
async def test_sync_ratings_dont_sync_too_old(taxi_eats_place_rating, pgsql):
    await taxi_eats_place_rating.run_periodic_task(
        'sync-rating-from-greenplum-periodic',
    )
    check_synchronization_date(pgsql, datetime.date.today())
    check_ratings_count(pgsql, 2)
    check_deltas(pgsql, 10, [4.9, -0.1], rating='final_rating')
    check_deltas(pgsql, 10, [5.0, 0], rating='user_rating')
    check_deltas(pgsql, 10, [4.5, -0.1], rating='cancel_rating')


@pytest.mark.config(EATS_PLACE_RATING_RATINGS_SYNC_CONFIGS=SYNC_CONFIG)
@pytest.mark.pgsql(
    'eats_place_rating_gp',
    files=('pg_eats_place_rating_gp_continue_update.sql',),
)
@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_continue_update.sql',),
)
async def test_sync_ratings_continue_update(taxi_eats_place_rating, pgsql):
    await taxi_eats_place_rating.run_periodic_task(
        'sync-rating-from-greenplum-periodic',
    )
    check_synchronization_date(pgsql, datetime.date.today())
    check_ratings_count(pgsql, 3)
    check_deltas(pgsql, 10, [4.6, -0.1, -0.1])


@pytest.mark.pgsql(
    'eats_place_rating_gp', files=('pg_eats_place_rating_gp_stats.sql',),
)
@pytest.mark.pgsql(
    'eats_place_rating', files=('pg_eats_place_rating_stats.sql',),
)
@pytest.mark.config(EATS_PLACE_RATING_RATINGS_SYNC_CONFIGS=SYNC_CONFIG)
async def test_sync_ratings_check_stats(taxi_eats_place_rating, pgsql):
    await taxi_eats_place_rating.run_periodic_task(
        'sync-rating-from-greenplum-periodic',
    )
    check_stats(pgsql, 4, 2, 6)
