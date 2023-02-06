import datetime

import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils


_NUMBER_OF_EMPLOYEES = 100
_LIMIT = 3


_EMPLOYEES = [
    employee.create_employee(
        i,
        departments=[
            department.generate_department(0, 'Subdivision'),
            department.generate_department(0, 'Division'),
        ],
    )
    for i in range(_NUMBER_OF_EMPLOYEES)
]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_big_update(
        taxi_effrat_employees,
        taxi_config,
        mockserver,
        mocked_time,
        department_context,
        mock_department,
):
    query_number = 0

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        nonlocal query_number
        emp_len = len(_EMPLOYEES)
        res = {
            'page': 1,
            'links': {},
            'limit': 1,
            'result': [
                x.to_staff_response(time_utils.NOW)
                for x in _EMPLOYEES[
                    emp_len
                    // 2
                    * query_number : emp_len
                    // 2
                    * (query_number + 1)
                ]
            ],
        }
        query_number += 1
        return res

    staff_departments = [
        department.StaffDepartment(
            department.generate_department(0, 'Division'), 'taxi',
        ),
    ]
    department_context.set_data(staff_departments)
    department.set_staff_departments_config(taxi_config, staff_departments)
    await taxi_effrat_employees.invalidate_caches()

    # all these updates have timestamp NOW, because time is fixed
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    # all these updates have timestamp NOW + 1 minute, because time is fixed
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    logins = set()
    cursor = None
    number_of_iterations = (_NUMBER_OF_EMPLOYEES + _LIMIT - 1) // _LIMIT
    for _ in range(number_of_iterations):
        response = await taxi_effrat_employees.post(
            '/internal/v1/employees/index',
            json={'limit': _LIMIT, 'cursor': cursor},
            headers={'Content-Type': 'application/json'},
        )
        response = response.json()
        assert len(response['employees']) <= _LIMIT
        for emp in response['employees']:
            logins.add(emp['login'])
        cursor = response['cursor']

    assert len(logins) == _NUMBER_OF_EMPLOYEES

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': _LIMIT, 'cursor': cursor},
        headers={'Content-Type': 'application/json'},
    )
    assert not response.json()['employees']
