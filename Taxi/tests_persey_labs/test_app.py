import copy

import pytest


async def add_state(taxi_persey_labs, state, headers):
    request = {'new_state': state}
    response = await taxi_persey_labs.post(
        'app/v1/employee/state', request, headers=headers,
    )
    assert response.status_code == 200


async def check_state(taxi_persey_labs, state, headers):
    response = await taxi_persey_labs.get(
        'app/v1/employee/state?date=2020-10-10', headers=headers,
    )
    assert response.status_code == 200, response.json()
    assert response.json() == {'employee_state': state}


@pytest.mark.now('2020-10-10 10:00:00 UTC')
@pytest.mark.servicetest
async def test_app_employee_state(
        taxi_persey_labs, fill_labs, load_json, pgsql,
):
    headers = {'X-Yandex-Login': 'login_0'}

    response = await taxi_persey_labs.get(
        'app/v1/employee/state?date=2020-10-10', headers=headers,
    )
    assert response.status_code == 404, response.json()
    assert response.json() == {
        'code': 'not_found',
        'message': 'Employee with such login doesn\'t exist',
    }

    request = {'new_state': 'start_shift'}
    response = await taxi_persey_labs.post(
        'app/v1/employee/state', request, headers=headers,
    )
    assert response.status_code == 404, response.json()
    assert response.json() == {
        'code': 'not_found',
        'message': 'Employee with such login doesn\'t exist',
    }

    lab_entities = load_json('labs.json')
    fill_labs.load_lab_entities(copy.deepcopy(lab_entities))
    fill_labs.load_employees('my_lab_id_1', load_json('employees.json'))

    await check_state(taxi_persey_labs, 'inactive', headers)
    await add_state(taxi_persey_labs, 'start_shift', headers)
    await check_state(taxi_persey_labs, 'start_shift', headers)
    await add_state(taxi_persey_labs, 'completed', headers)
    await check_state(taxi_persey_labs, 'completed', headers)
    await add_state(taxi_persey_labs, 'finish_shift', headers)
    await check_state(taxi_persey_labs, 'finish_shift', headers)
