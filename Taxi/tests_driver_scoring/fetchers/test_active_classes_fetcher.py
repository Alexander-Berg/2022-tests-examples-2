import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


HEADERS = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
DUP_SEARCH = {
    'order_id': 'order0',
    'order': {
        'request': {
            'source': {'geopoint': [39.60258, 52.569089]},
            'destinations': [{'geopoint': [39.60258, 52.569089]}],
            'surge_price': 1.5,
        },
        'nearest_zone': 'lipetsk',
    },
    'allowed_classes': ['econom', 'comfortplus'],
}
UNIQUE_SEARCH_1 = {
    'order_id': 'order2',
    'order': {
        'request': {
            'source': {'geopoint': [39.6423, 52.57532]},
            'destinations': [{'geopoint': [39.6, 52.5]}],
            'surge_price': 1.4,
        },
    },
    'allowed_classes': ['econom'],
}

DUP_CANDIDATE = {
    'id': 'dbid0_uuid0',
    'route_info': {'time': 500, 'distance': 3200, 'approximate': False},
    'position': [39.59568, 52.568001],
    'classes': ['econom'],
}
SAME_ID_CANDIDATE_1 = {
    'id': 'dbid1_uuid1',
    'route_info': {'time': 500, 'distance': 3200, 'approximate': False},
    'position': [39.5, 52.5],
    'classes': ['econom'],
}
SAME_ID_CANDIDATE_2 = {
    'id': 'dbid1_uuid1',
    'route_info': {'time': 400, 'distance': 3200, 'approximate': False},
    'position': [39.59568, 52.568001],
    'classes': ['econom'],
}
UNIQUE_CANDIDATE_1 = {
    'id': 'dbid2_uuid2',
    'route_info': {'time': 300, 'distance': 3200, 'approximate': False},
    'position': [39.5134, 52.5434],
    'classes': ['econom'],
}
UNIQUE_CANDIDATE_2 = {
    'id': 'dbid3_uuid3',
    'route_info': {'time': 1010, 'distance': 4342, 'approximate': False},
    'position': [39.511334, 52.4523],
    'classes': ['econom'],
}


