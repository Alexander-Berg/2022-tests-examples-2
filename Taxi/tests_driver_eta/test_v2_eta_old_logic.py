import json

import pytest

import tests_driver_eta.dispatch_settings as dispatch_settings


SEARCH_PARAMS = {
    'route_points': [[0, 0]],
    'zone_id': 'moscow',
    'classes': [
        {
            'class_name': 'comfort',
            'is_extended_radius': True,
            'search_settings': {
                'max_line_dist': 3000,
                'max_dist': 4000,
                'max_time': 100,
            },
        },
        {
            'class_name': 'econom',
            'is_extended_radius': True,
            'search_settings': {
                'max_line_dist': 4000,
                'max_dist': 5000,
                'max_time': 200,
            },
        },
        {
            'class_name': 'vip',
            'is_extended_radius': True,
            'search_settings': {
                'max_line_dist': 100000,
                'max_dist': 100000,
                'max_time': 100000,
            },
        },
    ],
    'provide_candidates': True,
    'extra_params': [
        {
            'consumers': ['candidates', 'lookup_ordering'],
            'params': {
                'order': {'request': {'offer': 'offer_id'}},
                'metadata': 'something',
            },
        },
    ],
}

SEARCH_SETTINGS_COMFORT = {
    'limit': 10,
    'max_distance': 3000,
    'max_route_distance': 4000,
    'max_route_time': 100,
}

SEARCH_SETTINGS_ECONOM = {
    'limit': 10,
    'max_distance': 4000,
    'max_route_distance': 5000,
    'max_route_time': 200,
}

SEARCH_SETTINGS_VIP = {
    'limit': 10,
    'max_distance': 20000,
    'max_route_distance': 20000,
    'max_route_time': 2000,
}

URL = '/driver-eta/v2/eta'

CANDIDATE_ZERO = {
    'id': 'dbid0_uuid0',
    'dbid': 'dbid0',
    'uuid': 'uuid0',
    'position': [55.0, 35.0],
    'classes': ['econom', 'comfort'],
    'route_info': {'distance': 0, 'time': 50, 'approximate': False},
    'status': {'driver': 'free'},
}

CANDIDATE_ONE = {
    'id': 'dbid1_uuid1',
    'dbid': 'dbid1',
    'uuid': 'uuid1',
    'position': [55.0, 35.0],
    'classes': ['econom', 'comfort'],
    'route_info': {'distance': 0, 'time': 100, 'approximate': False},
    'status': {'driver': 'free'},
}

CANDIDATE_TWO = {
    'id': 'dbid2_uuid2',
    'dbid': 'dbid2',
    'uuid': 'uuid2',
    'position': [55.0, 35.0],
    'classes': ['econom', 'vip'],
    'route_info': {'distance': 0, 'time': 200, 'approximate': False},
    'status': {'driver': 'free'},
}

CANDIDATE_FOUR = {
    'id': 'id1',
    'dbid': 'dbid1',
    'uuid': 'uuid1',
    'position': [55.0, 35.0],
    'classes': ['econom'],
    'route_info': {'distance': 0, 'time': 100, 'approximate': False},
    'status': {'driver': 'free'},
}

CANDIDATE_FIVE = {
    'id': 'id2',
    'dbid': 'dbid0',
    'uuid': 'uuid0',
    'position': [55.0, 35.0],
    'classes': ['econom'],
    'route_info': {'distance': 0, 'time': 50, 'approximate': False},
    'status': {'driver': 'free'},
}

CANDIDATE_SIX = {
    'id': 'id3',
    'dbid': 'dbid0',
    'uuid': 'uuid1',
    'position': [55.0, 35.0],
    'classes': ['vip'],
    'route_info': {'distance': 0, 'time': 100, 'approximate': False},
    'status': {'driver': 'free'},
}

CANDIDATE_SEVEN = {
    'id': 'id2',
    'dbid': 'dbid2',
    'uuid': 'uuid2',
    'position': [55.0, 35.0],
    'classes': ['econom'],
    'route_info': {'distance': 0, 'time': 50, 'approximate': False},
    'status': {'driver': 'free'},
}


@pytest.fixture(name='mock_umlaas_dispatch_unavailable')
def _mock_umlaas_dispatch_unavailable(mockserver):
    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/search-radius-prediction',
    )
    def _umlaas_dispatch(request):
        return mockserver.make_response(json={}, status=500)


