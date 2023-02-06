import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.parametrize(
    'testcase_name',
    [
        'simple_filter',
        'simple_calculate',
        'simple_postprocess_results',
        'postprocess_results_change_score',
        'exceptions',
        'postprocess_results_with_trace',
        'additional_properties',
    ],
)
async def test_ok(taxi_driver_scoring, testcase_name, load_json, load):
    body = load_json(f'ok/{testcase_name}_tests.json')
    body['content'] = load(f'ok/{testcase_name}_content.js')

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-commit',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 200
    assert response.json()['data'] == body


@pytest.mark.parametrize(
    'testcase_name',
    [
        'fail/simple_filter_wrong_answer',
        'fail/simple_calculate_wrong_answer',
        'fail/simple_postprocess_results_wrong_answer',
        'fail/no_exception',
        'fail/unexpected_exception',
        'timeout/simple_test',
        'incorrect_format/base',
        'incorrect_format/bulk_size',
        'incorrect_format/no_output',
        'incorrect_format/exception_and_trace',
        'incorrect_format/incorrect_output',
        'compilation_failed/compilation_failed',
    ],
)
async def test_fails(taxi_driver_scoring, testcase_name, load_json, load):
    body = load_json(f'{testcase_name}_tests.json')
    body['content'] = load(f'{testcase_name}_content.js')

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-commit',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 400
    assert response.json() == load_json(f'{testcase_name}_response.json')


async def test_v2_admin_scripts_commit_maintainers(taxi_driver_scoring):
    body = {
        'script_name': 'some_name',
        'content': 'return 0;',
        'type': 'calculate',
        'tests': [],
        'maintainers': ['fourthrome', 'dulumzhiev', 'alex-tsarkov'],
        'config_name': 'some_name_config',
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-commit',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 200
    resp_body = response.json()
    assert resp_body['data'] == body


async def test_v2_admin_scripts_commit_empty_maintainers_fail(
        taxi_driver_scoring,
):
    body = {
        'script_name': 'some_name',
        'content': 'return 0;',
        'type': 'calculate',
        'tests': [],
        'maintainers': [],
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-commit',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 400


async def test_v2_admin_scripts_commit_config_name_fail(taxi_driver_scoring):
    body = {
        'script_name': 'some_name',
        'content': 'return 0;',
        'type': 'calculate',
        'tests': [],
        'config_name': '',
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-commit',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 400
