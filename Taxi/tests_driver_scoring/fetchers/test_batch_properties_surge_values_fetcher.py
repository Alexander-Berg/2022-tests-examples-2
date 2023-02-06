import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='js_bonuses_for_values.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_bonuses_for_values.sql'])
async def test_driver_scoring_batch_properties_surge_exists(
        taxi_driver_scoring, load_json,
):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=load_json('request_body_with_pickup.json'),
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 24.0},
            {'id': 'dbid0_uuid0', 'score': 550.0},
        ],
    }