@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_eta(
        taxi_driver_eta,
        mockserver,
        testpoint,
        mock_umlaas_dispatch_unavailable,
):
    @testpoint('ordering-bulk-response')
    def _ordering_response(request):
        return {'change_response': True, 'data': 'fail'}

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _ordering(request):
        return mockserver.make_response(json={}, status=500)

    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        data = {
            'candidates': [CANDIDATE_FOUR, CANDIDATE_FIVE, CANDIDATE_SIX],
            'search_details': {
                'econom': {
                    'preferred': {
                        'line_distance': 1001,
                        'route_time': 101,
                        'route_distance': 1101,
                    },
                    'actual': {
                        'line_distance': 2001,
                        'route_time': 201,
                        'route_distance': 2101,
                    },
                },
                'comfort': {
                    'preferred': {
                        'line_distance': 1002,
                        'route_time': 102,
                        'route_distance': 1102,
                    },
                    'actual': {
                        'line_distance': 2002,
                        'route_time': 202,
                        'route_distance': 2102,
                    },
                },
                'vip': {
                    'preferred': {
                        'line_distance': 1003,
                        'route_time': 103,
                        'route_distance': 1103,
                    },
                    'actual': {
                        'line_distance': 2003,
                        'route_time': 203,
                        'route_distance': 2103,
                    },
                },
                'express': {
                    'preferred': {
                        'line_distance': 1004,
                        'route_time': 104,
                        'route_distance': 1104,
                    },
                    'actual': {
                        'line_distance': 2004,
                        'route_time': 204,
                        'route_distance': 2104,
                    },
                },
            },
        }
        return mockserver.make_response(json=data, status=200)

    response = await taxi_driver_eta.post(URL, json=SEARCH_PARAMS)
    assert response.status_code == 200
    answer = response.json()
    assert answer == {
        'classes': {
            'comfort': {
                'found': False,
                'no_cars_order_enabled': False,
                'paid_supply_enabled': False,
                'order_allowed': False,
            },
            'vip': {
                'found': True,
                'estimated_time': 100,
                'estimated_distance': 0,
                'no_cars_order_enabled': False,
                'paid_supply_enabled': False,
                'order_allowed': True,
                'candidates': [
                    {
                        'dbid': 'dbid0',
                        'uuid': 'uuid1',
                        'status': 'free',
                        'position': [55.0, 35.0],
                        'route_info': {
                            'approximate': False,
                            'distance': 0,
                            'time': 100,
                        },
                        'chain_info': {},
                    },
                ],
            },
            'econom': {
                'found': True,
                'estimated_time': 100,
                'estimated_distance': 0,
                'no_cars_order_enabled': False,
                'paid_supply_enabled': False,
                'order_allowed': True,
                'candidates': [
                    {
                        'dbid': 'dbid1',
                        'uuid': 'uuid1',
                        'status': 'free',
                        'position': [55.0, 35.0],
                        'route_info': {
                            'approximate': False,
                            'distance': 0,
                            'time': 100,
                        },
                        'chain_info': {},
                    },
                    {
                        'dbid': 'dbid0',
                        'uuid': 'uuid0',
                        'status': 'free',
                        'position': [55.0, 35.0],
                        'route_info': {
                            'approximate': False,
                            'distance': 0,
                            'time': 50,
                        },
                        'chain_info': {},
                    },
                ],
            },
        },
    }


