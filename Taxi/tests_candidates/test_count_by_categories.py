import datetime

import pytest

import tests_candidates.driver_status


@pytest.mark.parametrize(
    'request_body,response_code',
    [
        ({}, 400),
        ({'point': [37.619757, 55.753215]}, 400),
        ({'point': [37.619757, 55.753215], 'limit': 10}, 400),
        (
            {
                'point': [37.619757, 55.753215],
                'limit': 10,
                'allowed_classes': [],
            },
            400,
        ),
        (
            {
                'point': [37.619757, 55.753215],
                'limit': 10,
                'allowed_classes': [],
                'max_distance': 100,
            },
            400,
        ),
        (
            {
                'point': [37.619757, 55.753215],
                'limit': 10,
                'allowed_classes': ['econom'],
                'max_distance': 100,
            },
            200,
        ),
    ],
)
async def test_response_code(taxi_candidates, request_body, response_code):
    response = await taxi_candidates.post(
        'count-by-categories', json=request_body,
    )
    assert response.status_code == response_code


async def test_response_format(taxi_candidates, driver_positions, taxi_config):

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.619757, 55.753215]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.619757, 55.753215]},
        ],
    )
    request_body = {
        'point': [37.308020, 55.903174],
        'limit': 5,
        'max_distance': 4000,
        'allowed_classes': ['econom', 'vip'],
        'zone_id': 'moscow',
    }
    response = await taxi_candidates.post(
        'count-by-categories', json=request_body,
    )
    assert response.status_code == 200
    assert 'radius' in response.json()
    assert 'generic' in response.json()
    counts_by_categories = response.json()['generic']
    for cls, counts in counts_by_categories.items():
        assert cls in request_body['allowed_classes']
        assert all(
            x
            in ['total', 'on_order', 'free', 'free_chain', 'free_chain_groups']
            for x in counts
        )
    assert 'X-YaTaxi-Server-Hostname' in response.headers
    assert response.headers['X-YaTaxi-Server-Hostname']


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
@pytest.mark.parametrize(
    'skip_reposition_mode,skip_expired_reposition',
    [(False, False), (False, True), (True, False)],
)
async def test_sample(
        taxi_candidates,
        driver_positions,
        chain_busy_drivers,
        mockserver,
        load_binary,
        taxi_config,
        skip_reposition_mode,
        skip_expired_reposition,
        mock_reposition_index,
):
    bonus_until = None
    if skip_reposition_mode or skip_expired_reposition:
        bonus_until = datetime.datetime.now()
    if skip_reposition_mode:
        bonus_until += datetime.timedelta(hours=1)
    if skip_expired_reposition:
        bonus_until -= datetime.timedelta(hours=1)
    mock_reposition_index.set_response(
        drivers=[
            {
                'driver_id': 'uuid0',
                'park_db_id': 'dbid0',
                'can_take_orders': True,
                'can_take_orders_when_busy': True,
                'reposition_check_required': True,
                'mode_name': 'home',
                'bonus_until': bonus_until,
            },
        ],
    )

    taxi_config.set_values(
        {
            'CANDIDATES_COUNT_BY_CATEGORIES_REPOSITION_FILTER': {
                'exclude': ['home_completed'] if skip_reposition_mode else [],
            },
        },
    )

    await driver_positions(
        [
            {'dbid_uuid': 'dbid0_uuid0', 'position': [37.619062, 55.752606]},
            {'dbid_uuid': 'dbid0_uuid1', 'position': [37.617785, 55.754216]},
            {'dbid_uuid': 'dbid0_uuid2', 'position': [37.627852, 55.753021]},
        ],
    )
    chain_busy_drivers(
        [
            {
                'driver_id': 'dbid0_uuid2',
                'left_time': 100,
                'left_distance': 1000,
                'destination': [37.627852, 55.753021],
                'approximate': False,
            },
        ],
    )
    request_body = {
        'point': [37.619757, 55.753215],
        'limit': 5,
        'max_distance': 4000,
        'allowed_classes': ['econom', 'vip'],
    }
    response = await taxi_candidates.post(
        'count-by-categories', json=request_body,
    )
    assert response.status_code == 200
    assert 'generic' in response.json()
    counts_by_categories = response.json()['generic']
    assert 'econom' in counts_by_categories
    econom_counters = counts_by_categories['econom']
    assert econom_counters['total'] == 1
    assert econom_counters['free'] == 0
    assert econom_counters['on_order'] == 1
    assert econom_counters['free_chain'] == 0

    assert 'vip' in counts_by_categories
    vip_counters = counts_by_categories['vip']
    assert vip_counters['total'] == 2
    assert vip_counters['free'] == 1
    assert vip_counters['on_order'] == 1
    assert vip_counters['free_chain'] == 1

    reposition_count = 1
    if skip_reposition_mode or skip_expired_reposition:
        reposition_count = 0

    assert 'reposition' in response.json()
    counts_by_categories = response.json()['reposition']
    assert 'econom' in counts_by_categories
    econom_counters = counts_by_categories['econom']
    assert econom_counters['total'] == reposition_count
    assert econom_counters['free'] == 0
    assert econom_counters['on_order'] == reposition_count
    assert econom_counters['free_chain'] == 0

    assert 'vip' in counts_by_categories
    vip_counters = counts_by_categories['vip']
    assert vip_counters['total'] == 0
    assert vip_counters['free'] == 0
    assert vip_counters['on_order'] == 0
    assert vip_counters['free_chain'] == 0

    assert 'radius' in response.json()
    assert response.json()['radius'] == 4000

    # test limiting
    request_body['limit'] = 2
    response = await taxi_candidates.post(
        'count-by-categories', json=request_body,
    )
    assert response.status_code == 200
    assert 'radius' in response.json()
    assert response.json()['radius'] == 166

    request_body['limit'] = 2
    request_body['max_distance'] = 150
    response = await taxi_candidates.post(
        'count-by-categories', json=request_body,
    )
    assert response.status_code == 200
    assert 'radius' in response.json()
    assert response.json()['radius'] == 150


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['moscow'],
                'arg_name': 'tariff_zone',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='experiment',
    consumers=['candidates/filters'],
    clauses=[
        {
            'title': 'experiment_1',
            'value': {'value': 2},
            'predicate': {
                'init': {
                    'set': ['56f968f07c0aa65c44998e4e'],
                    'arg_name': 'unique_driver_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
        {
            'title': 'not_experiment_1',
            'value': {'value': 1},
            'predicate': {'type': 'true'},
        },
    ],
    default_value=True,
)
@pytest.mark.config(
    CANDIDATES_FILTER_FETCH_EXPERIMENT_CLASSES={
        '__default__': {
            'affect': True,
            'classes': ['econom', 'vip'],
            'experiments': ['experiment'],
        },
    },
)
async def test_nothing_found(taxi_candidates, driver_positions, taxi_config):

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid1', 'position': [37.619757, 55.753215]}],
    )
    request_body = {
        'point': [37.619757, 55.753215],
        'limit': 5,
        'max_distance': 4000,
        'allowed_classes': ['econom', 'vip'],
        'metadata': {
            'experiments': [
                {
                    'name': 'experiment',
                    'value': {'value': 1},
                    'position': 0,
                    'version': 0,
                    'is_signal': False,
                },
            ],
        },
    }
    response = await taxi_candidates.post(
        'count-by-categories', json=request_body,
    )
    assert response.status_code == 200

    assert 'generic' in response.json()
    counts_by_categories = response.json()['generic']
    assert 'econom' in counts_by_categories
    econom_counters = counts_by_categories['econom']
    assert econom_counters['total'] == 0
    assert 'vip' in counts_by_categories
    vip_counters = counts_by_categories['vip']
    assert vip_counters['total'] == 0

    assert 'radius' in response.json()
    assert response.json()['radius'] == request_body['max_distance']


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
@pytest.mark.experiments3(
    match={
        'predicate': {
            'type': 'in_set',
            'init': {
                'set': ['moscow'],
                'arg_name': 'tariff_zone',
                'set_elem_type': 'string',
            },
        },
        'enabled': True,
    },
    name='experiment',
    consumers=['candidates/filters'],
    clauses=[
        {
            'title': 'experiment_1',
            'value': {'value': 2},
            'predicate': {
                'init': {
                    'set': ['56f968f07c0aa65c44998e4e'],
                    'arg_name': 'unique_driver_id',
                    'set_elem_type': 'string',
                },
                'type': 'in_set',
            },
        },
        {
            'title': 'not_experiment_1',
            'value': {'value': 1},
            'predicate': {'type': 'true'},
        },
    ],
    default_value=True,
)
async def test_required_experiments(
        taxi_candidates, driver_positions, taxi_config,
):
    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid1', 'position': [37.619757, 55.753215]}],
    )
    request_body = {
        'point': [37.619757, 55.753215],
        'limit': 5,
        'max_distance': 4000,
        'allowed_classes': ['econom', 'vip'],
        'required_experiments': ['experiment'],
        'metadata': {
            'experiments': [
                {
                    'name': 'experiment',
                    'value': {'value': 1},
                    'position': 0,
                    'version': 0,
                    'is_signal': False,
                },
            ],
        },
    }
    response = await taxi_candidates.post(
        'count-by-categories', json=request_body,
    )
    assert response.status_code == 200

    assert 'generic' in response.json()
    counts_by_categories = response.json()['generic']
    assert 'econom' in counts_by_categories
    econom_counters = counts_by_categories['econom']
    assert econom_counters['total'] == 0
    assert 'vip' in counts_by_categories
    vip_counters = counts_by_categories['vip']
    assert vip_counters['total'] == 0

    assert 'radius' in response.json()
    assert response.json()['radius'] == request_body['max_distance']


