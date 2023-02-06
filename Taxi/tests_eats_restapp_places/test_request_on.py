import psycopg2


async def test_create_request_on(taxi_eats_restapp_places, pgsql):
    cur = pgsql['eats_restapp_places'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    place_id = 1128

    url = '/internal/places/v1/create_request_on'
    params = {'place_id': str(place_id)}
    _ = await taxi_eats_restapp_places.post(url, params=params, json={})

    cur.execute(
        'SELECT * '
        'FROM eats_restapp_places.switching_on_requested '
        'WHERE place_id = {!r}'.format(place_id),
    )
    place_added = cur.fetchone()
    assert place_added is not None
    assert place_added['place_id'] == place_id


async def test_delete_request_on(taxi_eats_restapp_places, pgsql):
    cur = pgsql['eats_restapp_places'].cursor(
        cursor_factory=psycopg2.extras.DictCursor,
    )
    place_id = 1129

    cur.execute(
        'INSERT INTO eats_restapp_places.switching_on_requested ('
        'place_id, created_at, updated_at'
        ') '
        'VALUES ({!r}, NOW(), NOW()) '.format(place_id)
        + 'ON CONFLICT (place_id) DO '
        'UPDATE SET updated_at = NOW()',
    )

    url = '/internal/places/v1/delete_request_on'
    params = {'place_id': str(place_id)}
    _ = await taxi_eats_restapp_places.post(url, params=params, json={})

    cur.execute(
        'SELECT * '
        'FROM eats_restapp_places.switching_on_requested '
        'WHERE place_id = {!r}'.format(place_id),
    )
    place_deleted = cur.fetchone()
    assert place_deleted is None
