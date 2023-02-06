# pylint: disable=C5521
import pytest


@pytest.mark.pgsql('reposition', files=['mode_home.sql', 'sessions.sql'])
@pytest.mark.parametrize('airport_queue_id', ['q0', 'q1', 'q2', 'q3'])
async def test_make_offer(taxi_reposition_api, load_json, airport_queue_id):
    response = await taxi_reposition_api.get(
        '/v1/service/airport_queue/get_drivers_en_route',
        params={'airport_queue_id': airport_queue_id},
    )

    assert response.status_code == 200

    responses = load_json('responses.json')
    assert response.json() == responses[airport_queue_id]
