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


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['eda']},
        'grocery': {'classes': ['econom', 'vip', 'uberblack']},
    },
)
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
                    'type': 'eats',
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


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['eda']},
        'grocery': {'classes': ['econom', 'vip', 'uberblack']},
    },
)
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
                    'type': 'eats',
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


@pytest.mark.config(
    ROUTER_SELECT=_DEFAULT_ROUTER_SELECT,
    CANDIDATES_SHIFT_SETTINGS={
        'eats': {'classes': ['econom', 'vip', 'uberblack']},
        'grocery': {'classes': ['econom', 'vip', 'uberblack']},
    },
)
@pytest.mark.now('2020-07-28T08:48:00+00:00')
async def test_grocery_queue_full(taxi_candidates, mockserver, grocery_depots):
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

    grocery_depots.add_depot(0, legacy_depot_id='12345')

    @mockserver.json_handler(
        '/grocery-checkins/internal/checkins/v1/shifts/shifts-info',
    )
    def _grocery_shifts_info(request):
        by_depots = {
            # external_depot_id -> shift response
            '12345': {
                'shifts': [
                    {
                        'performer_id': 'dbid0_uuid0',
                        'shift_id': '19950',
                        'shift_status': 'in_progress',
                        'started_at': '2020-07-28T08:47:00Z',
                        'closes_at': '2021-11-17T12:12:12Z',  # shift ends soon
                        'shift_type': 'wms',
                    },
                    {
                        'performer_id': 'dbid0_uuid1',
                        'shift_id': '19949',
                        'shift_status': 'in_progress',
                        'started_at': '2020-07-28T08:47:00Z',
                        'closes_at': '2021-11-17T12:14:12Z',
                        'shift_type': 'wms',
                    },
                ],
            },
        }
        return by_depots.get(request.json['depot_id'], {'shifts': []})

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
                    'zone_group': {'required_ids': ['12345']},
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
