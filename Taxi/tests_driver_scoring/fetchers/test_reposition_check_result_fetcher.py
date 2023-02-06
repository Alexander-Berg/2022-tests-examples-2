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
    'metadata': {'reposition_check_required': True},
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
    'metadata': {'reposition_check_required': True},
}
UNIQUE_CANDIDATE_2 = {
    'id': 'dbid3_uuid3',
    'route_info': {'time': 1010, 'distance': 4342, 'approximate': False},
    'position': [39.511334, 52.4523],
    'classes': ['econom'],
}


def _make_request_orders(searches):
    return [
        {
            'id': search['order_id'].encode(),
            'zone': search['order']['nearest_zone'].encode(),
            'allowed_classes': [
                cls.encode() for cls in search['allowed_classes']
            ],
        }
        for search in searches
    ]


def _make_request_drivers(candidates):
    return [
        {
            'dbid': candidate['id'].split('_')[0].encode(),
            'uuid': candidate['id'].split('_')[1].encode(),
        }
        for candidate in candidates
    ]


def _make_check_requests(deprecated_protocol, check_requests, candidates):
    result = []

    for check_req in check_requests:
        new_check_req = {'order_id': check_req[0], 'driver_id': check_req[1]}

        if not deprecated_protocol:
            new_check_req['pickup_route_info'] = {
                'time': candidates[check_req[1]]['route_info']['time'],
                'distance': candidates[check_req[1]]['route_info']['distance'],
            }

        result.append(new_check_req)

    return result


def _make_match_orders_drivers_request(
        searches,
        candidates,
        check_requests,
        router_experiments=None,
        deprecated_protocol=False,
):
    result = {
        'orders': _make_request_orders(searches),
        'drivers': _make_request_drivers(candidates),
        'check_requests': _make_check_requests(
            deprecated_protocol, check_requests, candidates,
        ),
    }

    if router_experiments:
        result['router_experiments'] = router_experiments

    return result


