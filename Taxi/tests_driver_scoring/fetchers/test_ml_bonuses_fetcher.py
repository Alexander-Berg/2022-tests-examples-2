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
SAME_ID_SEARCH_1 = {
    'order_id': 'order1',
    'order': {
        'request': {
            'source': {'geopoint': [39.60258, 52.569089]},
            'destinations': [{'geopoint': [39.6, 52.5]}],
            'surge_price': 1.5,
        },
        'nearest_zone': 'lipetsk',
    },
    'allowed_classes': ['econom', 'comfortplus'],
}
SAME_ID_SEARCH_2 = {
    'order_id': 'order1',
    'order': {
        'request': {
            'source': {'geopoint': [39.60258, 52.569089]},
            'destinations': [{'geopoint': [39.60258, 52.569089]}],
            'surge_price': 1.5,
        },
        'nearest_zone': 'lipetsk',
    },
    'allowed_classes': ['econom'],
}
UNIQUE_SEARCH_1 = {
    'order_id': 'order2',
    'order': {
        'request': {
            'source': {'geopoint': [39.6423, 52.57532]},
            'destinations': [{'geopoint': [39.6, 52.5]}],
            'surge_price': 1.4,
        },
        'nearest_zone': 'lipetsk',
    },
    'allowed_classes': ['econom'],
}
UNIQUE_SEARCH_2 = {
    'order_id': 'order3',
    'order': {
        'request': {
            'source': {'geopoint': [39.4, 52.6]},
            'destinations': [{'geopoint': [39.495, 52.227]}],
            'surge_price': 1.5,
        },
        'nearest_zone': 'lipetsk',
    },
    'allowed_classes': ['econom', 'comfortplus'],
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


def _make_umlaas_order(search):
    def set_optional(key, src, dst, dst_key=None):
        val = src.get(key)
        if val is not None:
            dst[key if dst_key is None else dst_key] = val

    def set_optional_geopoint(key, src, dst, dst_key=None):
        val = src.get(key)
        if val is not None:
            dst[key if dst_key is None else dst_key] = val

    def set_optional_geopoints(key, src, dst, dst_key=None):
        val = src.get(key)
        if val is not None:
            dst[key if dst_key is None else dst_key] = [elem for elem in val]

    result = {
        'source': search['order']['request']['source'],
        'allowed_classes': search['allowed_classes'],
    }
    set_optional_geopoint('source', search['order']['request'], result)
    set_optional_geopoints('destinations', search['order']['request'], result)
    set_optional('surge_price', search['order']['request'], result, 'surge')
    set_optional('nearest_zone', search['order'], result)
    set_optional('order_id', search, result, 'id')

    return result


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
)
async def test_fetch_with_duplicates(taxi_driver_scoring, mockserver):
    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/candidates-bonuses',
    )
    def _bonuses(request):
        order_candidates = {
            'order': _make_umlaas_order(DUP_SEARCH),
            'candidates': [DUP_CANDIDATE, DUP_CANDIDATE],
        }
        assert request.json == {
            'requests': [order_candidates, order_candidates],
        }
        return {
            'responses': [
                {
                    'candidates': [
                        {
                            'id': DUP_CANDIDATE['id'],
                            'bonuses': [
                                {'name': 'a', 'value': 10.0},
                                {'name': 'b', 'value': 20.0},
                            ],
                        },
                    ],
                },
                {
                    'candidates': [
                        {
                            'id': DUP_CANDIDATE['id'],
                            'bonuses': [
                                {'name': 'a', 'value': 30.0},
                                {'name': 'b', 'value': 40.0},
                            ],
                        },
                    ],
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
                'candidates': [DUP_CANDIDATE, DUP_CANDIDATE],
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
                {'id': 'dbid0_uuid0', 'score': 470.0},
                {'id': 'dbid0_uuid0', 'score': 500.0},
            ],
        },
        {
            'search': {'order_id': 'order0'},
            'candidates': [
                {'id': 'dbid0_uuid0', 'score': 430.0},
                {'id': 'dbid0_uuid0', 'score': 500.0},
            ],
        },
    ]


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
)
async def test_fetch_with_duplicated_ids(taxi_driver_scoring, mockserver):
    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/candidates-bonuses',
    )
    def _bonuses(request):
        assert request.json == {
            'requests': [
                {
                    'order': _make_umlaas_order(SAME_ID_SEARCH_1),
                    'candidates': [SAME_ID_CANDIDATE_2, SAME_ID_CANDIDATE_1],
                },
                {
                    'order': _make_umlaas_order(SAME_ID_SEARCH_2),
                    'candidates': [SAME_ID_CANDIDATE_1, SAME_ID_CANDIDATE_2],
                },
            ],
        }
        return {
            'responses': [
                {
                    'candidates': [
                        {
                            'id': SAME_ID_CANDIDATE_2['id'],
                            'bonuses': [
                                {'name': 'a', 'value': 10.0},
                                {'name': 'b', 'value': 20.0},
                            ],
                        },
                    ],
                },
                {
                    'candidates': [
                        {
                            'id': SAME_ID_CANDIDATE_1['id'],
                            'bonuses': [
                                {'name': 'a', 'value': 30.0},
                                {'name': 'b', 'value': 40.0},
                            ],
                        },
                    ],
                },
            ],
        }

    body = {
        'requests': [
            {
                'search': SAME_ID_SEARCH_1,
                'candidates': [SAME_ID_CANDIDATE_2, SAME_ID_CANDIDATE_1],
            },
            {
                'search': SAME_ID_SEARCH_2,
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
            'search': {'order_id': 'order1'},
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 370.0},
                {'id': 'dbid1_uuid1', 'score': 500.0},
            ],
        },
        {
            'search': {'order_id': 'order1'},
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 400.0},
                {'id': 'dbid1_uuid1', 'score': 430.0},
            ],
        },
    ]


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
)
async def test_fetch_with_skipped_candidates(taxi_driver_scoring, mockserver):
    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/candidates-bonuses',
    )
    def _bonuses(request):
        assert request.json == {
            'requests': [
                {
                    'order': _make_umlaas_order(UNIQUE_SEARCH_1),
                    'candidates': [UNIQUE_CANDIDATE_1, UNIQUE_CANDIDATE_2],
                },
                {
                    'order': _make_umlaas_order(UNIQUE_SEARCH_2),
                    'candidates': [UNIQUE_CANDIDATE_1, UNIQUE_CANDIDATE_2],
                },
            ],
        }
        return {
            'responses': [
                {
                    'candidates': [
                        {
                            'id': UNIQUE_CANDIDATE_1['id'],
                            'bonuses': [
                                {'name': 'a', 'value': 10.0},
                                {'name': 'b', 'value': 20.0},
                            ],
                        },
                    ],
                },
                {
                    'candidates': [
                        {
                            'id': UNIQUE_CANDIDATE_2['id'],
                            'bonuses': [
                                {'name': 'a', 'value': 30.0},
                                {'name': 'b', 'value': 40.0},
                            ],
                        },
                    ],
                },
            ],
        }

    body = {
        'requests': [
            {
                'search': UNIQUE_SEARCH_1,
                'candidates': [UNIQUE_CANDIDATE_1, UNIQUE_CANDIDATE_2],
            },
            {
                'search': UNIQUE_SEARCH_2,
                'candidates': [UNIQUE_CANDIDATE_1, UNIQUE_CANDIDATE_2],
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
            'search': {'order_id': 'order2'},
            'candidates': [
                {'id': 'dbid2_uuid2', 'score': 270.0},
                {'id': 'dbid3_uuid3', 'score': 1010.0},
            ],
        },
        {
            'search': {'order_id': 'order3'},
            'candidates': [
                {'id': 'dbid2_uuid2', 'score': 300.0},
                {'id': 'dbid3_uuid3', 'score': 940.0},
            ],
        },
    ]
