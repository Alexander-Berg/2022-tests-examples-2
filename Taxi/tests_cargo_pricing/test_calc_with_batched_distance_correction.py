import pytest


from tests_cargo_pricing import utils


class Position:
    def __init__(self, pos, name):
        self.position = pos
        self.name = name


_POSITIONS = [
    Position([32.544742, 55.906177], '32.544742,55.906177'),
    Position([35.544742, 55.906177], '35.544742,55.906177'),
    Position([37.544742, 55.906177], '37.544742,55.906177'),
]

_LONG_ROUTE = 'maps3.protobuf'
_MIDDLE_ROUTE = 'maps2.protobuf'
_SHORT_ROUTE = 'maps.protobuf'

_SHORT_ROUTE_LEN = 3.541087890625
_MIDDLE_ROUTE_LEN = 4.21791748046875
_LONG_ROUTE_LEN = 10.627275390625


class RouteLen:
    def __init__(self, start_pos_ind, end_pos_ind, route_file_name):
        self.start_pos_ind = start_pos_ind
        self.end_pos_ind = end_pos_ind
        self.route_file_name = route_file_name

    def route_id(self):
        return (
            _POSITIONS[self.start_pos_ind].name
            + '~'
            + _POSITIONS[self.end_pos_ind].name
        )


@pytest.fixture(name='mock_route_configuratable')
def _mock_route_configuratable(mockserver, load_binary):
    class RouterContext:
        request = None
        mock = None
        routes = {}

        def set_routes(self, routes):
            self.routes = {}
            for route in routes:
                self.routes[route.route_id()] = route.route_file_name

    ctx = RouterContext()

    @mockserver.handler('/maps-router/v2/route')
    def _mock(request, *args, **kwargs):
        ctx.request = dict(request.query)
        file_name = ctx.routes[ctx.request['rll']]
        response = load_binary(file_name)
        return mockserver.make_response(
            response=response,
            status=200,
            content_type='application/x-protobuf',
        )

    ctx.mock = _mock

    return ctx


class Point:
    def __init__(self, pos_ind, claim_id, is_visited=True, point_type=None):
        self.pos_ind = pos_ind
        self.claim_id = claim_id
        self.point_type = point_type if point_type is not None else 'dropoff'
        self.is_visited = is_visited


def _make_waypoints(v1_calc_creator, points):
    base_point = v1_calc_creator.payload['waypoints'][1]
    arrived_at = base_point['first_time_arrived_at']
    resolved_at = base_point['resolution_info']['resolved_at']
    v1_calc_creator.payload['waypoints'] = []
    for i, pnt in enumerate(points):
        waypoint = {
            'claim_id': pnt.claim_id,
            'id': 'waypoint' + str(i),
            'type': pnt.point_type,
            'position': _POSITIONS[pnt.pos_ind].position,
        }
        if pnt.is_visited:
            waypoint['first_time_arrived_at'] = arrived_at
            waypoint['resolution_info'] = {
                'resolved_at': resolved_at,
                'resolution': 'delivered',
            }
        v1_calc_creator.payload['waypoints'].append(waypoint)
    return v1_calc_creator


def _round(route):
    return int(route * 1000)


def _setup_default_routes(v1_calc_creator, mock_route_configuratable):
    _make_waypoints(
        v1_calc_creator,
        [
            Point(0, 'claim1'),
            Point(1, 'claim2'),
            Point(1, 'claim2'),
            Point(2, 'claim1'),
        ],
    )
    mock_route_configuratable.set_routes(
        [
            RouteLen(0, 1, _SHORT_ROUTE),
            RouteLen(1, 2, _SHORT_ROUTE),
            RouteLen(1, 1, _SHORT_ROUTE),
            RouteLen(0, 2, _LONG_ROUTE),
        ],
    )


async def test_calc_with_bacthed_dist_correction(
        v1_calc_creator,
        mock_route_configuratable,
        setup_batched_distance_correction_exp,
):
    _setup_default_routes(v1_calc_creator, mock_route_configuratable)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['const_corr_1'] == 1.0
    exp_saved_dist = (_LONG_ROUTE_LEN + _SHORT_ROUTE_LEN) - (
        3 * _SHORT_ROUTE_LEN
    )
    assert _round(user_options['per_km_corr_1']) == _round(exp_saved_dist)


async def test_recalc_with_bacthed_dist_correction(
        v1_calc_creator,
        mock_route_configuratable,
        setup_batched_distance_correction_exp,
):
    _setup_default_routes(v1_calc_creator, mock_route_configuratable)

    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200

    v1_calc_creator.payload['previous_calc_id'] = calc_response.json()[
        'calc_id'
    ]
    recalc_response = await v1_calc_creator.execute()
    assert recalc_response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['const_corr_1'] == 1.0
    exp_saved_dist = (_LONG_ROUTE_LEN + _SHORT_ROUTE_LEN) - (
        3 * _SHORT_ROUTE_LEN
    )
    assert _round(user_options['per_km_corr_1']) == _round(exp_saved_dist)


