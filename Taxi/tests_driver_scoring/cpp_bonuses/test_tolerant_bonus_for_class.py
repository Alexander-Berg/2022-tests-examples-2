import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.fixture(name='candidates', autouse=True)
def mock_candidates(mockserver):
    @mockserver.json_handler('/candidates/profiles')
    def _profiles(request):
        return {
            'drivers': [
                {
                    'uuid': 'uuid0',
                    'dbid': 'dbid0',
                    'position': [39.59568, 52.568001],
                    'classes': ['econom'],
                },
                {
                    'uuid': 'uuid1',
                    'dbid': 'dbid1',
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'comfortplus'],
                },
                {
                    'uuid': 'uuid2',
                    'dbid': 'dbid2',
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'comfortplus', 'business'],
                },
            ],
        }


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    BONUS_FOR_CLASS_MAX_SURGE=3.0,
    DISPATCH_CLASSES_ORDER=['econom', 'comfortplus', 'business'],
)
async def test_bonus_for_class(taxi_driver_scoring):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
    body = {
        'requests': [
            {
                'search': {
                    'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                    'order': {
                        'request': {
                            'source': {'geopoint': [39.60258, 52.569089]},
                        },
                        'nearest_zone': 'lipetsk',
                    },
                    'allowed_classes': ['econom', 'comfortplus'],
                },
                'candidates': [
                    {  # bonus: 0
                        'id': 'dbid0_uuid0',
                        'route_info': {
                            'time': 500,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [39.59568, 52.568001],
                        'classes': ['econom'],
                    },
                    {  # bonus: 10
                        'id': 'dbid1_uuid1',
                        'route_info': {
                            'time': 500,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [39.59568, 52.568001],
                        'classes': ['econom', 'comfortplus'],
                    },
                    {  # bonus: 20
                        'id': 'dbid2_uuid2',
                        'route_info': {
                            'time': 500,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [39.59568, 52.568001],
                        'classes': ['econom', 'comfortplus'],
                    },
                ],
            },
            {
                'search': {
                    'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                    'order': {
                        'request': {
                            'source': {'geopoint': [39.60258, 52.569089]},
                        },
                        'nearest_zone': 'lipetsk',
                    },
                    'allowed_classes': ['econom', 'comfortplus'],
                    'svs': [4.0],
                },
                'candidates': [
                    {  # bonus: 0
                        'id': 'dbid0_uuid0',
                        'route_info': {
                            'time': 500,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [39.59568, 52.568001],
                        'classes': ['econom'],
                    },
                    {  # bonus: 0
                        'id': 'dbid1_uuid1',
                        'route_info': {
                            'time': 400,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [39.59568, 52.568001],
                        'classes': ['econom', 'comfortplus'],
                    },
                    {  # bonus: 0
                        'id': 'dbid2_uuid2',
                        'route_info': {
                            'time': 300,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [39.59568, 52.568001],
                        'classes': ['econom', 'comfortplus'],
                    },
                ],
            },
        ],
        'intent': 'dispatch-buffer',
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk', headers=headers, json=body,
    )
    assert response.status_code == 200
    assert response.json()['responses'] == [
        {
            'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
            'candidates': [
                {'id': 'dbid2_uuid2', 'score': 480.0},
                {'id': 'dbid1_uuid1', 'score': 490.0},
                {'id': 'dbid0_uuid0', 'score': 500.0},
            ],
        },
        {
            'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
            'candidates': [
                {'id': 'dbid2_uuid2', 'score': 300.0},
                {'id': 'dbid1_uuid1', 'score': 400.0},
                {'id': 'dbid0_uuid0', 'score': 500.0},
            ],
        },
    ]