@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_eta_lookup_ordering(
        taxi_driver_eta, mockserver, mock_umlaas_dispatch_unavailable,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _ordering(request):
        body = json.loads(request.get_data())
        first = body['requests'][0]['search']
        assert first['metadata'] == 'something'
        assert first['order']['request'] == {
            'offer': 'offer_id',
            'source': {'geopoint': [0.0, 0.0]},
            'surge_price': None,
        }
        data = {
            'responses': [
                {
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 1},
                        {'id': 'dbid0_uuid0', 'score': 2},
                        {'id': 'dbid2_uuid2', 'score': 3},
                    ],
                },
            ],
        }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        data = {
            'candidates': [
                {
                    'id': 'dbid2_uuid2',
                    'dbid': 'dbid2',
                    'uuid': 'uuid2',
                    'position': [55.0, 35.0],
                    'classes': ['econom'],
                    'route_info': {
                        'distance': 0,
                        'time': 200,
                        'approximate': False,
                    },
                    'status': {'driver': 'free'},
                },
                {
                    'id': 'dbid1_uuid1',
                    'dbid': 'dbid1',
                    'uuid': 'uuid1',
                    'position': [55.0, 35.0],
                    'classes': ['econom'],
                    'route_info': {
                        'distance': 0,
                        'time': 100,
                        'approximate': False,
                    },
                    'status': {'driver': 'free'},
                },
                {
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'position': [55.0, 35.0],
                    'classes': ['econom'],
                    'route_info': {
                        'distance': 0,
                        'time': 50,
                        'approximate': False,
                    },
                    'status': {'driver': 'free'},
                },
            ],
            'search_details': {
                'econom': {
                    'preferred': {
                        'line_distance': 1001,
                        'route_time': 101,
                        'route_distance': 1101,
                    },
                    'actual': {
                        'line_distance': 2001,
                        'route_time': 201,
                        'route_distance': 2101,
                    },
                },
                'comfort': {
                    'preferred': {
                        'line_distance': 1002,
                        'route_time': 102,
                        'route_distance': 1102,
                    },
                    'actual': {
                        'line_distance': 2002,
                        'route_time': 202,
                        'route_distance': 2102,
                    },
                },
                'vip': {
                    'preferred': {
                        'line_distance': 1003,
                        'route_time': 103,
                        'route_distance': 1103,
                    },
                    'actual': {
                        'line_distance': 2003,
                        'route_time': 203,
                        'route_distance': 2103,
                    },
                },
                'express': {
                    'preferred': {
                        'line_distance': 1004,
                        'route_time': 104,
                        'route_distance': 1104,
                    },
                    'actual': {
                        'line_distance': 2004,
                        'route_time': 204,
                        'route_distance': 2104,
                    },
                },
            },
        }
        return mockserver.make_response(json=data, status=200)

    response = await taxi_driver_eta.post(URL, json=SEARCH_PARAMS)
    assert response.status_code == 200
    answer = response.json()
    assert answer == {
        'classes': {
            'comfort': {
                'found': False,
                'no_cars_order_enabled': False,
                'paid_supply_enabled': False,
                'order_allowed': False,
            },
            'vip': {
                'found': False,
                'no_cars_order_enabled': False,
                'paid_supply_enabled': False,
                'order_allowed': False,
            },
            'econom': {
                'found': True,
                'estimated_time': 100,
                'estimated_distance': 0,
                'no_cars_order_enabled': False,
                'paid_supply_enabled': False,
                'order_allowed': True,
                'candidates': [
                    {
                        'dbid': 'dbid1',
                        'uuid': 'uuid1',
                        'status': 'free',
                        'position': [55.0, 35.0],
                        'route_info': {
                            'approximate': False,
                            'distance': 0,
                            'time': 100,
                        },
                        'chain_info': {},
                    },
                    {
                        'dbid': 'dbid0',
                        'uuid': 'uuid0',
                        'status': 'free',
                        'position': [55.0, 35.0],
                        'route_info': {
                            'approximate': False,
                            'distance': 0,
                            'time': 50,
                        },
                        'chain_info': {},
                    },
                    {
                        'dbid': 'dbid2',
                        'uuid': 'uuid2',
                        'status': 'free',
                        'position': [55.0, 35.0],
                        'route_info': {
                            'approximate': False,
                            'distance': 0,
                            'time': 200,
                        },
                        'chain_info': {},
                    },
                ],
            },
        },
    }