async def test_recalc_with_bacthed_dist_correction_and_differ_route(
        v1_calc_creator,
        mock_route_configuratable,
        setup_batched_distance_correction_exp,
):
    _setup_default_routes(v1_calc_creator, mock_route_configuratable)

    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200

    _make_waypoints(
        v1_calc_creator,
        [
            Point(0, 'claim1'),
            Point(1, 'claim2'),
            Point(1, 'claim2'),
            Point(2, 'claim1'),
            Point(0, 'claim2'),
        ],
    )
    mock_route_configuratable.set_routes(
        [RouteLen(2, 0, _SHORT_ROUTE), RouteLen(1, 0, _MIDDLE_ROUTE)],
    )

    v1_calc_creator.payload['previous_calc_id'] = calc_response.json()[
        'calc_id'
    ]
    recalc_response = await v1_calc_creator.execute()
    assert recalc_response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['const_corr_2'] == 1.0
    exp_saved_dist = (
        _LONG_ROUTE_LEN + _SHORT_ROUTE_LEN + _MIDDLE_ROUTE_LEN
    ) - (4 * _SHORT_ROUTE_LEN)
    assert _round(user_options['per_km_corr_2']) == _round(exp_saved_dist)


async def test_recalc_with_bacthed_dist_correction_on_no_batched_offer(
        v1_calc_creator,
        mock_route_configuratable,
        setup_batched_distance_correction_exp,
):
    _make_waypoints(
        v1_calc_creator,
        [Point(0, 'claim1'), Point(1, 'claim1'), Point(2, 'claim1')],
    )
    mock_route_configuratable.set_routes(
        [RouteLen(0, 1, _MIDDLE_ROUTE), RouteLen(1, 2, _SHORT_ROUTE)],
    )

    calc_response = await v1_calc_creator.execute()
    assert calc_response.status_code == 200

    _make_waypoints(
        v1_calc_creator,
        [
            Point(0, 'claim1'),
            Point(0, 'claim2'),
            Point(1, 'claim1'),
            Point(2, 'claim1'),
            Point(2, 'claim2'),
        ],
    )

    mock_route_configuratable.set_routes(
        [
            RouteLen(0, 0, _MIDDLE_ROUTE),
            RouteLen(2, 2, _SHORT_ROUTE),
            RouteLen(0, 2, _LONG_ROUTE),
        ],
    )

    v1_calc_creator.payload['previous_calc_id'] = calc_response.json()[
        'calc_id'
    ]
    recalc_response = await v1_calc_creator.execute()
    assert recalc_response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['const_corr_0'] == 1.0
    exp_saved_dist = (
        _LONG_ROUTE_LEN + _SHORT_ROUTE_LEN + _MIDDLE_ROUTE_LEN
    ) - (2 * _MIDDLE_ROUTE_LEN + 2 * _SHORT_ROUTE_LEN)
    assert _round(user_options['per_km_corr_0']) == _round(exp_saved_dist)


