import pytest


_DEFAULT_ROUTER_SELECT = [
    {'routers': ['yamaps']},
    {'ids': ['moscow'], 'routers': ['linear-fallback']},
]


@pytest.mark.config(ROUTER_SELECT=_DEFAULT_ROUTER_SELECT)
async def test_grocery_queue_inactive(taxi_candidates):
    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 10000,
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert candidates == []


@pytest.mark.config(ROUTER_SELECT=_DEFAULT_ROUTER_SELECT)
async def test_grocery_queue_empty(taxi_candidates, mockserver):
    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v2/queue-info',
    )
    def _mock_queue_info(request):
        return {'couriers': []}

    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 10000,
        'order': {
            'request': {
                'shift': {
                    'type': 'grocery',
                    'zone_group': {'required_ids': ['abc', 'def']},
                },
            },
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert candidates == []


@pytest.mark.config(ROUTER_SELECT=_DEFAULT_ROUTER_SELECT)
async def test_grocery_queue_error(taxi_candidates, mockserver):
    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v2/queue-info',
    )
    def _mock_queue_info(request):
        return mockserver.make_response(json='Server error', status=500)

    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 10000,
        'order': {
            'request': {
                'shift': {
                    'type': 'grocery',
                    'zone_group': {'required_ids': ['abc', 'def']},
                },
            },
        },
    }
    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert candidates == []


@pytest.mark.config(ROUTER_SELECT=_DEFAULT_ROUTER_SELECT)
async def test_grocery_queue_full(taxi_candidates, mockserver):
    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v2/queue-info',
    )
    def _mock_queue_info(request):
        return {
            'couriers': [
                {
                    'courier_id': 'dbid0_uuid0',
                    'checkin_timestamp': '2021-01-02T00:00:00+0000',
                },
                {
                    'courier_id': 'dbid0_uuid1',
                    'checkin_timestamp': '2021-01-01T00:00:00+0000',
                },
            ],
        }

    @mockserver.json_handler(
        '/grocery-wms/api/external/courier_shifts/v1/updates',  # noqa: E501
    )
    def _mock_courier_shift_states(request):
        if not request.args['cursor']:
            return {
                'data': {
                    'cursor': '1',
                    'shifts': [
                        {
                            'store_id': '123',
                            'store_external_id': 'depot_1',
                            'courier_id': 'dbid0_uuid0',
                            'shift_id': '19950',
                            'status': 'in_progress',
                        },
                        {
                            'store_id': '123',
                            'store_external_id': 'depot_2',
                            'courier_id': 'dbid0_uuid1',
                            'shift_id': '19950',
                            'status': 'in_progress',
                        },
                    ],
                },
            }
        return {'data': {'cursor': '1', 'shifts': []}}

    body = {
        'limit': 3,
        'zone_id': 'moscow',
        'point': [37.625129, 55.757644],
        'max_route_time': 3600,
        'max_distance': 10000,
        'order': {
            'request': {
                'shift': {
                    'type': 'grocery',
                    'zone_group': {'required_ids': ['depot_1', 'depot_2']},
                },
            },
        },
    }

    response = await taxi_candidates.post('order-search', json=body)
    assert response.status_code == 200
    json = response.json()
    assert 'candidates' in json
    candidates = json['candidates']
    assert len(candidates) == 2

    assert candidates[0]['id'] == 'dbid0_uuid1'
    assert (
        candidates[0]['metadata']['grocery_queue']['checkin_timestamp']
        == '2021-01-01T00:00:00+00:00'
    )

    assert candidates[1]['id'] == 'dbid0_uuid0'
    assert (
        candidates[1]['metadata']['grocery_queue']['checkin_timestamp']
        == '2021-01-02T00:00:00+00:00'
    )