@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_eta_doubled_candidates(
        taxi_driver_eta, mockserver, mock_umlaas_dispatch_unavailable,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _ordering(request):
        data = {
            'responses': [
                {
                    'candidates': [
                        {'id': 'dbid0_uuid0', 'score': 1},
                        {'id': 'dbid0_uuid0', 'score': 2},
                        {'id': 'dbid0_uuid0', 'score': 3},
                    ],
                },
            ],
        }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        data = {
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'dbid': 'dbid0',
                    'uuid': 'uuid0',
                    'position': [55.0, 35.0],
                    'classes': ['econom'],
                    'route_info': {
                        'distance': 0,
                        'time': route_info_time,
                        'approximate': False,
                    },
                    'status': {'driver': 'free'},
                }
                for route_info_time in [50, 100, 150]
            ],
            'search_details': {
                'econom': {
                    'preferred': {
                        'line_distance': 1001,
                        'route_time': 101,
                        'route_distance': 1101,
                    },
                    'actual': {
                        'line_distance': 2001,
                        'route_time': 201,
                        'route_distance': 2101,
                    },
                },
                'comfort': {
                    'preferred': {
                        'line_distance': 1002,
                        'route_time': 102,
                        'route_distance': 1102,
                    },
                    'actual': {
                        'line_distance': 2002,
                        'route_time': 202,
                        'route_distance': 2102,
                    },
                },
                'vip': {
                    'preferred': {
                        'line_distance': 1003,
                        'route_time': 103,
                        'route_distance': 1103,
                    },
                    'actual': {
                        'line_distance': 2003,
                        'route_time': 203,
                        'route_distance': 2103,
                    },
                },
                'express': {
                    'preferred': {
                        'line_distance': 1004,
                        'route_time': 104,
                        'route_distance': 1104,
                    },
                    'actual': {
                        'line_distance': 2004,
                        'route_time': 204,
                        'route_distance': 2104,
                    },
                },
            },
        }
        return mockserver.make_response(json=data, status=200)

    response = await taxi_driver_eta.post(URL, json=SEARCH_PARAMS)
    assert response.status_code == 200
    answer = response.json()
    assert answer == {
        'classes': {
            'comfort': {
                'found': False,
                'no_cars_order_enabled': False,
                'paid_supply_enabled': False,
                'order_allowed': False,
            },
            'vip': {
                'found': False,
                'no_cars_order_enabled': False,
                'paid_supply_enabled': False,
                'order_allowed': False,
            },
            'econom': {
                'found': True,
                'estimated_time': 50,
                'estimated_distance': 0,
                'no_cars_order_enabled': False,
                'paid_supply_enabled': False,
                'order_allowed': True,
                'candidates': [
                    {
                        'dbid': 'dbid0',
                        'uuid': 'uuid0',
                        'status': 'free',
                        'position': [55.0, 35.0],
                        'route_info': {
                            'approximate': False,
                            'distance': 0,
                            'time': 50,
                        },
                        'chain_info': {},
                    },
                ],
            },
        },
    }


