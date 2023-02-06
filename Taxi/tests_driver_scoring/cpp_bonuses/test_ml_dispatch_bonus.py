import json

import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


BODY = {
    'request': {
        'search': {
            'order_id': '16e83c16beb74880b819d2a7b1c06d93',
            'order': {
                'request': {
                    'source': {'geopoint': [39.60258, 52.569089]},
                    'surge_price': 5.0,
                },
            },
            'allowed_classes': ['econom'],
        },
        'candidates': [
            {
                'id': 'dbid0_uuid0',
                'route_info': {
                    'time': 650,
                    'distance': 1450,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom', 'business'],
            },
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 124,
                    'distance': 3200,
                    'approximate': False,
                },
                'position': [39.609112, 52.570000],
                'classes': ['econom', 'business'],
            },
        ],
    },
    'intent': 'dispatch-buffer',
}


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_bonus_for_ml(taxi_driver_scoring):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=headers, json=BODY,
    )
    assert response.status_code == 200
    response = response.json()
    assert response['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 137},
        {'id': 'dbid0_uuid0', 'score': 663},
    ]


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_empty_candidates_for_ml(taxi_driver_scoring, mockserver):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}

    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/candidates-bonuses',
    )
    def _bonuses(request):
        return {'responses': [{'candidates': []}]}

    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=headers, json=BODY,
    )

    assert response.status_code == 200
    response = response.json()
    assert response['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 124},
        {'id': 'dbid0_uuid0', 'score': 650},
    ]


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_ml_fallback(taxi_driver_scoring, statistics):
    statistics.fallbacks = [
        'handler.umlaas-dispatch.v1.candidates-bonuses-post.fallback',
    ]
    await taxi_driver_scoring.tests_control(invalidate_caches=True)

    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=headers, json=BODY,
    )
    assert response.status_code == 200
    response = response.json()
    assert response['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 124},
        {'id': 'dbid0_uuid0', 'score': 650},
    ]

    statistics.fallbacks = []
    await taxi_driver_scoring.tests_control(invalidate_caches=True)
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=headers, json=BODY,
    )
    assert response.status_code == 200
    response = response.json()
    assert response['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 137},
        {'id': 'dbid0_uuid0', 'score': 663},
    ]


BODY_WITH_NEGATIVE_TIME_DISTANCE = {
    'request': {
        'search': {
            'order_id': '16e83c16beb74880b819d2a7b1c06d93',
            'order': {
                'request': {
                    'source': {'geopoint': [39.60258, 52.569089]},
                    'surge_price': 5.0,
                },
            },
            'allowed_classes': ['econom'],
        },
        'candidates': [
            {
                'id': 'dbid0_uuid0',
                'route_info': {
                    'time': -1,
                    'distance': -2,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom', 'business'],
            },
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 124,
                    'distance': 3200,
                    'approximate': False,
                },
                'position': [39.609112, 52.570000],
                'classes': ['econom', 'business'],
            },
            {
                'id': 'dbid2_uuid2',
                'route_info': {
                    'time': -10,
                    'distance': 0,
                    'approximate': False,
                },
                'position': [39.609112, 52.570000],
                'classes': ['econom', 'business'],
            },
        ],
    },
    'intent': 'dispatch-buffer',
}


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_negative_values_for_ml(taxi_driver_scoring, mockserver):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}

    @mockserver.json_handler(
        '/umlaas-dispatch/umlaas-dispatch/v1/candidates-bonuses',
    )
    def _bonuses(request):
        body_unicode = request.get_data().decode('utf-8')
        body = json.loads(body_unicode)

        candidates = body['requests'][0]['candidates']
        route_info0 = candidates[0]['route_info']
        route_info1 = candidates[1]['route_info']
        route_info2 = candidates[2]['route_info']

        assert 'time' not in route_info0
        assert 'distance' not in route_info0

        assert route_info1['time'] == 124
        assert route_info1['distance'] == 3200

        assert 'time' not in route_info2
        assert route_info2['distance'] == 0

        return {'responses': [{'candidates': []}]}

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers=headers,
        json=BODY_WITH_NEGATIVE_TIME_DISTANCE,
    )

    assert response.status_code == 200
