import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets

HEADERS = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
BODY = {
    'request': {
        'search': {
            'order_id': '16e83c16beb74880b819d2a7b1c06d93',
            'order': {
                'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                'nearest_zone': 'lipetsk',
            },
            'allowed_classes': ['econom'],
        },
        'candidates': [
            {
                'id': 'dbid0_uuid0',
                'route_info': {
                    'time': 400,
                    'distance': 1450,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom', 'business'],
            },
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 800,
                    'distance': 3200,
                    'approximate': True,
                },
                'position': [39.609112, 52.570000],
                'classes': ['econom', 'business'],
            },
        ],
    },
    'intent': 'dispatch-buffer',
}


@pytest.mark.experiments3(filename='exclude.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_exclude(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADERS, json=BODY,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 500.0},  # 800 - 100 - 200
        ],
    }


@pytest.mark.experiments3(filename='pessimize.json')
@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_pessimize_with_postprocessor(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADERS, json=BODY,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 500.0},
            {
                'id': 'dbid0_uuid0',
                'score': 501.0,
            },  # It is pessimized so should have bigger value
        ],
    }


@pytest.mark.experiments3(filename='pessimize.json')
@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_postprocessor_no_pessimized(taxi_driver_scoring):
    body = {
        'request': {
            'search': {
                'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                'order': {
                    'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                    'nearest_zone': 'lipetsk',
                },
                'allowed_classes': ['econom'],
            },
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 400,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                },
                {
                    'id': 'dbid2_uuid2',
                    'route_info': {
                        'time': 800,
                        'distance': 3200,
                        'approximate': True,
                    },
                    'position': [39.609112, 52.570000],
                    'classes': ['econom', 'business'],
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADERS, json=body,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid0_uuid0', 'score': 100.0},
            {'id': 'dbid2_uuid2', 'score': 500.0},
        ],
    }


@pytest.mark.experiments3(filename='pessimize.json')
@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_postprocessor_all_pessimized(taxi_driver_scoring):
    body = {
        'request': {
            'search': {
                'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                'order': {
                    'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                    'nearest_zone': 'lipetsk',
                },
                'allowed_classes': ['econom'],
            },
            'candidates': [
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 400,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                },
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 800,
                        'distance': 3200,
                        'approximate': True,
                    },
                    'position': [39.609112, 52.570000],
                    'classes': ['econom', 'business'],
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADERS, json=body,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 100.0},
            {'id': 'dbid1_uuid1', 'score': 500.0},
        ],
    }
