import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.experiments3(
    filename='driver_scoring_candidate_logic_config.json',
)
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_basic(taxi_driver_scoring, load_json):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=load_json('request_body.json'),
    )
    assert response.status_code == 200

    resp_json = response.json()['responses']

    assert resp_json[0]['candidates'] == [
        {'id': 'dbid0_uuid0', 'score': 600.0},
    ]
