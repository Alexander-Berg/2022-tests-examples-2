import typing as tp

import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils


def _default_args(index: int) -> tp.Dict:
    return {
        'full_name': f'surname{index} firstname{index} fathername{index}',
        'email_pd_id': None,
        'departments': [department.generate_departments(index)[0]],
    }


_CC_EMPLOYEES = [
    employee.create_employee(i, **_default_args(i)) for i in range(3, 6)
]

_STAFF_EMPLOYEES = [
    employee.create_employee(i, departments=department.generate_departments(0))
    for i in range(3)
]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_get(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        synched_gen_staff_dpts_config,
):
    await synched_gen_staff_dpts_config(taxi_config, 1)

    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _operators_list_handler(_):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 5,
                'operators': [
                    emp.to_callcenter_response() for emp in _CC_EMPLOYEES
                ],
            },
        )

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _persons_handler(_):
        return {
            'page': 1,
            'links': {},
            'limit': 1,
            'result': [
                emp.to_staff_response(time_utils.NOW)
                for emp in _STAFF_EMPLOYEES
            ],
        }

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    response = await taxi_effrat_employees.get(
        '/internal/v1/departments?domain=taxi',
    )
    assert response.status_code == 200
    response = list(
        sorted(response.json()['departments'], key=lambda x: x['id']),
    )
    should_be = [
        department.generate_departments(i)[0] for i in range(3, 6)
    ] + department.generate_departments(0)
    should_be = [{'id': x.external_id, 'name': x.name} for x in should_be]
    should_be = list(sorted(should_be, key=lambda x: x['id']))
    assert should_be == response
