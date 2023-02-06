import pytest


async def test_get_cities(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.post('/api/atlas/cities')
    assert response.status == 200

    content = sorted(await response.json(), key=lambda x: x['_id'])
    assert len(content) == 3

    assert content[0] == {
        '_id': 'Владивосток',
        'br': [43.039337, 132.214104],
        'class': [
            'business',
            'econom',
            'minivan',
            'uberselect',
            'uberx',
            'comfortplus',
            'uberselectplus',
            'cargo',
            'express',
            'courier',
            'promo',
            'night',
        ],
        'en': 'Vladivostok',
        'geo_center': [43.115536, 131.885485],
        'main_class': 'econom',
        'tl': [43.313718, 131.844689],
        'tz': 'Asia/Vladivostok',
        'utcoffset': 10.0,
        'zoom': 11,
    }


async def test_get_cities_with_fields(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.post(
        '/api/atlas/cities',
        json={'fields': ['tz', 'geo_center', '_id', 'tl', 'br']},
    )
    assert response.status == 200

    content = await response.json()
    assert len(content) == 3

    assert content[1] == {
        '_id': 'Казань',
        'br': [55.582464, 49.399344],
        'geo_center': [55.798551, 49.106324],
        'tl': [55.916296, 48.829428],
        'tz': 'Europe/Moscow',
        'utcoffset': 3.0,
    }


async def test_get_cities_miss_tz(web_app_client, atlas_blackbox_mock):
    response = await web_app_client.post(
        '/api/atlas/cities',
        json={'fields': ['geo_center', '_id', 'tl', 'br']},
    )
    assert response.status == 400, await response.text()
    content = await response.json()
    assert content['code'] == '400'
    assert content['message'] == 'There is not "tz" key in "fields" list'


@pytest.mark.parametrize(
    'username, expected_status, expected_cities, is_car_map_request',
    [
        ('omnipotent_user', 200, {'Москва', 'Казань', 'Владивосток'}, False),
        ('city_user', 200, {'Москва', 'Казань'}, False),
        ('car_map_user', 200, {'Москва', 'Казань', 'Владивосток'}, True),
        ('car_map_user', 403, {}, False),
        ('super_user', 200, {'Москва', 'Казань', 'Владивосток'}, False),
        ('restricted_user', 200, {'Москва', 'Казань', 'Владивосток'}, False),
        ('main_user', 200, {'Москва', 'Казань', 'Владивосток'}, False),
        ('nonexisted_user', 403, {}, False),
    ],
)
async def test_get_cities_permissions(
        username,
        expected_status,
        web_app_client,
        atlas_blackbox_mock,
        expected_cities,
        is_car_map_request,
):
    params = {}
    if is_car_map_request:
        params = {'atlas_view': 'car_map'}
    response = await web_app_client.post('/api/atlas/cities', json=params)

    assert response.status == expected_status
    if response.status != 403:
        gotten_cities = {x['_id'] for x in await response.json()}
        assert gotten_cities == expected_cities
