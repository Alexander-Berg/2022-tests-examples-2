import pytest


def compare_answers(response_a, response_b):
    response_a['points'].sort(key=lambda x: x['id'])
    for point in response_a['points']:
        point['point_tags'].sort()
    response_b['points'].sort(key=lambda x: x['id'])
    for point in response_b['points']:
        point['point_tags'].sort()
    assert response_a == response_b


async def test_admin_points_unique(taxi_pickup_points_manager, load_json):
    response = await taxi_pickup_points_manager.post(
        '/v1/admin/points',
        json=load_json('request_admin_post_not_unique.json'),
    )
    assert response.status_code == 200

    response = await taxi_pickup_points_manager.post(
        '/v1/admin/points',
        json=load_json('request_admin_post_not_unique.json'),
    )
    assert response.status_code == 400

    response = await taxi_pickup_points_manager.post(
        '/v1/admin/points', json=load_json('request_admin_post_unique.json'),
    )
    assert response.status_code == 200


async def test_admin_points(taxi_pickup_points_manager, pgsql, load_json):
    response = await taxi_pickup_points_manager.post(
        '/v1/admin/points', json=load_json('small_request_admin_post.json'),
    )
    assert response.status_code == 200
    assert response.json() == load_json('small_response_admin_post.json')

    params = {'id': '3'}
    response = await taxi_pickup_points_manager.delete(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 200

    params = {'bbox': '44.0,-13.0,57.0,38'}
    response = await taxi_pickup_points_manager.get(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 200
    compare_answers(response.json(), load_json('response_admin_get.json'))


async def test_admin_points_get_bad_request(taxi_pickup_points_manager, pgsql):
    # bbox is normalized in constructor to [178, -13.0, 57.0, 38]
    params = {'bbox': '-182.0,-13.0,57.0,38'}
    response = await taxi_pickup_points_manager.get(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 200

    params = {'trash': 'jgksof'}
    response = await taxi_pickup_points_manager.get(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 400

    params = {'bbox': '-82.0,-13.0,38'}
    response = await taxi_pickup_points_manager.get(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'points',
    queries=[
        """
        INSERT INTO points_manager.points
        (lon, lat, iconCaption, titleTankerKey,
        titleFallback, uri, score, geohash)
        VALUES ('56.87754', '37.47502', 'Dot 1',
                'dot_1.tanker', 'Dot 1 title fallback',
                'ytmpp://lon=37.47502,lat=56.87754', NULL, 'geohash1'),
               ('45.32212', '-12.87734', 'Dot 2',
                NULL, NULL, 'point2_uri', NULL, 'geohash2'),
               ('-130.12', '88.03454', 'Dot 3',
               'dot_3.tanker', NULL, NULL, NULL, 'geohash3')
        """,
    ],
)
async def test_admin_points_delete(
        taxi_pickup_points_manager, pgsql, load_json,
):
    params = {'id': '3'}
    response = await taxi_pickup_points_manager.delete(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 200

    params = {'bbox': '-180.0,-90.0,180.0,90.0'}
    response = await taxi_pickup_points_manager.get(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 200
    compare_answers(response.json(), load_json('response_admin_get.json'))


async def test_admin_points_delete_bad_request(
        taxi_pickup_points_manager, pgsql,
):
    params = {'id': '2.44'}
    response = await taxi_pickup_points_manager.delete(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 400

    params = {'trash': 'jgksof'}
    response = await taxi_pickup_points_manager.delete(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 400


@pytest.mark.pgsql(
    'points',
    queries=[
        """
        INSERT INTO points_manager.points
        (lon, lat, iconCaption, geohash)
        VALUES ('56.87754', '37.47502', 'Dot 1', 'geohash1'),
               ('45.32212', '-12.87734', 'Dot 2', 'geohash2'),
               ('-130.12', '88.03454', 'Dot 3', 'geohash3')
        """,
    ],
)
async def test_admin_points_delete_no_such_id(
        taxi_pickup_points_manager, pgsql,
):
    params = {'id': '15'}
    response = await taxi_pickup_points_manager.delete(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 400


async def test_admin_points_post(taxi_pickup_points_manager, pgsql, load_json):
    response = await taxi_pickup_points_manager.post(
        '/v1/admin/points', json=load_json('request_admin_post.json'),
    )
    assert response.status_code == 200
    compare_answers(response.json(), load_json('response_admin_post.json'))


async def test_admin_points_post_bad_request(
        taxi_pickup_points_manager, pgsql, load_json,
):
    response = await taxi_pickup_points_manager.post(
        '/v1/admin/points', json=load_json('bad_request_admin_post.json'),
    )
    assert response.status_code == 400
    params = {'bbox': '-180.0,-90.0,180.0,90.0'}
    response = await taxi_pickup_points_manager.get(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 200
    compare_answers(response.json(), {'num_points': 0, 'points': []})


@pytest.mark.pgsql(
    'points',
    queries=[
        """
        INSERT INTO points_manager.points
        (lon, lat, iconCaption, titleTankerKey,
        titleFallback, uri, score, geohash)
        VALUES ('56.87754', '37.47502', 'Dot 1',
                'dot_1.tanker', 'Dot 1 title fallback',
                NULL, NULL, 'geohash1'),
               ('45.32212', '-12.87734', 'Dot 2',
                NULL, NULL, 'point2_uri', NULL, 'geohash2'),
               ('-130.12', '88.03454', 'Dot 3',
               'dot_3.tanker', NULL, NULL, NULL, 'geohash3')
        """,
    ],
)
async def test_admin_points_edit(taxi_pickup_points_manager, pgsql, load_json):
    response = await taxi_pickup_points_manager.post(
        '/v1/admin/points/edit',
        params={'id': '3'},
        json=load_json('request_admin_edit.json'),
    )
    assert response.status_code == 200

    params = {'bbox': '-180.0,-90.0,180.0,90.0'}
    response = await taxi_pickup_points_manager.get(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 200
    compare_answers(
        response.json(), load_json('response_admin_get_after_edit.json'),
    )


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
                NULL, NULL, 'point2_uri', NULL, 'geohash2'),
               ('-130.12', '88.03454', 'Dot 3',
               'dot_3.tanker', NULL, NULL, NULL, 'geohash3')
        """,
    ],
)
async def test_admin_points_find(taxi_pickup_points_manager, pgsql, load_json):
    response = await taxi_pickup_points_manager.get(
        '/v1/admin/points/find', params={'uri': 'point2_uri'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('response_admin_find.json')

    response = await taxi_pickup_points_manager.get(
        '/v1/admin/points/find', params={'uri': 'no_such_uri'},
    )
    assert response.status_code == 404


@pytest.mark.pgsql(
    'points',
    queries=[
        """
        INSERT INTO points_manager.points
        (lon, lat, iconCaption, titleTankerKey,
        titleFallback, uri, score, geohash)
        VALUES ('56.87754', '37.47502', 'Dot 1',
                'dot_1.tanker', 'Dot 1 title fallback',
                'point1_uri', NULL, 'geohash1')
        """,
    ],
)
async def test_admin_points_manual(taxi_pickup_points_manager, load_json):
    response = await taxi_pickup_points_manager.post(
        '/v1/admin/points/manual',
        json=load_json('request_admin_add_manual.json'),
    )
    assert response.status_code == 200

    response = await taxi_pickup_points_manager.post(
        '/v1/admin/points/manual',
        json=load_json('request_admin_add_manual.json'),
    )
    assert response.status_code == 400

    params = {'bbox': '-180.0,-90.0,180.0,90.0'}
    response = await taxi_pickup_points_manager.get(
        '/v1/admin/points', params=params,
    )
    assert response.status_code == 200
    compare_answers(
        response.json(), load_json('response_admin_get_manual.json'),
    )
