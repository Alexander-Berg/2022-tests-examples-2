import pytest


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
async def test_route_no_path(taxi_tigraph_router):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[0.0, 0.0], [37.548664, 55.697747]],
            'request_path': False,
            'use_jams': False,
            'use_tolls': False,
        },
    )
    assert response.status_code == 404


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
async def test_route_simple_summary(taxi_tigraph_router):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[37.529272, 55.697285], [37.526510, 55.698854]],
            'request_path': False,
            'use_jams': False,
            'use_tolls': False,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert 'summary' in data

    summary = data['summary']
    assert int(summary['duration']) == 18
    assert int(summary['length']) == 246
    assert not summary['has_closure']
    assert not summary['has_dead_jam']
    assert not summary['has_toll_roads']

    assert 'paths' not in data


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
async def test_route_simple_path(taxi_tigraph_router):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[37.529272, 55.697285], [37.526510, 55.698854]],
            'request_path': True,
            'use_jams': False,
            'use_tolls': False,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert 'summary' in data

    summary = data['summary']
    assert int(summary['duration']) == 18
    assert int(summary['length']) == 246

    assert 'paths' in data
    paths = data['paths']

    assert len(paths) == 1
    assert len(paths[0]) == 5

    assert 'paths_meta' in data
    paths_meta = data['paths_meta']

    assert len(paths_meta) == 1
    assert len(paths_meta[0]['legs']) == 1


async def test_route_summary_jams_invalidated(taxi_tigraph_router):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[37.527499, 55.698160], [37.589464, 55.668626]],
            'request_path': False,
            'use_jams': False,
            'use_tolls': False,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert 'summary' in data

    summary = data['summary']
    assert int(summary['duration']) == 536
    assert int(summary['length']) == 5146


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
async def test_route_summary_nojams(taxi_tigraph_router):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[37.527499, 55.698160], [37.589464, 55.668626]],
            'request_path': False,
            'use_jams': False,
            'use_tolls': False,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert 'summary' in data

    summary = data['summary']
    assert int(summary['duration']) == 536
    assert int(summary['length']) == 5146


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
async def test_route_summary_jams(taxi_tigraph_router):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[37.527499, 55.698160], [37.589464, 55.668626]],
            'request_path': False,
            'use_jams': True,
            'use_tolls': False,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert 'summary' in data

    summary = data['summary']
    assert int(summary['duration']) == 536
    assert int(summary['length']) == 5146


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
async def test_route_summary_via(taxi_tigraph_router):
    # https://yandex.ru/maps/-/CKuWBAoQ
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [
                [37.641672, 55.734948],
                [37.601210, 55.771562],
                [37.644520, 55.733307],
            ],
            'request_path': False,
            'use_jams': False,
            'use_tolls': False,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert 'summary' in data

    summary = data['summary']

    # duration is greater than 10 minutes
    assert int(summary['duration']) > 600
    # length is greater than 10 km
    assert int(summary['length']) > 10000


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
async def test_route_results_many(taxi_tigraph_router):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
            'request_path': True,
            'use_jams': False,
            'use_tolls': False,
            'results': 10,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert 'paths' in data
    assert len(data['paths']) == 2

    assert 'paths_meta' in data
    paths_meta = data['paths_meta']

    assert len(paths_meta) == 2
    assert len(paths_meta[0]['legs']) == 1
    assert len(paths_meta[1]['legs']) == 1


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
async def test_route_results_one(taxi_tigraph_router):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
            'request_path': True,
            'use_jams': False,
            'use_tolls': False,
            'results': 1,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert 'paths' in data
    assert len(data['paths']) == 1

    assert 'paths_meta' in data
    paths_meta = data['paths_meta']

    assert len(paths_meta) == 1
    assert len(paths_meta[0]['legs']) == 1


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
async def test_route_results_one_with_two_legs(taxi_tigraph_router):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [
                [37.541258, 55.703967],
                [37.521246, 55.702218],
                [37.521234, 55.701218],
            ],
            'request_path': True,
            'use_jams': False,
            'use_tolls': False,
            'results': 1,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert 'paths' in data
    assert len(data['paths']) == 1

    assert 'paths_meta' in data
    paths_meta = data['paths_meta']

    assert len(paths_meta) == 1
    assert len(paths_meta[0]['legs']) == 2


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
async def test_route_results_debug(
        taxi_tigraph_router, load_binary, mockserver,
):
    @mockserver.handler('/maps-router/v2/route')
    def _mock_route(request):
        return mockserver.make_response(
            response=load_binary('maps.protobuf'),
            status=200,
            content_type='application/x-protobuf',
        )

    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
            'request_path': True,
            'use_jams': False,
            'use_tolls': False,
            'results': 1,
            'output': 'debug',
        },
    )
    assert response.status_code == 200

    data = response.json()

    assert 'paths' in data
    assert len(data['paths']) == 1

    assert 'debug' in data
    assert 'maps_path' in data['debug']
    assert len(data['debug']['maps_path']) == 97


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
@pytest.mark.experiments3(filename='tigraph_discard_all.json')
async def test_route_config_discard_all(
        taxi_tigraph_router, load_binary, mockserver,
):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
            'request_path': True,
            'use_jams': False,
            'use_tolls': False,
            'results': 1,
        },
    )
    assert response.status_code == 413


@pytest.mark.config(GRAPH_JAMS_LIFETIME=0)
@pytest.mark.experiments3(filename='tigraph_discard_some.json')
async def test_route_config_discard_some(
        taxi_tigraph_router, load_binary, mockserver,
):
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[37.541258, 55.703967], [37.521246, 55.702218]],
            'request_path': True,
            'use_jams': False,
            'use_tolls': False,
            'results': 1,
        },
    )
    assert response.status_code == 200
    response = await taxi_tigraph_router.post(
        'route',
        {
            'route': [[0, -90], [0, 90]],
            'request_path': True,
            'use_jams': False,
            'use_tolls': False,
            'results': 1,
        },
    )
    assert response.status_code == 413
