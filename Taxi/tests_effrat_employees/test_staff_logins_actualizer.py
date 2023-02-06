import copy
import datetime

import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import employee
from tests_effrat_employees import staff
from tests_effrat_employees import time_utils
from tests_effrat_employees import utils

_EMPLOYEES = [
    employee.create_employee(0, login='login0', domain='taxi'),
    employee.create_employee(1, login='login1', domain='eats'),
    employee.create_employee(2, login='login2', domain='lavka'),
]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_config_update(
        taxi_effrat_employees,
        taxi_config,
        mockserver,
        mocked_time,
        generated_uuids,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(request):
        staff_request = staff.StaffLoginsQuery(request.query['_query'])
        response_employees = filter(
            lambda emp: emp.login in staff_request.logins, _EMPLOYEES,
        )
        return {
            'page': 1,
            'links': {},
            'limit': 100,
            'result': [
                emp.to_staff_response(time_utils.NOW)
                for emp in response_employees
            ],
        }

    staff_logins = [
        employee.StaffEmployee(employee.generate_login(0), 'taxi'),
        employee.StaffEmployee(employee.generate_login(1), 'eats'),
        employee.StaffEmployee(employee.generate_login(2), 'lavka'),
    ]
    employee.set_staff_logins_config(taxi_config, staff_logins)
    await taxi_effrat_employees.invalidate_caches()
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 100},
        headers={'Content-Type': 'application/json'},
    )

    cursor = utils.verify_response(response, _EMPLOYEES, generated_uuids)

    del staff_logins[0]
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    employee.set_staff_logins_config(taxi_config, staff_logins)
    await taxi_effrat_employees.invalidate_caches()
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 100, 'cursor': cursor},
        headers={'Content-Type': 'application/json'},
    )

    fired_employee = copy.copy(_EMPLOYEES[0])
    fired_employee.employment_status = 'fired'
    utils.verify_response(response, [fired_employee], generated_uuids)
