async def test_restore_excluded_order(pgsql, taxi_eats_place_rating):
    await taxi_eats_place_rating.post(
        '/eats/v1/eats-place-rating/v1/exclude-canceled-orders',
        json={
            'place_id': 123456,
            'order_nrs': ['111-111'],
            'user_context': 'user',
            'reason': 'because',
        },
    )

    response = await taxi_eats_place_rating.post(
        '/eats/v1/eats-place-rating/v1/exclude-canceled-orders/restore',
        json={
            'order_nrs': ['111-111'],
            'user_context': 'user2',
            'reason': 'because',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'restored'}

    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT order_nr, is_deleted, user_context, reason '
        'FROM eats_place_rating.excluded_canceled_orders;',
    )
    cursor_res = cursor.fetchone()
    assert cursor_res == ('111-111', False, 'user2', 'because')


async def test_restore_excluded_order_twice(pgsql, taxi_eats_place_rating):
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
            'order_nrs': ['111-111', '222-222', '333-333'],
            'user_context': 'user2',
            'reason': 'because2',
        },
    )
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT COUNT(*) ' 'FROM eats_place_rating.excluded_canceled_orders;',
    )
    cursor_res = cursor.fetchone()[0]
    assert cursor_res == 3

    await taxi_eats_place_rating.post(
        '/eats/v1/eats-place-rating/v1/exclude-canceled-orders/restore',
        json={
            'order_nrs': ['111-111'],
            'user_context': 'user3',
            'reason': 'because 3',
        },
    )
    cursor.execute(
        'SELECT user_context, is_deleted '
        'FROM eats_place_rating.excluded_canceled_orders '
        'WHERE order_nr=\'111-111\'',
    )
    cursor_res = cursor.fetchone()
    assert cursor_res == ('user3', False)


async def test_restore_unexcluded_order(pgsql, taxi_eats_place_rating):
    response = await taxi_eats_place_rating.post(
        '/eats/v1/eats-place-rating/v1/exclude-canceled-orders/restore',
        json={
            'order_nrs': ['111-111'],
            'user_context': 'user2',
            'reason': 'because',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'restored'}

    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT * ' 'FROM eats_place_rating.excluded_canceled_orders;',
    )
    cursor_res = cursor.fetchone()
    assert not cursor_res
