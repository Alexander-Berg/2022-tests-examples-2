import pytest


def compare_answers(response_a, response_b):
    response_a['points'].sort(key=lambda x: x['id'])
    for point in response_a['points']:
        point['point_tags'].sort()
    response_b['points'].sort(key=lambda x: x['id'])
    for point in response_b['points']:
        point['point_tags'].sort()
    assert response_a == response_b


@pytest.mark.pgsql(
    'points',
    queries=[
        """
        INSERT INTO points_manager.points
        (lon, lat, iconCaption, titleTankerKey, geohash)
        VALUES ('55.1201', '37.12005', 'Dot 1', 'dot_1.tanker', 'geohash1'),
               ('55.12005', '37.1201', 'Dot 2', 'dot_2.tanker', 'geohash2'),
               ('55.12003', '37.12003', 'Dot 4', NULL, 'geohash3'),
               ('-130.12', '88.03454', 'Dot 3',  'dot_3.tanker', 'geohash4'),
               ('56.0', '38.0', 'Dot 5', NULL, 'geohash5')
        """,
    ],
)
async def test_admin_points(taxi_pickup_points_manager, pgsql, load_json):
    params = {'point': '55.12,37.12', 'radius': '1000'}
    response = await taxi_pickup_points_manager.get(
        '/v1/points', params=params,
    )
    assert response.status_code == 200
    compare_answers(response.json(), load_json('response_points_get.json'))


@pytest.mark.pgsql(
    'points',
    queries=[
        """
        INSERT INTO points_manager.points
        (lon, lat, iconCaption, titleTankerKey, geohash)
        VALUES ('179.9991', '37.12005', 'Dot 1', 'dot_1.tanker', 'geohash1'),
               ('-179.9991', '37.1201', 'Dot 2', NULL, 'geohash2')
        """,
    ],
)
async def test_admin_points_over_180(
        taxi_pickup_points_manager, pgsql, load_json,
):
    params = {'point': '179.999,37.12', 'radius': '1000'}
    response = await taxi_pickup_points_manager.get(
        '/v1/points', params=params,
    )
    assert response.status_code == 200
    compare_answers(
        response.json(), load_json('response_points_get_over_180.json'),
    )


@pytest.mark.translations(
    pickuppoints={'manual_pp_1': {'ru': 'Точечка', 'en': 'Point'}},
)
@pytest.mark.pgsql(
    'points',
    queries=[
        """
        INSERT INTO points_manager.points
        (lon, lat, iconCaption, titleTankerKey, geohash)
        VALUES ('55.1201', '37.12005', 'Dot 1', 'manual_pp_1', 'geohash1')
        """,
    ],
)
@pytest.mark.parametrize(
    'lang, exp_title', [('ru', 'Точечка'), ('en', 'Point')],
)
async def test_admin_points_translation(
        taxi_pickup_points_manager, pgsql, lang, exp_title,
):
    params = {'point': '55.12,37.12', 'radius': '1000'}
    response = await taxi_pickup_points_manager.get(
        '/v1/points', params=params, headers={'X-Request-Language': lang},
    )
    assert response.status_code == 200
    resp_title = response.json()['points'][0]['title']
    assert resp_title == exp_title


@pytest.mark.pgsql(
    'points',
    queries=[
        """
        INSERT INTO points_manager.points
        (lon, lat, iconCaption, titleTankerKey,
        titleFallback, uri, score, geohash)
        VALUES ('56.87754', '37.47502', 'Dot 1',
                'dot_1.tanker', 'Dot 1 title fallback',
                'point1_uri', NULL, 'geohash1'),
               ('45.32212', '-12.87734', 'Dot 2',
                'dot_2.tanker', NULL, 'point2_uri', NULL, 'geohash2'),
               ('-130.12', '88.03454', 'Dot 3',
               'dot_3.tanker', NULL, NULL, NULL, 'geohash3')
        """,
    ],
)
@pytest.mark.translations(
    pickuppoints={'dot_2.tanker': {'ru': 'Точечка', 'en': 'Point'}},
)
@pytest.mark.parametrize(
    'uri, status, lang, exp_title',
    [
        ('point2_uri', 200, 'ru', 'Точечка'),
        ('point2_uri', 200, 'en', 'Point'),
        ('point2_uri', 200, None, None),
        ('no_such_uri', 404, None, None),
    ],
)
async def test_points_find(
        taxi_pickup_points_manager,
        pgsql,
        load_json,
        uri,
        status,
        lang,
        exp_title,
):
    response = await taxi_pickup_points_manager.get(
        '/v1/points/find',
        params={'uri': uri},
        headers={'X-Request-Language': lang} if lang is not None else {},
    )
    assert response.status_code == status
    if status == 200:
        resp_json = response.json()
        resp_title = resp_json.get('title')
        resp_json.pop('title', None)
        assert resp_json == load_json('response_find.json')
        assert resp_title == exp_title


@pytest.mark.pgsql(
    'points',
    queries=[
        """
        INSERT INTO points_manager.points
        (lon, lat, iconCaption, titleTankerKey, geohash, pointTags, uri)
        VALUES ('55.1201', '37.12005', 'Dot 1', 'dot_1.tanker', 'geohash1',
                ARRAY['kPoi']::points_manager.point_tag[], 'uri1'),
               ('55.12005', '37.1201', 'Dot 2', 'dot_2.tanker', 'geohash2',
                ARRAY['kPickup']::points_manager.point_tag[], NULL),
               ('55.12003', '37.12003', 'Dot 4', NULL, 'geohash3',
                ARRAY['kArrivalPoint']::points_manager.point_tag[], 'uri2'),
               ('55.12003', '37.1201', 'Dot 3',  'dot_3.tanker', 'geohash4',
                ARRAY[]::points_manager.point_tag[], NULL)
        """,
    ],
)
@pytest.mark.parametrize(
    'test, skip_tag',
    [
        ('pickup', True),
        ('pickup', False),
        ('poi', False),
        ('arrival_point', False),
    ],
)
async def test_tag_points(
        taxi_pickup_points_manager, pgsql, load_json, test, skip_tag,
):
    params = {'point': '55.12,37.12', 'radius': '1000'}
    if not skip_tag:
        params['point_tags'] = test
    response = await taxi_pickup_points_manager.get(
        '/v1/points', params=params,
    )
    assert response.status_code == 200
    expected_resp = load_json('response_points_get_by_tags.json')
    expected_resp['points'] = [
        point
        for point in expected_resp['points']
        if point['point_tags'] == [test]
    ]
    expected_resp['num_points'] = len(expected_resp['points'])
    for point in expected_resp['points']:
        assert 'poi' not in point['point_tags'] or point['uri']
    compare_answers(response.json(), expected_resp)
