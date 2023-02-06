import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_white_label_bonus(taxi_driver_scoring):
    body = {
        'request': {
            'search': {
                'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                'order': {
                    'request': {
                        'source': {'geopoint': [39.52449, 52.69810]},
                        'white_label_requirements': {
                            'source_park_id': 'cheetah',
                            'dispatch_requirement': 'source_park_and_all',
                        },
                    },
                },
                'allowed_classes': ['econom'],
            },
            'candidates': [
                {
                    'id': 'cheetah_uuid0',
                    'route_info': {
                        'time': 650,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.52321, 52.69234],
                    'classes': ['econom', 'business'],
                },
                {
                    'id': 'dbid0_uuid1',
                    'route_info': {
                        'time': 124,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.51345, 52.69346],
                    'classes': ['econom', 'business'],
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert candidates == [
        {'id': 'cheetah_uuid0', 'score': 650.0},
        # pessimized with minimal delta = 1
        {'id': 'dbid0_uuid1', 'score': 651.0},
    ]
