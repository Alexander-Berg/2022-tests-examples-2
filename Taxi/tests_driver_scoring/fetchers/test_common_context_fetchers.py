import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='postprocessors.json')
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.now('2020-04-21T12:17:00.000+0000')
async def test_now_timestamp_s(taxi_driver_scoring, load_json):
    content = """
        if (common_context.now_timestamp_s === 1587471420.0) {
            return 50;
        }
        return 0;
    """
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/commit',
        headers={
            'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Id': '0',
        },
        json={
            'script_name': 'checker',
            'type': 'calculate',
            'content': content,
            'tests': [],
        },
    )
    assert response.status_code == 200
    await taxi_driver_scoring.invalidate_caches()

    request_body = load_json('request_body.json')
    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == {
        'responses': [
            {
                'search': {},
                'candidates': [{'id': 'dbid0_uuid0', 'score': 600.0}],
            },
        ],
    }
