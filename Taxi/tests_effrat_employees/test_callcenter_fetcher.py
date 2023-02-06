import datetime
from typing import Dict

import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import personal
from tests_effrat_employees import time_utils
from tests_effrat_employees import utils


def _default_args(index: int) -> Dict:
    return {
        'full_name': f'surname{index} firstname{index} fathername{index}',
        'email_pd_id': None,
        'departments': [department.generate_departments(index)[0]],
    }


_EMPLOYEES = [
    employee.create_employee(0, **_default_args(0)),
    employee.create_employee(1, **_default_args(1)),
    employee.create_employee(2, **_default_args(0)),
]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
@pytest.mark.parametrize(
    'employee_responses',
    [
        pytest.param(_EMPLOYEES, id='employees are only added'),
        pytest.param(
            [
                employee.create_employee(0, **_default_args(0)),
                employee.create_employee(1, **_default_args(0)),
                employee.create_employee(
                    0,
                    phone_pd_id=personal.encode_entity('phone1'),
                    **_default_args(0),
                ),
                employee.create_employee(
                    0, positions=['hozyaushka'], **_default_args(0),
                ),
                employee.create_employee(0, **_default_args(5)),
                employee.create_employee(
                    0,
                    supervisor=employee.create_supervisor(0),
                    **_default_args(0),
                ),
            ],
            id='employee is being updated',
        ),
    ],
)
async def test_fetcher(
        taxi_effrat_employees,
        mockserver,
        employee_responses,
        mocked_time,
        generated_uuids,
):
    curr_employee = 0

    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def handler(request):
        nonlocal curr_employee
        response_employees = employee_responses[
            curr_employee
        ].to_callcenter_response()
        response = mockserver.make_response(
            status=200,
            json={
                'next_cursor': curr_employee,
                'operators': [response_employees],
            },
        )
        curr_employee += 1
        return response

    cursor = None

    for i, emp in enumerate(employee_responses):
        mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=i))
        await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
        query = handler.next_call()['request'].json
        query_limit = query['limit']
        query_cursor = query.get('cursor', None)
        assert query_limit == 50
        assert query_cursor == (None if i == 0 else i - 1)

        request = {'limit': 1}
        if cursor is not None:
            request['cursor'] = cursor
        response = await taxi_effrat_employees.post(
            '/internal/v1/employees/index',
            json=request,
            headers={'Content-Type': 'application/json'},
        )
        cursor = utils.verify_response(response, [emp], generated_uuids)
