# pylint: disable=E1101,W0612
import json

import pytest


@pytest.mark.parametrize('drivers_count', [None, -1, 0, 2])
@pytest.mark.config(ALL_CATEGORIES=['econom'])
async def test_resource_free_drivers_graph_basic(
        taxi_surge_calculator, mockserver, drivers_count,
):
    actual_request = None

    allowed_classes = ['econom']

    candidates = [
        {
            # free 1
            'position': [38.1, 51],
            'id': 'id0',
            'dbid': 'dbid0',
            'uuid': 'uuid0',
            'classes': allowed_classes,
            'status': {'status': 'online'},
            'route_info': {'time': 10, 'distance': 0},
        },
        {
            # free 2
            'position': [38.1, 51],
            'id': 'id1',
            'dbid': 'dbid1',
            'uuid': 'uuid1',
            'classes': allowed_classes,
            'status': {'status': 'online', 'orders': []},
            'route_info': {'time': 50, 'distance': 0},
        },
        {
            # long chain
            'position': [38.1, 51],
            'id': 'id2',
            'dbid': 'dbid2',
            'uuid': 'uuid2',
            'classes': allowed_classes,
            'status': {'status': 'online', 'orders': [{'status': 'driving'}]},
            'chain_info': {
                'destination': [38.11, 51.1],
                'left_dist': 1200,
                'left_time': 950,
                'order_id': 'order_id1',
            },
            'route_info': {'time': 5, 'distance': 0},
        },
        {
            # medium chain
            'position': [38.1, 51],
            'id': 'id3',
            'dbid': 'dbid3',
            'uuid': 'uuid3',
            'classes': allowed_classes,
            'status': {'status': 'online', 'orders': [{'status': 'driving'}]},
            'chain_info': {
                'destination': [38.101, 51.01],
                'left_dist': 500,
                'left_time': 500,
                'order_id': 'order_id2',
            },
        },
        {
            # short chain
            'position': [38.1, 51],
            'id': 'id4',
            'dbid': 'dbid4',
            'uuid': 'uuid4',
            'classes': allowed_classes,
            'status': {'status': 'online', 'orders': [{'status': 'driving'}]},
            'chain_info': {
                'destination': [38.1005, 51.005],
                'left_dist': 250,
                'left_time': 100,
                'order_id': 'order_id3',
            },
        },
    ]

    @mockserver.json_handler('/candidates/order-multisearch')
    def _order_multisearch(request):
        nonlocal actual_request
        actual_request = request.json

        response = {'candidates': candidates}

        return response

    # valid
    point_a = [38.1, 51]
    request = {
        'point_a': point_a,
        'tariff_zone': json.dumps({'drivers_count': drivers_count}),
    }
    expected_counts = {
        'pins': 0,
        'radius': 0,
        'free': 2,
        'free_chain': 111,  # long * 100 + medium * 10 + short
        'total': 0,
    }
    expected_request = {
        'allowed_classes': allowed_classes,
        'class_limits': {'econom': 400},
        'max_distance': 2500,
        'max_route_distance': 2500,
        'point': point_a,
        'zone_id': 'moscow',  # hardcoded in pipeline
    }
    drivers_count = drivers_count or 0  # treat None as 0
    # expect given number drivers with the smallest eta or
    # all drivers with eta if number is negative
    expected_drivers = list(
        sorted(
            filter(lambda d: 'route_info' in d, candidates),
            key=lambda d: d['route_info']['time'],
        ),
    )[: drivers_count if drivers_count >= 0 else None]

    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    data = response.json()
    actual_counts = data['classes'][0]['calculation_meta']['counts']
    actual_drivers = json.loads(
        data['classes'][0]['calculation_meta']['reason'],
    )['drivers']

    assert actual_counts == expected_counts
    assert actual_request == expected_request
    assert actual_drivers == expected_drivers


@pytest.mark.config(ALL_CATEGORIES=['econom'])
async def test_eta_groups(taxi_surge_calculator, mockserver):
    actual_request = None

    @mockserver.json_handler('/candidates/order-multisearch')
    def _order_multisearch(request):
        nonlocal actual_request
        actual_request = request.json

        candidates = [
            {
                'position': [38.1, 51],
                'id': f'id{i}',
                'dbid': f'dbid{i}',
                'uuid': f'uuid{i}',
                'classes': actual_request['allowed_classes'],
                'status': {'status': 'online'},
                'route_info': {'time': eta, 'distance': 70 + i * 5},
            }
            for i, eta in enumerate([1, 9, 21, 50])
        ]
        return {'candidates': candidates}

    # valid
    point_a = [38.1, 51]
    request = {'point_a': point_a, 'tariff_zone': '{}'}
    expected_request = {
        'allowed_classes': ['econom'],
        'class_limits': {'econom': 400},
        'max_distance': 2500,
        'max_route_distance': 2500,
        'point': point_a,
        'zone_id': 'moscow',  # hardcoded in pipeline
    }
    response = await taxi_surge_calculator.post('/v1/calc-surge', json=request)
    assert response.status == 200
    data = response.json()
    actual_eta = json.loads(data['classes'][0]['calculation_meta']['reason'])[
        'eta_groups'
    ]
    actual_eta.sort(key=lambda t: t['limit'])
    assert actual_eta == [
        {'limit': 1, 'count': 1},
        {'limit': 10, 'count': 2},
        {'limit': 20, 'count': 2},
        {'limit': 50, 'count': 4},
    ]
    assert actual_request == expected_request
