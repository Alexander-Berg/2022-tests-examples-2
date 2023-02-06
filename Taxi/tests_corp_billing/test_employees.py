import dataclasses

import pytest


async def test_cannot_insert_without_client(
        load_json, request_create_employee,
):
    employees = load_json('employees_ya_taxi_team.json')
    response = await request_create_employee(employees[0])
    assert response.status_code == 400
    assert response.json()['code'] == 'CLIENT_NOT_FOUND'


async def test_same_update_ok(_fill_ya_team, request_update_employee):
    result = await _fill_ya_team()
    employee = result.employees['yataxi_team/dmkurilov']
    orig_revision = employee['revision']
    employee['revision'] -= 1

    # Document the same, return 200 even with old revision
    response = await request_update_employee(employee)
    assert response.status_code == 200
    assert response.json()['revision'] == orig_revision


async def test_old_revision_rejected(_fill_ya_team, request_update_employee):
    result = await _fill_ya_team()
    employee = result.employees['yataxi_team/dmkurilov']
    employee['revision'] -= 1
    employee['all_services_suspended'] = True

    # Document the same, return 200 even with old revision
    response = await request_update_employee(employee)
    assert response.status_code == 409


async def test_repeated_service(_fill_ya_team, request_update_employee):
    result = await _fill_ya_team()
    employee = result.employees['yataxi_team/dmkurilov']
    employee['services'].append(employee['services'][0])

    response = await request_update_employee(employee)
    assert response.status_code == 400
    assert response.json()['code'] == 'SERVICES_REPEATED'


async def test_deleted_service(_fill_ya_team, request_update_employee):
    result = await _fill_ya_team()
    employee = result.employees['yataxi_team/dmkurilov']
    del employee['services'][0]

    response = await request_update_employee(employee)
    assert response.status_code == 400
    assert response.json()['code'] == 'CANNOT_DISABLE_SERVICE'


async def test_missing_uid_and_phone_is_ok(
        _fill_ya_team, request_update_employee,
):
    result = await _fill_ya_team()
    employee = result.employees['yataxi_team/rkarlash']
    assert employee.get('passport_uid') is None
    assert employee.get('personal_phone_id') is None


async def test_can_add_service(_fill_ya_team, request_update_employee):
    result = await _fill_ya_team()
    employee = result.employees['yataxi_team/dmkurilov']
    employee['services'].append({'type': 'eats/kaz', 'suspended': False})

    response = await request_update_employee(employee)
    assert response.status_code == 200
    assert len(response.json()['services']) == 2
    assert not response.json()['service_limits']


@pytest.fixture
def _fill_ya_team(
        request_create_employee,
        request_update_employee,
        request_find_employees,
        add_client_with_services,
        load_json,
):
    async def _wrapper():
        client = load_json('client_with_services_ya_taxi_team.json')
        await add_client_with_services(client)

        employees_dict = {}
        employees = load_json('employees_ya_taxi_team.json')
        for obj in employees:
            response = await request_create_employee(obj)
            assert response.status_code == 200
            obj['revision'] = response.json()['revision']
            obj['service_limits'] = response.json()['service_limits']
            response = await request_update_employee(obj)
            assert response.status_code == 200

            employee = response.json()
            employees_dict[employee['external_ref']] = employee

        @dataclasses.dataclass
        class Result:
            client: dict
            employees: dict

        return Result(client, employees_dict)

    return _wrapper