@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_eta_lookup_ordering_bulk(
        taxi_driver_eta, mockserver, mock_umlaas_dispatch_unavailable,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _ordering_bulk(request):
        data = {
            'responses': [
                {
                    'candidates': [
                        {'id': 'dbid0_uuid0', 'score': 4},
                        {'id': 'dbid1_uuid1', 'score': 5},
                    ],
                },
                {
                    'candidates': [
                        {'id': 'dbid1_uuid1', 'score': 1},
                        {'id': 'dbid0_uuid0', 'score': 2},
                        {'id': 'dbid2_uuid2', 'score': 3},
                    ],
                },
                {'candidates': [{'id': 'dbid2_uuid2', 'score': 5}]},
            ],
        }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        data = {'candidates': [CANDIDATE_TWO, CANDIDATE_ONE, CANDIDATE_ZERO]}

        return mockserver.make_response(json=data, status=200)

    response = await taxi_driver_eta.post(URL, json=SEARCH_PARAMS)
    assert response.status_code == 200
    answer = response.json()
    classes = answer['classes']
    assert len(classes['comfort']['candidates']) == 2
    assert classes['comfort']['candidates'][0]['dbid'] == 'dbid0'
    assert classes['comfort']['candidates'][1]['dbid'] == 'dbid1'

    assert len(classes['econom']['candidates']) == 3
    assert classes['econom']['candidates'][0]['dbid'] == 'dbid1'
    assert classes['econom']['candidates'][1]['dbid'] == 'dbid0'
    assert classes['econom']['candidates'][2]['dbid'] == 'dbid2'

    assert len(classes['vip']['candidates']) == 1
    assert classes['vip']['candidates'][0]['dbid'] == 'dbid2'


@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_eta_bad_lookup_ordering_bulk(
        taxi_driver_eta, mockserver, mock_umlaas_dispatch_unavailable,
):
    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _ordering_bulk(request):
        data = {
            'responses': [
                {
                    'candidates': [
                        {'id': 'dbid0_uuid0', 'score': 4},
                        {'id': 'dbid1_uuid1', 'score': 5},
                    ],
                },
            ],
        }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        data = {'candidates': [CANDIDATE_TWO, CANDIDATE_ONE, CANDIDATE_ZERO]}
        return mockserver.make_response(json=data, status=200)

    response = await taxi_driver_eta.post(URL, json=SEARCH_PARAMS)
    assert response.status_code == 200
    answer = response.json()
    classes = answer['classes']
    assert len(classes['comfort']['candidates']) == 2
    assert classes['comfort']['candidates'][0]['dbid'] == 'dbid0'
    assert classes['comfort']['candidates'][1]['dbid'] == 'dbid1'

    assert len(classes['econom']['candidates']) == 3
    assert classes['econom']['candidates'][0]['dbid'] == 'dbid0'
    assert classes['econom']['candidates'][1]['dbid'] == 'dbid1'
    assert classes['econom']['candidates'][2]['dbid'] == 'dbid2'

    assert len(classes['vip']['candidates']) == 1
    assert classes['vip']['candidates'][0]['dbid'] == 'dbid2'


@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_eta_pa_auth_context(
        taxi_driver_eta, mockserver, mock_umlaas_dispatch_unavailable,
):
    def _get_user_phone_id(request_json):
        order = request_json.get('order')
        assert order
        user_phone_id = order.get('user_phone_id')
        assert user_phone_id

        return user_phone_id

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _ordering(request):
        assert (
            _get_user_phone_id(request.json['requests'][0]['search'])
            == 'phone_id1'
        )
        data = {
            'responses': [{'candidates': [{'id': 'dbid1_uuid1', 'score': 1}]}],
        }
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        assert _get_user_phone_id(request.json) == 'phone_id1'
        data = {'candidates': [CANDIDATE_ONE]}
        return mockserver.make_response(json=data, status=200)

    response = await taxi_driver_eta.post(
        URL, headers={'X-YaTaxi-PhoneId': 'phone_id1'}, json=SEARCH_PARAMS,
    )

    assert response.status_code == 200
    assert _ordering.has_calls
    assert _search.has_calls


@pytest.mark.dispatch_settings(settings=dispatch_settings.DISPATCH_SETTINGS)
async def test_scoring_bulk(
        taxi_driver_eta,
        mockserver,
        load_json,
        testpoint,
        mock_umlaas_dispatch_unavailable,
):
    @testpoint('ordering-bulk-response')
    def _ordering_response(data):
        assert data == {
            'responses': [
                {
                    'candidates': [
                        {'id': 'c2', 'penalty': 0, 'score': 1},
                        {'id': 'c4', 'penalty': 0, 'score': 3},
                    ],
                    'source': 'scoring',
                },
                {
                    'candidates': [
                        {'id': 'c1', 'penalty': 0, 'score': 0},
                        {'id': 'c2', 'penalty': 0, 'score': 1},
                        {'id': 'c3', 'penalty': 0, 'score': 2},
                    ],
                    'source': 'scoring',
                },
            ],
        }

    @testpoint('ordering-bulk-request')
    def _ordering_request(data):
        request = {'intent': 'eta', 'requests': []}
        request['requests'].append(load_json('reposition_request.json'))
        request['requests'].append(load_json('approximate_request.json'))
        return request

    @mockserver.json_handler('/candidates/order-multisearch')
    def _search(request):
        data = {'candidates': [CANDIDATE_FOUR, CANDIDATE_SEVEN]}
        return mockserver.make_response(json=data, status=200)

    @mockserver.json_handler('/driver_scoring/v2/score-candidates-bulk')
    def _driver_scoring(request):
        body = json.loads(request.get_data())
        assert body['intent'] == 'eta'
        requests = body['requests']
        response_json = {'responses': []}

        for req in requests:
            candidates = req['candidates']
            candidates.sort(key=lambda x: x['id'])
            response = []
            for i, candidate in enumerate(candidates):
                metadata = candidate.get('metadata', {})
                if not metadata.get('reposition_check_required', False):
                    response.append(
                        {'id': candidate['id'], 'score': i, 'penalty': 0},
                    )
            response_json['responses'].append({'candidates': response})

        return mockserver.make_response(json=response_json, status=200)

    await taxi_driver_eta.post(
        URL, headers={'X-YaTaxi-PhoneId': 'phone_id1'}, json=SEARCH_PARAMS,
    )
    assert _driver_scoring.has_calls
