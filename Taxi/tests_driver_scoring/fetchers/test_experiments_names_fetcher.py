import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


BODY = {
    'requests': [
        {
            'search': {
                'order_id': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
                'order': {
                    'request': {
                        'source': {'geopoint': [39.52449, 52.69810]},
                        'corp': {
                            'client_id': '89c43fa2faab4518849ae29fdc25926d',
                        },
                    },
                    'user_agent': 'ru.yandex.taxi.inhouse/3.73.5291 (iPhone; iPhone8,2; iOS 10.0.1; Darwin)',  # noqa: E501
                },
                'allowed_classes': ['econom'],
                'metadata': {
                    'experiments': [
                        {
                            'name': 'metadata_test_experiment',
                            'version': 0,
                            'position': 0,
                            'value': {},
                        },
                    ],
                },
            },
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 0,
                        'distance': 5,
                        'approximate': False,
                    },
                    'unique_driver_id': 'udid0',
                    'position': [39.52449, 52.69810],
                    'classes': ['econom'],
                },
            ],
        },
        {
            'search': {
                'order_id': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb',
                'order': {
                    'request': {'source': {'geopoint': [39.52449, 52.69810]}},
                },
                'allowed_classes': ['econom'],
            },
            'candidates': [
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 0,
                        'distance': 5,
                        'approximate': False,
                    },
                    'unique_driver_id': 'udid0',
                    'position': [39.52449, 52.69810],
                    'classes': ['econom'],
                },
            ],
        },
    ],
    'intent': 'dispatch-buffer',
}


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='experiments3_dispatch_settings.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_fetcher(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200

    resp_json = response.json()['responses']

    # Check experiment taken by order_id kwarg
    assert resp_json[0]['candidates'] == [
        {'id': 'dbid0_uuid0', 'score': -110.0},
    ]

    # Check default experiment is taken
    assert resp_json[1]['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': -10.0},
    ]
