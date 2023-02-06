# pylint: disable=redefined-outer-name
import datetime
import enum

import pytest


ISO_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
NOW = datetime.datetime(2020, 4, 20, 0, 0, 0)
NOW_STR = NOW.strftime(ISO_FORMAT)
THEN = datetime.datetime(2020, 4, 22, 0, 0, 0)
THEN_STR = THEN.strftime(ISO_FORMAT)
EXPECTED_WINDOW = f'{NOW_STR}/{THEN_STR}'


def make_start_request(n_points, kinds=None, ids=None):
    if n_points == 0:
        return {}
    if kinds is None:
        kinds = ['source'] + ['destination' for _ in range(1, n_points)]
    if ids is None:
        ids = [None] * n_points
    return {
        'route': [
            make_location(i, kinds[i], False, ids[i]) for i in range(n_points)
        ],
    }


def make_location(
        idx, kind=None, for_b2bgeo=False, point_id=None, drop_reason=None,
):
    result = {'id': point_id or f'{idx:04d}'}
    if for_b2bgeo:
        result['time_window'] = EXPECTED_WINDOW
        result['point'] = {'lon': idx + 0.5, 'lat': idx + 1.5}
    else:
        result.update({'lon': idx + 0.5, 'lat': idx + 1.5})
        if kind is not None:
            result['type'] = kind
    if drop_reason:
        result['drop_reason'] = drop_reason
    return result


def make_route_node(idx, kind=None):
    kind = kind or ('depot' if idx == 0 else 'location')
    return {
        'arrival_time_s': NOW.timestamp(),
        'transit_distance_m': 100,
        'transit_duration_s': 100,
        'node': {'value': {'id': f'{idx:04d}'}, 'type': kind},
    }


def make_status(status):
    timestamps = {'queued': NOW.timestamp()}
    if status == 'queued':
        return timestamps
    timestamps['started'] = NOW.timestamp()
    if status == 'started':
        return timestamps
    assert status in ('completed', 'cancelled'), 'unknown status'
    timestamps[status] = NOW.timestamp()
    return timestamps


def make_result(
        status='SOLVED', route=None, vehicle_id='0', dropped_locations=None,
):
    dropped_locations = dropped_locations or []
    route = route or [make_route_node(i) for i in range(4)]
    return {
        'solver_status': status,
        'dropped_locations': dropped_locations,
        'routes': [{'route': route, 'vehicle_id': vehicle_id}],
    }


@pytest.fixture
def mock_yandex_routing(mockserver):
    # use integers for lon/lat to avoid float comparison issues
    context = {
        'create': {
            'check-request': True,
            'expected-request': {
                'options': {
                    'quality': 'low',
                    'time_zone': 0,
                    'routing_mode': 'driving',
                },
                'vehicle': {'id': '0', 'return_to_depot': False},
                'locations': [
                    make_location(i, for_b2bgeo=True) for i in range(1, 3)
                ],
                'depot': make_location(0, for_b2bgeo=True),
            },
            'status': 202,
            'response': {
                'id': '12345',
                'message': 'queued for execution',
                'status': {'queued': NOW.timestamp()},
            },
        },
        'get': {
            'check-request': True,
            'expected-id': '12345',
            'status': 200,
            'response': {
                'id': '12345',
                'status': make_status('completed'),
                'result': make_result(),
            },
        },
    }

    @mockserver.json_handler('/b2bgeo/v1/add/svrp')
    def _mock_add_svrp(request):
        assert request.query['apikey'] == 'yandex-routing-api-key'
        assert (
            not context['create']['check-request']
            or request.json == context['create']['expected-request']
        )
        return mockserver.make_response(
            json=context['create']['response'],
            status=context['create']['status'],
        )

    @mockserver.json_handler('/b2bgeo/v1/result/svrp', prefix=True)
    def _mock_result_svrp(request):
        assert (
            request.path
            == '/b2bgeo/v1/result/svrp/' + context['get']['expected-id']
        )
        return mockserver.make_response(
            json=context['get']['response'], status=context['get']['status'],
        )

    context['create']['handler'] = _mock_add_svrp
    context['get']['handler'] = _mock_result_svrp
    yield context


@pytest.mark.now(NOW_STR)
async def test_optimize_route_start(
        taxi_cargo_claims, mock_yandex_routing, get_default_headers,
):
    request = make_start_request(3)
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/start',
        json=request,
        headers=get_default_headers(),
    )
    assert mock_yandex_routing['create']['handler'].times_called == 1
    assert response.status_code == 200
    response = response.json()
    assert response['id'] == '12345'
    assert response['status'] == 'queued'


class ParamSource(enum.Enum):
    SETTINGS = (0,)
    QUERY = 1


