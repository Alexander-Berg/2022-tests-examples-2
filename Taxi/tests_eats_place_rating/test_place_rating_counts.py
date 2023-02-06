import pytest


async def test_place_rating_counts(
        taxi_eats_place_rating, taxi_eats_place_rating_monitor, mocked_time,
):
    await taxi_eats_place_rating.run_periodic_task('place_rating_counts_task')
    mocked_time.sleep(86402)
    await taxi_eats_place_rating.invalidate_caches()

    await taxi_eats_place_rating.run_periodic_task('place_rating_counts_task')
    metrics = await taxi_eats_place_rating_monitor.get_metrics()
    assert metrics['place-rating-counts']['rows_at_table'] == 8
    assert metrics['place-rating-counts']['final_rating_more_3.0'] == 4
    assert metrics['place-rating-counts']['final_rating_more_3.5'] == 4
    assert metrics['place-rating-counts']['final_rating_more_4.2'] == 3
    assert metrics['place-rating-counts']['final_rating_more_4.5'] == 2


@pytest.mark.now('2021-04-26T00:00:00Z')
async def test_place_rating_stats(
        taxi_eats_place_rating, taxi_eats_place_rating_monitor,
):
    await taxi_eats_place_rating.run_periodic_task('place_rating_stats_task')

    metrics = await taxi_eats_place_rating_monitor.get_metrics()

    assert (
        metrics['place-rating-stats']['time_from_last_success_import']
        == 7192800
    )
    assert (
        metrics['place-rating-stats']['time_from_last_known_date'] == 9082800
    )
    assert metrics['place-rating-stats']['imported_places_num'] == 20
    assert metrics['place-rating-stats']['new_places_num'] == 10
    assert metrics['place-rating-stats']['updated_places_num'] == 10


@pytest.mark.now('2021-04-26T00:00:00Z')
async def test_place_rating_snapshots_stats(
        taxi_eats_place_rating, taxi_eats_place_rating_monitor,
):
    await taxi_eats_place_rating.run_periodic_task('place_rating_stats_task')

    metrics = await taxi_eats_place_rating_monitor.get_metrics()

    assert (
        metrics['place-rating-stats'][
            'sync-place-cancels-from-greenplum.imported_objects_num'
        ]
        == 123
    )
    assert (
        metrics['place-rating-stats'][
            'sync-place-cancels-from-greenplum.places_num_with_objects'
        ]
        == 99
    )
    assert (
        metrics['place-rating-stats'][
            'sync-place-cancels-from-greenplum.time_from_last_sync'
        ]
        == 7182000
    )

    assert (
        metrics['place-rating-stats'][
            'sync-place-predefined-comments.imported_objects_num'
        ]
        == 111
    )
    assert (
        metrics['place-rating-stats'][
            'sync-place-predefined-comments.places_num_with_objects'
        ]
        == 24
    )
    assert (
        metrics['place-rating-stats'][
            'sync-place-predefined-comments.time_from_last_sync'
        ]
        == 7182000
    )

    assert (
        metrics['place-rating-stats'][
            'sync-place-cancels-stats.imported_objects_num'
        ]
        == 7564
    )
    assert (
        metrics['place-rating-stats'][
            'sync-place-cancels-stats.places_num_with_objects'
        ]
        == 214
    )
    assert (
        metrics['place-rating-stats'][
            'sync-place-cancels-stats.time_from_last_sync'
        ]
        == 7182000
    )

    assert (
        metrics['place-rating-stats'][
            'sync-feedback-weight-from-greenplum.imported_objects_num'
        ]
        == 8675
    )
    assert (
        metrics['place-rating-stats'][
            'sync-feedback-weight-from-greenplum.places_num_with_objects'
        ]
        == 457
    )
    assert (
        metrics['place-rating-stats'][
            'sync-feedback-weight-from-greenplum.time_from_last_sync'
        ]
        == 7182000
    )
