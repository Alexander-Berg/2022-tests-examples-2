import json

import pytest


@pytest.mark.driver_experiments('old_experiment')
@pytest.mark.config(EXPERIMENTS_ENABLED=True)
def test_taximeter_driver_experiments(taxi_protocol, mockserver):
    res = {'called': False}

    @mockserver.json_handler('/experiments/match')
    def match(request):
        res['called'] = True
        assert json.loads(request.get_data()) == {
            'driver': {
                'driver_id': 'driver',
                'park': '999011',
                'taximeter_version': '1.2 (3)',
                'city': 'Moscow',
            },
            'labels': ['protocol', 'driver_experiments'],
        }
        return {'tags': ['new_experiment:tag1']}

    response = taxi_protocol.post(
        '/taximeter/driver-experiments',
        params={
            'driver_id': 'driver',
            'park_id': '999011',
            'taximeter_version': '1.2 (3)',
        },
    )

    assert not res['called']

    assert response.status_code == 200
    assert response.json() == {'experiments': ['old_experiment']}
