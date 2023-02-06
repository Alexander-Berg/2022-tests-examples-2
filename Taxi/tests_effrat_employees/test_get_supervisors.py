import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils


_EMPLOYEES = [
    employee.create_employee(0, supervisor=employee.create_supervisor(250)),
    employee.create_employee(1, supervisor=employee.create_supervisor(0)),
    employee.create_employee(2, supervisor=None),
    employee.create_employee(
        3, supervisor=employee.create_supervisor(100, name=None),
    ),
    # employee with id=1 should not be supervisor,
    # since he is a supervisor of the fired man
    employee.create_employee(
        4, employment_status='fired', supervisor=employee.create_supervisor(1),
    ),
    # employee with id=4 should not be supervisor,
    # since he is fired
    employee.create_employee(5, supervisor=employee.create_supervisor(4)),
]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_get(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
):
    department.gen_staff_departments_config(taxi_config, 1)

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return {
            'page': 1,
            'links': {},
            'limit': 1,
            'result': [
                emp.to_staff_response(time_utils.NOW) for emp in _EMPLOYEES
            ],
        }

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    response = await taxi_effrat_employees.get(
        '/admin/v1/supervisors?domain=taxi',
    )
    assert response.status_code == 200
    response = list(
        map(
            employee.supervisor_from_ee_response,
            sorted(response.json()['supervisors'], key=lambda x: x['login']),
        ),
    )
    should_be = [
        employee.create_supervisor(0),
        employee.create_supervisor(100, name=None),
        employee.create_supervisor(250),
    ]
    should_be = list(sorted(should_be, key=lambda x: x.login))
    assert should_be == response
