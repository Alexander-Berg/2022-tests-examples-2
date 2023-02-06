import copy
import datetime
import typing as tp

import pytest

# pylint: disable=import-only-modules
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import staff
from tests_effrat_employees import time_utils
from tests_effrat_employees import utils


_EMPLOYEES = [
    employee.create_employee(
        0,
        departments=[
            department.generate_department(0, 'Subdivision'),
            department.generate_department(0, 'Division'),
        ],
    ),
    employee.create_employee(
        1,
        departments=[
            department.generate_department(1, 'Subdivision'),
            department.generate_department(0, 'Division'),
        ],
    ),
    employee.create_employee(
        2,
        departments=[
            department.generate_department(2, 'Subdivision'),
            department.generate_department(1, 'Division'),
        ],
    ),
    employee.create_employee(
        3,
        departments=[
            department.generate_department(2, 'Subdivision'),
            department.generate_department(1, 'Division'),
        ],
    ),
]

_DEPARTMENTS = [
    department.StaffDepartment(
        department.generate_department(0, 'Division'), 'taxi',
    ),
    department.StaffDepartment(
        department.generate_department(1, 'Subdivision'), 'taxi',
    ),
    department.StaffDepartment(
        department.generate_department(2, 'Subdivision'), 'taxi',
    ),
]


def _default_handler(request):
    staff_request = staff.StaffDepartmentsQuery(request.query['_query'])
    response_employees = filter(
        lambda emp: staff_request.departments[0]
        in map(lambda x: x.external_id, emp.departments),
        _EMPLOYEES,
    )
    return {
        'page': 1,
        'links': {},
        'limit': 100,
        'result': [
            emp.to_staff_response(time_utils.NOW) for emp in response_employees
        ],
    }


@pytest.fixture(name='init_departments')
async def _init_departments(
        taxi_effrat_employees,
        taxi_config,
        mockserver,
        mocked_time,
        department_context,
        mock_department,
        testpoint,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def handler(request):
        return _default_handler(request)

    department_context.set_data(_DEPARTMENTS)
    department.set_staff_departments_config(taxi_config, _DEPARTMENTS)
    await taxi_effrat_employees.invalidate_caches()

    for _ in range(len(_DEPARTMENTS)):
        await employee_fetcher_activate_task()
        request = (await handler.wait_call())['request']
        query = staff.StaffDepartmentsQuery(request.query['_query'])
        assert query.modified_at == time_utils.EPOCH


async def _update_departments(
        new_departments: tp.List[department.StaffDepartment],
        taxi_effrat_employees,
        taxi_config,
        mocked_time,
):
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    department.set_staff_departments_config(taxi_config, new_departments)
    await taxi_effrat_employees.invalidate_caches()


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_add_departments(
        taxi_effrat_employees,
        taxi_config,
        mocked_time,
        init_departments,
        generated_uuids,
):
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 100},
        headers={'Content-Type': 'application/json'},
    )
    utils.verify_response(response, _EMPLOYEES, generated_uuids)


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_remove_departments(
        taxi_effrat_employees,
        taxi_config,
        mocked_time,
        init_departments,
        generated_uuids,
):
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 100},
        headers={'Content-Type': 'application/json'},
    )
    cursor = utils.verify_response(response, _EMPLOYEES, generated_uuids)

    local_copy = copy.deepcopy(_DEPARTMENTS)
    local_copy.remove(_DEPARTMENTS[0])
    await _update_departments(
        local_copy, taxi_effrat_employees, taxi_config, mocked_time,
    )

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 100, 'cursor': cursor},
        headers={'Content-Type': 'application/json'},
    )

    fired_employee = copy.copy(_EMPLOYEES[0])
    fired_employee.employment_status = 'fired'
    utils.verify_response(response, [fired_employee], generated_uuids)


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_change_departments(
        taxi_effrat_employees,
        taxi_config,
        mocked_time,
        init_departments,
        generated_uuids,
):
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 100},
        headers={'Content-Type': 'application/json'},
    )
    cursor = utils.verify_response(response, _EMPLOYEES, generated_uuids)

    local_copy = copy.deepcopy(_DEPARTMENTS)
    local_copy[2].domain = 'lavka'
    await _update_departments(
        local_copy, taxi_effrat_employees, taxi_config, mocked_time,
    )

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 100, 'cursor': cursor},
        headers={'Content-Type': 'application/json'},
    )

    changed_employees = copy.copy(_EMPLOYEES[2:])
    for emp in changed_employees:
        emp.domain = 'lavka'
    utils.verify_response(response, changed_employees, generated_uuids)


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_get_name(
        taxi_effrat_employees,
        taxi_config,
        mockserver,
        mocked_time,
        pgsql,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
        generated_uuids,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(request):
        return _default_handler(request)

    department_context.set_data(_DEPARTMENTS)

    department.set_staff_departments_config(taxi_config, _DEPARTMENTS)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()
    db = pgsql['effrat_employees']
    cursor = db.cursor()
    cursor.execute('select name from effrat_employees.department')
    rows = cursor.fetchall()
    rows = sorted(rows, key=lambda x: x[0])
    expected_res = [
        'Division 0',
        'Subdivision 0',
        'Subdivision 1',
        'Subdivision 2',
    ]
    for (response_department, should_be_department) in zip(rows, expected_res):
        assert response_department[0] == should_be_department


@pytest.mark.now(time_utils.NOW.isoformat('T'))
@pytest.mark.parametrize(
    'organization',
    (
        {'id': None},
        {
            'id': 1,
            'name': 'nalkj',
            '_meta': {'modified_at': time_utils.NOW.isoformat('T')},
            'created_at': time_utils.NOW.isoformat('T'),
        },
        {
            'id': 2,
            'name': 'qernbp',
            '_meta': {'modified_at': time_utils.NOW.isoformat('T')},
            'created_at': time_utils.NOW.isoformat('T'),
            'country_code': 'ASD',
        },
        {
            'id': 2,
            'name': None,
            '_meta': None,
            'created_at': None,
            'country_code': None,
        },
    ),
)
async def test_official_organization(
        taxi_effrat_employees,
        taxi_config,
        mockserver,
        mocked_time,
        pgsql,
        department_context,
        mock_department,
        organization,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(request):
        response = _default_handler(request)
        for res in response['result']:
            res['official']['organization'] = organization
        return response

    department_context.set_data(_DEPARTMENTS)

    department.set_staff_departments_config(taxi_config, _DEPARTMENTS)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()
    db = pgsql['effrat_employees']
    cursor = db.cursor()
    cursor.execute('select name from effrat_employees.department')
    rows = cursor.fetchall()
    rows = sorted(rows, key=lambda x: x[0])
    expected_res = [
        'Division 0',
        'Subdivision 0',
        'Subdivision 1',
        'Subdivision 2',
    ]
    for (response_department, should_be_department) in zip(rows, expected_res):
        assert response_department[0] == should_be_department
