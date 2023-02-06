import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets

HEADERS = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
)
async def test_autoaccept_fetcher(taxi_driver_scoring, mockserver, load_json):
    expected_bonuses = {
        'order_id1': {'dbid0_uuid0': -100, 'dbid1_uuid1': 500},
        'order_id2': {'dbid2_uuid2': 500},
        'order_id3': {'dbid2_uuid2': -100},
    }

    @mockserver.json_handler('/autoaccept/v1/decide-autoaccept-bulk')
    def _decide_autoaccept(request):
        assert request.json == load_json('autoaccept_request.json')
        return {
            'orders': [
                {
                    'order_id': 'order_id1',
                    'candidates': [
                        {
                            'park_id': 'dbid0',
                            'driver_profile_id': 'uuid0',
                            'autoaccept': {
                                'enabled': (
                                    expected_bonuses['order_id1'][
                                        'dbid0_uuid0'
                                    ]
                                    == -100
                                ),
                            },
                        },
                        {
                            'park_id': 'dbid1',
                            'driver_profile_id': 'uuid1',
                            'autoaccept': {
                                'enabled': (
                                    expected_bonuses['order_id1'][
                                        'dbid1_uuid1'
                                    ]
                                    == -100
                                ),
                            },
                        },
                    ],
                },
                {
                    'order_id': 'order_id3',
                    'candidates': [
                        {
                            'park_id': 'dbid2',
                            'driver_profile_id': 'uuid2',
                            'autoaccept': {
                                'enabled': (
                                    expected_bonuses['order_id3'][
                                        'dbid2_uuid2'
                                    ]
                                    == -100
                                ),
                            },
                        },
                    ],
                },
            ],
        }

    body = load_json('request.json')

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk', headers=HEADERS, json=body,
    )
    assert response.status_code == 200

    for order in response.json()['responses']:
        for cand in order['candidates']:
            assert (
                expected_bonuses[order['search']['order_id']][cand['id']]
                == cand['score']
            )