async def test_calc_with_bacthed_dist_correction_three_claims(
        v1_calc_creator,
        mock_route_configuratable,
        setup_batched_distance_correction_exp,
):
    _make_waypoints(
        v1_calc_creator,
        [
            Point(0, 'claim1'),
            Point(1, 'claim2'),
            Point(2, 'claim3'),
            Point(1, 'claim2'),
            Point(2, 'claim1'),
            Point(1, 'claim3'),
        ],
    )
    mock_route_configuratable.set_routes(
        [
            RouteLen(0, 1, _SHORT_ROUTE),
            RouteLen(1, 2, _SHORT_ROUTE),
            RouteLen(1, 1, _LONG_ROUTE),
            RouteLen(0, 2, _LONG_ROUTE),
            RouteLen(2, 1, _MIDDLE_ROUTE),
        ],
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['const_corr_def'] == 1.0
    exp_saved_dist = (2 * _LONG_ROUTE_LEN + _MIDDLE_ROUTE_LEN) - (
        3 * _SHORT_ROUTE_LEN + 2 * _MIDDLE_ROUTE_LEN
    )
    assert _round(user_options['per_km_corr_def']) == _round(exp_saved_dist)


async def test_calc_with_bacthed_dist_correction_negative_saved_distance(
        v1_calc_creator,
        mock_route_configuratable,
        lazy_setup_batched_distance_correction_exp,
):
    await lazy_setup_batched_distance_correction_exp(
        {
            'requirement_names': {
                'limited_requirement_names': [
                    {
                        'requirement_names': {
                            'per_km_requirement_name': 'per_km_corr_0',
                            'constant_requirement_name': 'const_corr_0',
                        },
                        'saved_distance_limit': -3.0,
                    },
                ],
                'default_requirement_names': {
                    'per_km_requirement_name': 'per_km_corr_def',
                    'constant_requirement_name': 'const_corr_def',
                },
            },
        },
    )

    _make_waypoints(
        v1_calc_creator,
        [
            Point(0, 'claim1'),
            Point(1, 'claim2'),
            Point(1, 'claim1'),
            Point(2, 'claim2'),
        ],
    )
    mock_route_configuratable.set_routes(
        [
            RouteLen(0, 1, _SHORT_ROUTE),
            RouteLen(1, 2, _SHORT_ROUTE),
            RouteLen(1, 1, _MIDDLE_ROUTE),
        ],
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['const_corr_0'] == 1.0
    exp_saved_dist = (2 * _SHORT_ROUTE_LEN) - (
        2 * _SHORT_ROUTE_LEN + _MIDDLE_ROUTE_LEN
    )
    assert _round(user_options['per_km_corr_0']) == _round(exp_saved_dist)


async def test_calc_with_bacthed_dist_correction_empty_exp(
        v1_calc_creator,
        mock_route_configuratable,
        lazy_setup_batched_distance_correction_exp,
):
    await lazy_setup_batched_distance_correction_exp({})
    _setup_default_routes(v1_calc_creator, mock_route_configuratable)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options == {
        'composite_pricing__destination_point_completed': 4.0,
        'composite_pricing__destination_point_visited': 4.0,
        'composite_pricing__return_point_completed': 0.0,
        'composite_pricing__return_point_visited': 0.0,
        'composite_pricing__source_point_completed': 0.0,
        'composite_pricing__source_point_visited': 0.0,
        'fake_middle_point_cargocorp_van.no_loaders_point': 3.0,
    }


async def test_calc_with_bacthed_dist_correction_empty_exp_map(
        v1_calc_creator,
        mock_route_configuratable,
        lazy_setup_batched_distance_correction_exp,
):
    await lazy_setup_batched_distance_correction_exp(
        {
            'requirement_names': {
                'limited_requirement_names': [],
                'default_requirement_names': {
                    'per_km_requirement_name': 'per_km_corr_def',
                    'constant_requirement_name': 'const_corr_def',
                },
            },
        },
    )
    _setup_default_routes(v1_calc_creator, mock_route_configuratable)

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['const_corr_def'] == 1.0
    exp_saved_dist = (_LONG_ROUTE_LEN + _SHORT_ROUTE_LEN) - (
        3 * _SHORT_ROUTE_LEN
    )
    assert _round(user_options['per_km_corr_def']) == _round(exp_saved_dist)


async def test_calc_with_bacthed_dist_correction_none_visited_waypoints(
        v1_calc_creator,
        mock_route_configuratable,
        setup_batched_distance_correction_exp,
):
    _make_waypoints(
        v1_calc_creator,
        [
            Point(0, 'claim1'),
            Point(1, 'claim2'),
            Point(1, 'claim2'),
            Point(2, 'claim1'),
            Point(2, 'claim2', is_visited=False),
            Point(0, 'claim1', is_visited=False),
        ],
    )
    mock_route_configuratable.set_routes(
        [
            RouteLen(0, 1, _SHORT_ROUTE),
            RouteLen(1, 2, _SHORT_ROUTE),
            RouteLen(1, 1, _SHORT_ROUTE),
            RouteLen(0, 2, _LONG_ROUTE),
        ],
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['const_corr_1'] == 1.0
    exp_saved_dist = (_LONG_ROUTE_LEN + _SHORT_ROUTE_LEN) - (
        3 * _SHORT_ROUTE_LEN
    )
    assert _round(user_options['per_km_corr_1']) == _round(exp_saved_dist)


async def test_calc_with_bacthed_dist_correction_ignore_return_points(
        v1_calc_creator,
        mock_route_configuratable,
        setup_batched_distance_correction_exp,
):
    _make_waypoints(
        v1_calc_creator,
        [
            Point(0, 'claim1', is_visited=False, point_type='pickup'),
            Point(1, 'claim2', is_visited=False, point_type='pickup'),
            Point(1, 'claim2', is_visited=False, point_type='dropoff'),
            Point(2, 'claim1', is_visited=False, point_type='dropoff'),
            Point(2, 'claim2', is_visited=False, point_type='return'),
            Point(0, 'claim1', is_visited=False, point_type='return'),
        ],
    )
    v1_calc_creator.payload.pop('resolution_info')
    mock_route_configuratable.set_routes(
        [
            RouteLen(0, 1, _SHORT_ROUTE),
            RouteLen(1, 2, _SHORT_ROUTE),
            RouteLen(1, 1, _SHORT_ROUTE),
            RouteLen(0, 2, _LONG_ROUTE),
        ],
    )

    response = await v1_calc_creator.execute()
    assert response.status_code == 200

    user_options = utils.get_recalc_request_user_options(v1_calc_creator)
    assert user_options['const_corr_1'] == 1.0
    exp_saved_dist = (_LONG_ROUTE_LEN + _SHORT_ROUTE_LEN) - (
        3 * _SHORT_ROUTE_LEN
    )
    assert _round(user_options['per_km_corr_1']) == _round(exp_saved_dist)