def _add_reposition_score_experiment(experiments3):
    experiments3.add_experiment(
        consumers=['driver-scoring/reposition-score'],
        name='driver_scoring_reposition_score',
        match={
            'enabled': True,
            'consumers': [{'name': 'driver-scoring/reposition-score'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'home',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'reposition_mode',
                        'arg_type': 'string',
                        'value': 'home',
                    },
                },
                'value': {'b': 100.0, 'c': 1.0, 'd': 40.0},
            },
            {
                'title': 'SuperSurge_completed',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'reposition_mode',
                        'arg_type': 'string',
                        'value': 'SuperSurge_completed',
                    },
                },
                'value': {'b': 55.0, 'c': 2.0, 'd': 20.0},
            },
            {
                'title': 'poi',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'reposition_mode',
                        'arg_type': 'string',
                        'value': 'poi',
                    },
                },
                'value': {'b': 80, 'c': 1.0, 'd': 40.0},
            },
        ],
    )


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
)
@pytest.mark.reposition_matcher_check_results(
    {
        (b'dbid0', b'uuid0', b'order0'): {'mode': 'home', 'score': 0.5},
    },  # bonus: 120
)
@pytest.mark.expect_reposition_matcher_check_request(
    _make_match_orders_drivers_request(
        searches=[DUP_SEARCH],
        candidates=[DUP_CANDIDATE],
        check_requests=[(0, 0)],
    ),
)
async def test_fetch_with_duplicates(taxi_driver_scoring, experiments3):
    _add_reposition_score_experiment(experiments3)
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

    expected_candidate = {
        'id': 'dbid0_uuid0',
        'score': 380.0,
        'metadata': {
            'reposition': {
                'mode': 'home',
                'suitable': True,
                'score': 0.5,
                'score_parameters': {'b': 100.0, 'c': 1.0, 'd': 40.0},
            },
        },
    }

    assert response.json()['responses'] == [
        {
            'search': {'order_id': 'order0'},
            'candidates': [expected_candidate, expected_candidate],
        },
        {
            'search': {'order_id': 'order0'},
            'candidates': [expected_candidate, expected_candidate],
        },
    ]


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
)
@pytest.mark.reposition_matcher_check_results(
    {
        (b'dbid0', b'uuid0', b'order0'): {
            'mode': 'home',
            'score': 0.5,
        },  # bonus: 120
        (b'dbid0', b'uuid0', b'order2'): {
            'mode': 'poi',
            'score': 0.5,
        },  # bonus: 100
        (b'dbid2', b'uuid2', b'order0'): {
            'mode': 'SuperSurge_completed',
            'score': 0.5,  # bonus: 60
        },
        (b'dbid3', b'uuid3', b'order2'): {
            'mode': 'home',
            'suitable': False,  # filtered
            'score': 0.5,
        },
    },
)
@pytest.mark.expect_reposition_matcher_check_request(
    _make_match_orders_drivers_request(
        searches=[DUP_SEARCH, UNIQUE_SEARCH_1],
        candidates=[DUP_CANDIDATE, UNIQUE_CANDIDATE_1, UNIQUE_CANDIDATE_2],
        check_requests=[(0, 0), (0, 1), (1, 2), (1, 0)],
    ),
)
async def test_fetch_with_some_duplicates(taxi_driver_scoring, experiments3):
    _add_reposition_score_experiment(experiments3)
    body = {
        'requests': [
            {'search': DUP_SEARCH, 'candidates': [UNIQUE_CANDIDATE_1]},
            {
                'search': UNIQUE_SEARCH_1,
                'candidates': [UNIQUE_CANDIDATE_2, DUP_CANDIDATE],
            },
            {'search': DUP_SEARCH, 'candidates': [DUP_CANDIDATE]},
        ],
        'intent': 'dispatch-buffer',
    }
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk', headers=HEADERS, json=body,
    )
    assert response.status_code == 200

    expected = [
        {
            'search': {'order_id': 'order0'},
            'candidates': [
                {
                    'id': 'dbid2_uuid2',
                    'score': 240.0,
                    'metadata': {
                        'reposition_check_required': True,
                        'reposition': {
                            'mode': 'SuperSurge_completed',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 55.0,
                                'c': 2.0,
                                'd': 20.0,
                            },
                        },
                    },
                },
            ],
        },
        {
            'search': {'order_id': 'order2'},
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'score': 400.0,
                    'metadata': {
                        'reposition': {
                            'mode': 'poi',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 80.0,
                                'c': 1.0,
                                'd': 40.0,
                            },
                        },
                    },
                },
            ],
        },
        {
            'search': {'order_id': 'order0'},
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'score': 380.0,
                    'metadata': {
                        'reposition': {
                            'mode': 'home',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 100.0,
                                'c': 1.0,
                                'd': 40.0,
                            },
                        },
                    },
                },
            ],
        },
    ]

    assert response.json()['responses'] == expected


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
)
@pytest.mark.reposition_matcher_check_results(
    {
        (b'dbid1', b'uuid1', b'order1'): {
            'mode': 'home',
            'score': 0.5,
        },  # bonus: 120
        (b'dbid2', b'uuid2', b'order1'): {
            'mode': 'SuperSurge_completed',
            'score': 0.5,  # bonus: 60
        },
        (b'dbid1', b'uuid1', b'order2'): {
            'mode': 'home',
            'score': 0.5,
        },  # bonus: 120
        (b'dbid3', b'uuid3', b'order2'): {
            'mode': 'poi',
            'score': 0.5,
        },  # bonus: 100
    },
)
@pytest.mark.expect_reposition_matcher_check_request(
    _make_match_orders_drivers_request(
        searches=[SAME_ID_SEARCH_1, SAME_ID_SEARCH_2, UNIQUE_SEARCH_1],
        candidates=[
            SAME_ID_CANDIDATE_1,
            SAME_ID_CANDIDATE_2,
            UNIQUE_CANDIDATE_1,
            UNIQUE_CANDIDATE_2,
        ],
        check_requests=[(0, 0), (0, 1), (1, 0), (1, 2), (2, 1), (2, 3)],
    ),
)
async def test_fetch_with_duplicated_ids(taxi_driver_scoring, experiments3):
    _add_reposition_score_experiment(experiments3)

    body = {
        'requests': [
            {
                'search': SAME_ID_SEARCH_1,
                'candidates': [SAME_ID_CANDIDATE_1, SAME_ID_CANDIDATE_2],
            },
            {
                'search': SAME_ID_SEARCH_2,
                'candidates': [SAME_ID_CANDIDATE_1, UNIQUE_CANDIDATE_1],
            },
            {
                'search': UNIQUE_SEARCH_1,
                'candidates': [SAME_ID_CANDIDATE_2, UNIQUE_CANDIDATE_2],
            },
            {'search': UNIQUE_SEARCH_2, 'candidates': []},
        ],
        'intent': 'dispatch-buffer',
    }
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk', headers=HEADERS, json=body,
    )
    assert response.status_code == 200

    expected = [
        {
            'search': {'order_id': 'order1'},
            'candidates': [
                {
                    'id': 'dbid1_uuid1',
                    'score': 280.0,
                    'metadata': {
                        'reposition': {
                            'mode': 'home',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 100.0,
                                'c': 1.0,
                                'd': 40.0,
                            },
                        },
                    },
                },
                {
                    'id': 'dbid1_uuid1',
                    'score': 380.0,
                    'metadata': {
                        'reposition_check_required': True,
                        'reposition': {
                            'mode': 'home',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 100.0,
                                'c': 1.0,
                                'd': 40.0,
                            },
                        },
                    },
                },
            ],
        },
        {
            'search': {'order_id': 'order1'},
            'candidates': [
                {
                    'id': 'dbid2_uuid2',
                    'score': 240.0,
                    'metadata': {
                        'reposition_check_required': True,
                        'reposition': {
                            'mode': 'SuperSurge_completed',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 55.0,
                                'c': 2.0,
                                'd': 20.0,
                            },
                        },
                    },
                },
                {
                    'id': 'dbid1_uuid1',
                    'score': 380.0,
                    'metadata': {
                        'reposition_check_required': True,
                        'reposition': {
                            'mode': 'home',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 100.0,
                                'c': 1.0,
                                'd': 40.0,
                            },
                        },
                    },
                },
            ],
        },
        {
            'search': {'order_id': 'order2'},
            'candidates': [
                {
                    'id': 'dbid1_uuid1',
                    'score': 280.0,
                    'metadata': {
                        'reposition': {
                            'mode': 'home',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 100.0,
                                'c': 1.0,
                                'd': 40.0,
                            },
                        },
                    },
                },
                {
                    'id': 'dbid3_uuid3',
                    'score': 910.0,
                    'metadata': {
                        'reposition': {
                            'mode': 'poi',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 80.0,
                                'c': 1.0,
                                'd': 40.0,
                            },
                        },
                    },
                },
            ],
        },
        {'search': {'order_id': 'order3'}, 'candidates': []},
    ]

    assert response.json()['responses'] == expected


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='reposition_settings.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
)
@pytest.mark.reposition_matcher_check_results(
    {
        (b'dbid1', b'uuid1', b'order1'): {
            'mode': 'home',
            'score': 0.5,
        },  # bonus: 120
        (b'dbid2', b'uuid2', b'order1'): {
            'mode': 'SuperSurge_completed',
            'score': 0.5,  # bonus: 60
        },
        (b'dbid1', b'uuid1', b'order2'): {
            'mode': 'home',
            'score': 0.5,
        },  # bonus: 120
    },
)
@pytest.mark.expect_reposition_matcher_check_request(
    _make_match_orders_drivers_request(
        searches=[SAME_ID_SEARCH_1, SAME_ID_SEARCH_2],
        candidates=[SAME_ID_CANDIDATE_1, UNIQUE_CANDIDATE_1],
        check_requests=[(0, 0), (1, 0), (1, 1)],
    ),
)
async def test_fetch_considering_check_required(
        taxi_driver_scoring, experiments3,
):
    _add_reposition_score_experiment(experiments3)

    body = {
        'requests': [
            {
                'search': SAME_ID_SEARCH_1,
                'candidates': [SAME_ID_CANDIDATE_1, SAME_ID_CANDIDATE_2],
            },
            {
                'search': SAME_ID_SEARCH_2,
                'candidates': [SAME_ID_CANDIDATE_1, UNIQUE_CANDIDATE_1],
            },
            {
                'search': UNIQUE_SEARCH_1,
                'candidates': [SAME_ID_CANDIDATE_2, UNIQUE_CANDIDATE_2],
            },
            {'search': UNIQUE_SEARCH_2, 'candidates': []},
        ],
        'intent': 'dispatch-buffer',
    }
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk', headers=HEADERS, json=body,
    )
    assert response.status_code == 200

    expected = [
        {
            'search': {'order_id': 'order1'},
            'candidates': [
                {
                    'id': 'dbid1_uuid1',
                    'score': 380.0,
                    'metadata': {
                        'reposition_check_required': True,
                        'reposition': {
                            'mode': 'home',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 100.0,
                                'c': 1.0,
                                'd': 40.0,
                            },
                        },
                    },
                },
                {'id': 'dbid1_uuid1', 'score': 400.0},
            ],
        },
        {
            'search': {'order_id': 'order1'},
            'candidates': [
                {
                    'id': 'dbid2_uuid2',
                    'score': 240.0,
                    'metadata': {
                        'reposition_check_required': True,
                        'reposition': {
                            'mode': 'SuperSurge_completed',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 55.0,
                                'c': 2.0,
                                'd': 20.0,
                            },
                        },
                    },
                },
                {
                    'id': 'dbid1_uuid1',
                    'score': 380.0,
                    'metadata': {
                        'reposition_check_required': True,
                        'reposition': {
                            'mode': 'home',
                            'suitable': True,
                            'score': 0.5,
                            'score_parameters': {
                                'b': 100.0,
                                'c': 1.0,
                                'd': 40.0,
                            },
                        },
                    },
                },
            ],
        },
        {
            'search': {'order_id': 'order2'},
            'candidates': [
                {'id': 'dbid1_uuid1', 'score': 400.0},
                {'id': 'dbid3_uuid3', 'score': 1010.0},
            ],
        },
        {'search': {'order_id': 'order3'}, 'candidates': []},
    ]
    assert response.json()['responses'] == expected