@pytest.mark.config(EXTRA_EXAMS_BY_ZONE={})
async def test_count_free(
        taxi_candidates,
        driver_positions,
        mockserver,
        load_binary,
        taxi_config,
        mock_reposition_index,
):
    @mockserver.handler('/driver-status/v2/orders/updates')
    def _mock_orders(request):
        response_data = tests_candidates.driver_status.build_orders_fbs(
            0, [], request.query.get('compression', 'gzip'),
        )
        return mockserver.make_response(
            response=response_data,
            headers={'Content-Type': 'application/x-flatbuffers'},
            status=200,
        )

    mock_reposition_index.set_response(
        drivers=[
            {
                'driver_id': 'uuid0',
                'park_db_id': 'dbid0',
                'can_take_orders': True,
                'can_take_orders_when_busy': True,
                'reposition_check_required': True,
            },
        ],
    )

    await driver_positions(
        [{'dbid_uuid': 'dbid0_uuid0', 'position': [37.627852, 55.753021]}],
    )
    request_body = {
        'point': [37.619757, 55.753215],
        'limit': 5,
        'max_distance': 4000,
        'allowed_classes': ['econom'],
    }
    response = await taxi_candidates.post(
        'count-by-categories', json=request_body,
    )
    assert response.status_code == 200
    assert 'generic' in response.json()
    counts_by_categories = response.json()['generic']
    assert 'econom' in counts_by_categories
    econom_counters = counts_by_categories['econom']
    assert econom_counters['total'] == 1
    assert econom_counters['free'] == 1
    assert econom_counters['on_order'] == 0
    assert econom_counters['free_chain'] == 0

    assert 'reposition' in response.json()
    counts_by_categories = response.json()['reposition']
    assert 'econom' in counts_by_categories
    econom_counters = counts_by_categories['econom']
    assert econom_counters['total'] == 1
    assert econom_counters['free'] == 1
    assert econom_counters['on_order'] == 0
    assert econom_counters['free_chain'] == 0