def _make_umlaas_order(order):
    def set_optional(key, src, dst, dst_key=None):
        val = src.get(key)
        if val is not None:
            dst[key if dst_key is None else dst_key] = val

    def set_optional_geopoint(key, src, dst, dst_key=None):
        val = src.get(key)
        if val is not None:
            dst[key if dst_key is None else dst_key] = {'geopoint': val}

    def set_optional_geopoints(key, src, dst, dst_key=None):
        val = src.get(key)
        if val is not None:
            dst[key if dst_key is None else dst_key] = [
                {'geopoint': elem} for elem in val
            ]

    result = {
        'source': order['request']['source'],
        'allowed_classes': order['allowed_classes'],
    }
    set_optional_geopoint('source', order['request'], result)
    set_optional_geopoints('destinations', order['request'], result)
    set_optional('surge_price', order['request'], result, 'surge')
    set_optional('nearest_zone', order, result)
    set_optional('id', order, result)
    set_optional('id', order, result)

    return result


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
    BONUS_FOR_CLASS_MAX_SURGE=3.0,
    DISPATCH_CLASSES_ORDER=['econom', 'comfortplus', 'business'],
)
async def test_fetch_with_duplicates(taxi_driver_scoring, mockserver):
    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        assert request.json == {
            'driver_ids': [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid1', 'uuid': 'uuid1'},
            ],
            'data_keys': ['classes', 'car_id'],
            'zone_id': 'lipetsk',
        }
        return {
            'drivers': [
                {
                    'uuid': 'uuid0',
                    'dbid': 'dbid0',
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'comfortplus'],  # bonus: 10
                },
                {
                    'uuid': 'uuid1',
                    'dbid': 'dbid1',
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],  # bonus: 20
                },
            ],
        }

    body = {
        'requests': [
            {
                'search': DUP_SEARCH,
                'candidates': [DUP_CANDIDATE, DUP_CANDIDATE],
            },
            {
                'search': DUP_SEARCH,
                'candidates': [SAME_ID_CANDIDATE_1, SAME_ID_CANDIDATE_2],
            },
        ],
        'intent': 'dispatch-buffer',
    }
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk', headers=HEADERS, json=body,
    )
    assert response.status_code == 200
    assert response.json()['responses'] == [
        {
            'search': {'order_id': 'order0'},
            'candidates': [
                {'id': 'dbid0_uuid0', 'score': 490.0},
                {'id': 'dbid0_uuid0', 'score': 490.0},
            ],
        },
        {
            'search': {'order_id': 'order0'},
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 380.0},
                {'id': 'dbid1_uuid1', 'score': 480.0},
            ],
        },
    ]


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
    BONUS_FOR_CLASS_MAX_SURGE=3.0,
    DISPATCH_CLASSES_ORDER=['econom', 'comfortplus', 'business'],
)
async def test_fetch_with_different_zones(taxi_driver_scoring, mockserver):
    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        expected_request1 = {
            'driver_ids': [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid1', 'uuid': 'uuid1'},
            ],
            'data_keys': ['classes', 'car_id'],
            'zone_id': 'lipetsk',
        }
        expected_request2 = {
            'driver_ids': [
                {'dbid': 'dbid0', 'uuid': 'uuid0'},
                {'dbid': 'dbid1', 'uuid': 'uuid1'},
                {'dbid': 'dbid2', 'uuid': 'uuid2'},
            ],
            'data_keys': ['classes', 'car_id'],
        }
        assert (
            request.json == expected_request1
            or request.json == expected_request2
        )
        if request.json == expected_request1:
            return {
                'drivers': [
                    {
                        'uuid': 'uuid0',
                        'dbid': 'dbid0',
                        'position': [39.59568, 52.568001],
                        'classes': ['econom', 'comfortplus'],  # bonus: 10
                    },
                    {
                        'uuid': 'uuid1',
                        'dbid': 'dbid1',
                        'position': [39.59568, 52.568001],
                        'classes': ['econom', 'business'],  # bonus: 20
                    },
                ],
            }

        return {
            'drivers': [
                {
                    'uuid': 'uuid0',
                    'dbid': 'dbid0',
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'comfortplus'],  # bonus: 10
                },
                {
                    'uuid': 'uuid1',
                    'dbid': 'dbid1',
                    'position': [39.59568, 52.568001],
                    'classes': ['econom'],  # bonus: 0
                },
                {
                    'uuid': 'uuid2',
                    'dbid': 'dbid2',
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],  # bonus: 20
                },
            ],
        }

    body = {
        'requests': [
            {
                'search': DUP_SEARCH,
                'candidates': [DUP_CANDIDATE, DUP_CANDIDATE],
            },
            {
                'search': DUP_SEARCH,
                'candidates': [SAME_ID_CANDIDATE_1, SAME_ID_CANDIDATE_2],
            },
            {
                'search': UNIQUE_SEARCH_1,
                'candidates': [
                    DUP_CANDIDATE,
                    SAME_ID_CANDIDATE_1,
                    UNIQUE_CANDIDATE_1,
                ],
            },
        ],
        'intent': 'dispatch-buffer',
    }
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk', headers=HEADERS, json=body,
    )
    assert response.status_code == 200
    assert response.json()['responses'] == [
        {
            'search': {'order_id': 'order0'},
            'candidates': [
                {'id': 'dbid0_uuid0', 'score': 490.0},
                {'id': 'dbid0_uuid0', 'score': 490.0},
            ],
        },
        {
            'search': {'order_id': 'order0'},
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 380.0},
                {'id': 'dbid1_uuid1', 'score': 480.0},
            ],
        },
        {
            'search': {'order_id': 'order2'},
            'candidates': [
                {'id': 'dbid2_uuid2', 'score': 280.0},
                {'id': 'dbid0_uuid0', 'score': 490.0},
                {'id': 'dbid1_uuid1', 'score': 500.0},
            ],
        },
    ]
