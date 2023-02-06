NEW_CITY_JSON = {
    '_id': 'Ара-ара',
    'geo_center': [101.2, 101.5],
    'tz': 'Asia/Yerevan',
    'utcoffset': 4.0,
    'tl': [102.1, 101.3],
    'br': [101.1, 101.9],
    'main_class': 'econom',
    'class': ['econom', 'business'],
    'en': 'Ara-ara',
    'quadkeys': [],
    'zoom': 12,
}


async def test_update_city(web_app_client, db):
    response = await web_app_client.post(
        '/api/config/cities/update', json=NEW_CITY_JSON,
    )
    assert response.status == 200

    content = await response.json()
    assert content['response'] == 'ok'

    city = await db.atlas_cities.find_one({'_id': 'Ара-ара'})

    assert city['geo_center'] == NEW_CITY_JSON['geo_center']
    assert city['tl'] == NEW_CITY_JSON['tl']
    assert city['br'] == NEW_CITY_JSON['br']
    assert city['zoom'] == NEW_CITY_JSON['zoom']
    assert city['quadkeys'] == NEW_CITY_JSON['quadkeys']
