import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.parametrize(
    'body, expected_status_code',
    [
        (
            {
                'id': 6,
                'script_name': 'script_1',
                'type': 'postprocess_results',
                'revision': 0,
            },
            200,
        ),
        (
            {
                'id': 3,
                'script_name': 'bonus_1',
                'type': 'calculate',
                'revision': 2,
                'last_active_id': 2,
            },
            200,
        ),
    ],
)
@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
async def test_check_activate(taxi_driver_scoring, body, expected_status_code):
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        resp_body = response.json()
        assert resp_body['data'] == body


@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
async def test_check_activate_conflict(taxi_driver_scoring):
    body = {
        'id': 3,
        'script_name': 'bonus_1',
        'type': 'calculate',
        'revision': 2,
    }

    async def check():
        response = await taxi_driver_scoring.post(
            'v2/admin/scripts/check-activate',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=body,
        )

        assert response.status_code == 409

    await check()

    body['last_active_id'] = 1
    await check()


@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
async def test_check_activate_not_found(taxi_driver_scoring):
    body = {
        'id': 4,
        'script_name': 'bonus_1',
        'type': 'calculate',
        'revision': 2,
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 404

    resp_body = response.json()
    assert resp_body['status'] == 404

    args = [body['id'], body['script_name'], body['type'], body['revision']]
    exp_resp = 'Script not found: script with '
    exp_resp += 'id={} name={} type={} revision={} does not exist'
    exp_resp = exp_resp.format(*args)

    assert resp_body['message'] == exp_resp


@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
async def test_check_activate_script_400_validation_fail(
        taxi_driver_scoring, pgsql,
):
    body = {
        'id': 5,
        'revision': 1,
        'script_name': 'bonus_2',
        'type': 'calculate',
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/check-activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 400

    resp_body = response.json()
    assert resp_body['message'].startswith(
        'Script validation failed: JS compile error',
    )
    assert resp_body['code_point'] == {
        'column_begin': 5,
        'column_end': 9,
        'line': 1,
    }
    assert resp_body['status'] == 400
