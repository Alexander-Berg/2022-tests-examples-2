import datetime

import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
@pytest.mark.now('2020-02-07T13:34:48Z')
async def test_activate_script(taxi_driver_scoring, pgsql):
    cursor = pgsql['driver_scoring'].conn.cursor()

    body = {
        'id': 2,
        'revision': 1,
        'script_name': 'bonus_1',
        'type': 'calculate',
    }
    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 202
    resp_body = response.json()
    assert resp_body['active_script'] == body

    cursor.execute('SELECT * FROM scripts.active_scripts')

    now = datetime.datetime(2020, 2, 7, 13, 34, 48)
    assert list(cursor) == [(1, now, 'bonus_1', 'calculate', 2)]


@pytest.mark.pgsql(
    'driver_scoring',
    files=['sample_js_scripts.sql', 'sample_active_scripts2.sql'],
)
@pytest.mark.now('2020-02-07T13:34:48Z')
async def test_activate_script_upd(taxi_driver_scoring, pgsql):
    cursor = pgsql['driver_scoring'].conn.cursor()

    body = {
        'id': 1,
        'revision': 0,
        'script_name': 'bonus_1',
        'type': 'calculate',
        'last_active_id': 2,
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/activate',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )

    assert response.status_code == 202

    cursor.execute('SELECT * FROM scripts.active_scripts')

    now = datetime.datetime(2020, 2, 7, 13, 34, 48)
    assert list(cursor) == [(1, now, 'bonus_1', 'calculate', 1)]


@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
async def test_activate_script_404(taxi_driver_scoring):
    body = {
        'id': 2,
        'revision': 1,
        'script_name': 'bonus_1',
        'type': 'calculate',
    }

    async def check():
        response = await taxi_driver_scoring.post(
            'v2/admin/scripts/activate',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=body,
        )

        assert response.status_code == 404

        resp_body = response.json()

        args = [
            body['id'],
            body['script_name'],
            body['type'],
            body['revision'],
        ]
        exp_resp = 'Script not found: script with '
        exp_resp += 'id={} name={} type={} revision={} does not exist'
        exp_resp = exp_resp.format(*args)

        assert resp_body['message'] == exp_resp
        assert resp_body['status'] == 404

    body['id'] = 3
    await check()
    body['id'] = 2

    body['revision'] = 0
    await check()
    body['revision'] = 1

    body['script_name'] = 'bonus_2'
    await check()
    body['script_name'] = 'bonus_1'

    body['type'] = 'filter'
    await check()
    body['type'] = 'calculate'


@pytest.mark.pgsql(
    'driver_scoring',
    files=['sample_js_scripts.sql', 'sample_active_scripts1.sql'],
)
async def test_activate_script_409(taxi_driver_scoring, pgsql):
    body = {
        'id': 2,
        'revision': 1,
        'script_name': 'bonus_1',
        'type': 'calculate',
    }
    cursor = pgsql['driver_scoring'].conn.cursor()

    async def check():
        response = await taxi_driver_scoring.post(
            'v2/admin/scripts/activate',
            headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
            json=body,
        )

        cursor.execute('select * from scripts.active_scripts')

        assert response.status_code == 409

        resp_body = response.json()

        exp_message = 'Script activation conflict: '
        exp_message += 'got no last_active_id, but current active id=1'
        if 'last_active_id' in body:
            exp_message = 'Script activation conflict: '
            exp_message += 'got last_active_id=3, but current active id=1'
        assert resp_body['message'] == exp_message
        assert resp_body['status'] == 409
        assert resp_body['active_script'] == {
            'script_name': 'bonus_1',
            'id': 1,
            'revision': 0,
            'type': 'calculate',
        }

    await check()

    body['last_active_id'] = 3
    await check()


@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
async def test_activate_script_400_validation_fail(taxi_driver_scoring, pgsql):
    body = {
        'id': 3,
        'revision': 2,
        'script_name': 'bonus_1',
        'type': 'calculate',
    }

    response = await taxi_driver_scoring.post(
        'v2/admin/scripts/activate',
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
