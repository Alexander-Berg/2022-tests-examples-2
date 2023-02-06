import datetime

import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils

_EMPLOYEES = [
    employee.create_employee(
        0,
        departments=[
            department.generate_department(0, 'Subdivision'),
            department.generate_department(0, 'Division'),
        ],
        domain='lavka',
    ),
]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_config_update(
        taxi_effrat_employees,
        taxi_config,
        mockserver,
        mocked_time,
        pgsql,
        department_context,
        mock_department,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def handler(request):
        return {
            'page': 3,
            'links': {},
            'limit': 100,
            'result': [
                emp.to_staff_response(time_utils.NOW) for emp in _EMPLOYEES
            ],
        }

    staff_departments = [
        department.StaffDepartment(
            department.generate_department(0, 'Division'), 'lavka',
        ),
    ]
    department_context.set_data(staff_departments)
    department.set_staff_departments_config(taxi_config, staff_departments)

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    handler.next_call()

    staff_departments.append(
        department.StaffDepartment(
            department.generate_department(0, 'Division'), 'taxi',
        ),
    )
    department.set_staff_departments_config(taxi_config, staff_departments)
    _EMPLOYEES.append(
        employee.create_employee(
            0,
            departments=[
                department.generate_department(0, 'Subdivision'),
                department.generate_department(0, 'Division'),
            ],
            domain='taxi',
        ),
    )
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 10, 'cursor': time_utils.NOW.isoformat()},
    )
    assert response.status_code == 200
    response = response.json()['employees']
    for emp in response:
        assert emp['departments']