@pytest.mark.now(NOW_STR)
@pytest.mark.parametrize(
    'quality_from', [ParamSource.SETTINGS, ParamSource.QUERY],
)
@pytest.mark.parametrize(
    'routing_mode_from', [ParamSource.SETTINGS, ParamSource.QUERY],
)
@pytest.mark.parametrize('quality', ['normal', 'high'])
@pytest.mark.parametrize('routing_mode', ['truck', 'transit'])
async def test_optimize_route_start_query_settings(
        taxi_cargo_claims,
        taxi_config,
        mock_yandex_routing,
        get_default_headers,
        quality_from,
        routing_mode_from,
        quality,
        routing_mode,
):
    expect_settings = mock_yandex_routing['create']['expected-request'][
        'options'
    ]
    expect_settings['quality'] = quality
    expect_settings['routing_mode'] = routing_mode

    config = {
        'quality': quality if quality_from == ParamSource.SETTINGS else 'low',
        'routing_mode': (
            routing_mode
            if routing_mode_from == ParamSource.SETTINGS
            else 'driving'
        ),
        'min_points': 3,
    }
    taxi_config.set_values(dict(CARGO_CLAIMS_OPTIMIZE_ROUTE_SETTINGS=config))

    query = ''
    if quality_from == ParamSource.QUERY:
        query = f'?quality={quality}'
    if routing_mode_from == ParamSource.QUERY:
        query += '?' if not query else '&'
        query += f'routing_mode={routing_mode}'

    request = make_start_request(3)
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/start{query}',
        json=request,
        headers=get_default_headers(),
    )
    assert mock_yandex_routing['create']['handler'].times_called == 1
    assert response.status_code == 200
    response = response.json()
    assert response['id'] == '12345'
    assert response['status'] == 'queued'


async def test_start_b2bgeo_errors(
        taxi_cargo_claims, mock_yandex_routing, get_default_headers,
):
    mock_yandex_routing['create']['check-request'] = False
    mock_yandex_routing['create']['response'] = {
        'error': {'message': 'foo bar', 'incident_id': '12345'},
    }
    mock_yandex_routing['create']['status'] = 400
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/start',
        json=make_start_request(3),
        headers=get_default_headers(),
    )
    assert mock_yandex_routing['create']['handler'].times_called == 1
    assert response.status_code == 400
    assert response.json()['code'] == 'bad_request'


@pytest.mark.now(NOW_STR)
@pytest.mark.parametrize(
    'status,error_code,optimize_request',
    [
        (400, 'duplicate_id', make_start_request(3, ids=['1', '1', '2'])),
        (
            400,
            'duplicate_source_point',
            make_start_request(3, kinds=['source', 'source', 'destination']),
        ),
        (400, 'too_few_points', make_start_request(2)),
        (
            400,
            'source_point_missing',
            make_start_request(3, kinds=['destination'] * 3),
        ),
    ],
)
async def test_validation_errors(
        taxi_cargo_claims,
        mock_yandex_routing,
        get_default_headers,
        status,
        error_code,
        optimize_request,
):
    response = await taxi_cargo_claims.post(
        '/api/integration/v2/optimize-route/start',
        json=optimize_request,
        headers=get_default_headers(),
    )
    assert mock_yandex_routing['create']['handler'].times_called == 0
    assert response.status_code == status
    assert response.json()['code'] == error_code


async def test_optimize_route_result(
        taxi_cargo_claims, mock_yandex_routing, get_default_headers,
):
    request = {'id': '12345'}
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/result',
        json=request,
        headers=get_default_headers(),
    )
    assert mock_yandex_routing['get']['handler'].times_called == 1
    assert response.status_code == 200
    expected_response = {
        'info': {'status': 'completed', 'id': '12345'},
        'result': {
            'route': [
                x['node']['value']['id']
                for x in mock_yandex_routing['get']['response']['result'][
                    'routes'
                ][0]['route']
            ],
        },
    }
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'code,status', ((201, 'queued'), (202, 'started'), (202, 'cancelled')),
)
async def test_optimize_route_result_not_ready(
        taxi_cargo_claims,
        mock_yandex_routing,
        get_default_headers,
        code,
        status,
):
    request = {'id': '12345'}
    mock_yandex_routing['get']['response'] = {
        'status': make_status(status),
        'id': '12345',
    }
    mock_yandex_routing['get']['status'] = code
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/result',
        json=request,
        headers=get_default_headers(),
    )
    assert response.status_code == 200
    assert response.json()['info'] == {'id': '12345', 'status': status}


async def test_optimize_route_result_404(
        taxi_cargo_claims, mock_yandex_routing, get_default_headers,
):
    mock_yandex_routing['get']['status'] = 410
    mock_yandex_routing['get']['response'] = {
        'error': {'message': 'foo', 'incident_id': '123'},
    }
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/result',
        json={'id': '12345'},
        headers=get_default_headers(),
    )
    assert response.status_code == 404
    assert response.json()['code'] == 'task_not_found'


@pytest.mark.parametrize(
    'b2bgeo_response',
    [
        {
            'status': make_status('completed'),
            'id': '12345',
            'result': make_result(
                route=[make_route_node(i, kind='location') for i in range(3)],
            ),
        },
        {
            'status': make_status('completed'),
            'id': '12345',
            'result': make_result(
                route=[make_route_node(i) for i in range(3)],
                dropped_locations=[make_location(3, drop_reason='foo')],
            ),
        },
    ],
)
async def test_result_solver_error(
        taxi_cargo_claims,
        mock_yandex_routing,
        get_default_headers,
        b2bgeo_response,
):
    request = {'id': '12345'}
    mock_yandex_routing['get']['response'] = b2bgeo_response
    response = await taxi_cargo_claims.post(
        f'/api/integration/v2/optimize-route/result',
        json=request,
        headers=get_default_headers(),
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'solver_failed'
