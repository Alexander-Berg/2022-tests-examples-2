async def test_get_stats(
        taxi_eats_place_rating, taxi_eats_place_rating_monitor,
):
    await taxi_eats_place_rating.post(
        '/eats/v1/eats-place-rating/v1/exclude-canceled-orders',
        json={
            'place_id': 123456,
            'order_nrs': ['111-111', '222-222', '333-333'],
            'user_context': 'user',
            'reason': 'because',
        },
    )

    await taxi_eats_place_rating.post(
        '/eats/v1/eats-place-rating/v1/exclude-canceled-orders/restore',
        json={
            'order_nrs': ['111-111'],
            'user_context': 'user2',
            'reason': 'because',
        },
    )

    await taxi_eats_place_rating.run_periodic_task(
        'excluded_cancels_stats_task',
    )
    metrics = await taxi_eats_place_rating_monitor.get_metrics()
    assert metrics['excluded-cancels-stats']['excluded'] == 2
    assert metrics['excluded-cancels-stats']['restored'] == 1
