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

SYNC_TIME = '2021-04-26T00:00:00+00:00'


def check_snapshot_stats(
        pgsql, key_id, imported, places_num_with_objects, sync,
):
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT stats'
        ' FROM eats_place_rating.greenplum_sync'
        f' WHERE id = \'{key_id}\';',
    )

    result = cursor.fetchone()[0]
    assert result['imported_objects_num'] == imported
    assert result['places_num_with_objects'] == places_num_with_objects
    assert result['last_sync'] == sync


@pytest.mark.now(SYNC_TIME)
@pytest.mark.config(EATS_PLACE_RATING_CANCELS_STATS_SYNC_CONFIGS=SYNC_CONFIG)
async def test_eats_place_rating_sync_cancel_reasons_snapshots_stats(
        taxi_eats_place_rating, pgsql,
):
    await taxi_eats_place_rating.run_periodic_task(
        'sync-place-cancels-stats-periodic',
    )
    check_snapshot_stats(pgsql, 'sync-place-cancels-stats', 7, 6, SYNC_TIME)


@pytest.mark.now(SYNC_TIME)
@pytest.mark.config(
    EATS_PLACE_RATING_FEEDBACK_WEIGHTS_SYNC_CONFIGS=SYNC_CONFIG,
)
async def test_eats_place_rating_sync_feedback_weight_snapshots_stats(
        taxi_eats_place_rating, pgsql,
):
    await taxi_eats_place_rating.run_periodic_task(
        'sync-feedback-weight-from-greenplum-periodic',
    )
    check_snapshot_stats(
        pgsql, 'sync-feedback-weight-from-greenplum', 7, 5, SYNC_TIME,
    )


@pytest.mark.now(SYNC_TIME)
@pytest.mark.config(EATS_PLACE_RATING_PLACE_CANCELS_SYNC_CONFIGS=SYNC_CONFIG)
async def test_eats_place_rating_sync_cancels_from_gp_snapshots_stats(
        taxi_eats_place_rating, pgsql,
):
    await taxi_eats_place_rating.run_periodic_task(
        'sync-place-cancels-from-greenplum-periodic',
    )
    check_snapshot_stats(
        pgsql, 'sync-place-cancels-from-greenplum', 8, 5, SYNC_TIME,
    )


@pytest.mark.now(SYNC_TIME)
@pytest.mark.config(
    EATS_PLACE_RATING_PREDEFINED_COMMENTS_SYNC_CONFIGS=SYNC_CONFIG,
)
async def test_eats_place_rating_sync_predefined_comments_snapshots_stats(
        taxi_eats_place_rating, pgsql,
):
    await taxi_eats_place_rating.run_periodic_task(
        'sync-place-predefined-comments-periodic',
    )
    check_snapshot_stats(
        pgsql, 'sync-place-predefined-comments', 10, 6, SYNC_TIME,
    )
