import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'silver'),  # bonus: 10
        ('dbid_uuid', 'dbid0_uuid0', 'private_car'),  # bonus: 20
    ],
)
async def test_limit_cpp_bonuses(taxi_driver_scoring):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
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
        'v2/score-candidates', headers=headers, json=body,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 224.0},  # 124 - max(-100, -600)
            {'id': 'dbid0_uuid0', 'score': 635.0},  # 650 - min(15, 10+20)
        ],
    }


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'silver'),
        ('dbid_uuid', 'dbid0_uuid0', 'private_car'),
    ],
)
async def test_limit_js_bonuses(taxi_driver_scoring):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
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
        'v2/score-candidates', headers=headers, json=body,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 124.0},
            {'id': 'dbid0_uuid0', 'score': 500.0},  # 650 - min(150, 2*100)
        ],
    }


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='driver_scoring_mix_max_cap.json')
@pytest.mark.parametrize(
    'zone,expected',
    [
        (
            'lipetsk',
            {
                'dbid1_uuid1': 171.0,
                'dbid0_uuid0': 640.0,
            },  # 124 - max(-100, -47), 650 - min(15, 10)
        ),
        (
            'moscow',
            {
                'dbid1_uuid1': 164,
                'dbid0_uuid0': 635,
            },  # 124 - max(-100, -40), 650 - min(15, 20)
        ),
        (
            'spb',
            {
                'dbid1_uuid1': 174,
                'dbid0_uuid0': 635,
            },  # 124 - max(-100, -50), 650 - min(15, nullopt)
        ),
    ],
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'silver'),  # bonus: 10
        ('dbid_uuid', 'dbid0_uuid0', 'private_car'),  # bonus: 20
    ],
)
async def test_limit_caps(taxi_driver_scoring, zone, expected):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
    body = {
        'request': {
            'search': {
                'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                'order': {
                    'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                    'nearest_zone': zone,
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
        'v2/score-candidates', headers=headers, json=body,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': expected['dbid1_uuid1']},
            {'id': 'dbid0_uuid0', 'score': expected['dbid0_uuid0']},
        ],
    }
