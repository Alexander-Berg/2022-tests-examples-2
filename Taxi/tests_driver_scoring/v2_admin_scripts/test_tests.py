import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.now('2020-02-02T02:02:02Z')
async def test_simple_calculate(taxi_driver_scoring):
    tests = [
        {
            'test_input': {
                'common_context': {},
                'order_context': {},
                'candidate_context': {},
            },
            'test_output': {'return_value': 1},
            'name': 'test_1',
        },
    ]
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/commit',
        headers={
            'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Id': '0',
        },
        json={
            'script_name': 'bonus_1',
            'type': 'calculate',
            'content': 'return 1;',
            'tests': tests,
        },
    )
    assert response.status_code == 200
    response = await taxi_driver_scoring.get(
        'v2/admin/scripts/tests?id=1',
        headers={
            'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Id': '0',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'tests': tests}


@pytest.mark.now('2020-02-02T02:02:02Z')
async def test_simple_filter(taxi_driver_scoring):
    tests = [
        {
            'test_input': {
                'common_context': {},
                'order_context': {},
                'candidate_context': {},
            },
            'test_output': {'return_value': False},
            'name': 'test_1',
        },
    ]
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/commit',
        headers={
            'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Id': '0',
        },
        json={
            'script_name': 'filter_1',
            'type': 'filter',
            'content': 'return false;',
            'tests': tests,
        },
    )
    assert response.status_code == 200

    response = await taxi_driver_scoring.get(
        'v2/admin/scripts/tests?id=1',
        headers={
            'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Id': '0',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'tests': tests}


@pytest.mark.now('2020-02-02T02:02:02Z')
async def test_simple_postprocess_results(taxi_driver_scoring):
    tests = [
        {
            'test_input': {
                'common_context': {},
                'order_contexts': [{}],
                'scoring_results': {},
            },
            'test_output': {'scoring_results': {}},
            'name': 'test_1',
        },
    ]
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/commit',
        headers={
            'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Id': '0',
        },
        json={
            'script_name': 'postprocess_results_1',
            'type': 'postprocess_results',
            'content': '',
            'tests': tests,
        },
    )
    assert response.status_code == 200

    response = await taxi_driver_scoring.get(
        'v2/admin/scripts/tests?id=1',
        headers={
            'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET,
            'X-YaTaxi-Draft-Id': '0',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'tests': tests}
