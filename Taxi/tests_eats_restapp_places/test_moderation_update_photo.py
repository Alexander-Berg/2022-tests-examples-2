IDENTITY = 'fake_identity'
PLACE_ID = 1234


async def test_moderation_update_photo(taxi_eats_restapp_places, pgsql):
    response = await taxi_eats_restapp_places.post(
        '/internal/moderation/update_photo',
        json={'place_id': PLACE_ID, 'avatarnica_identity': IDENTITY},
    )

    assert response.status_code == 204

    cur = pgsql['eats_restapp_places'].dict_cursor()
    cur.execute(
        'SELECT * '
        'FROM eats_restapp_places.pictures '
        'WHERE place_id = {}'.format(PLACE_ID),
    )
    result = cur.fetchone()

    assert result['place_id'] == PLACE_ID
    assert result['avatarnica_identity'] == IDENTITY


async def test_moderation_error(taxi_eats_restapp_places, pgsql):
    response = await taxi_eats_restapp_places.post(
        '/internal/moderation/update_photo',
        json={'place_id': PLACE_ID, 'avatarnica_identity': 12345},
    )

    assert response.status_code == 400
