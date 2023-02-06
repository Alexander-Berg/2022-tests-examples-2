async def test_exclude_order(pgsql, taxi_eats_place_rating):
    response = await taxi_eats_place_rating.post(
        '/eats/v1/eats-place-rating/v1/exclude-canceled-orders',
        json={
            'place_id': 123456,
            'order_nrs': ['111-111'],
            'user_context': 'user',
            'reason': 'because',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'status': 'excluded'}

    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT order_nr, is_deleted, user_context, reason '
        'FROM eats_place_rating.excluded_canceled_orders;',
    )
    cursor_res = cursor.fetchone()
    assert cursor_res == ('111-111', True, 'user', 'because')


async def test_excluded_order_twice(pgsql, taxi_eats_place_rating):
    await taxi_eats_place_rating.post(
        '/eats/v1/eats-place-rating/v1/exclude-canceled-orders',
        json={
            'place_id': 123456,
            'order_nrs': ['111-111', '222-222', '333-333'],
            'user_context': 'user',
            'reason': 'because',
        },
    )
    cursor = pgsql['eats_place_rating'].cursor()
    cursor.execute(
        'SELECT COUNT(*) ' 'FROM eats_place_rating.excluded_canceled_orders;',
    )
    cursor_res = cursor.fetchone()[0]
    assert cursor_res == 3

    await taxi_eats_place_rating.post(
        '/eats/v1/eats-place-rating/v1/exclude-canceled-orders',
        json={
            'place_id': 123456,
            'order_nrs': ['111-111'],
            'user_context': 'user2',
            'reason': 'because 2',
        },
    )
    cursor.execute(
        'SELECT user_context '
        'FROM eats_place_rating.excluded_canceled_orders '
        'WHERE order_nr=\'111-111\'',
    )
    cursor_res = cursor.fetchone()[0]
    assert cursor_res == 'user2'
