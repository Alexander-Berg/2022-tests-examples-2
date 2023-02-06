import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils


_EMPLOYEES = [
    employee.create_employee(
        0,
        mentor_login=employee.create_mentor(
            250, login='login_mentor_of_0',
        ).login,
    ),
    employee.create_employee(
        1,
        login='login_mentor_of_0',
        full_name='name mentor of_0',
        mentor_login=employee.create_mentor(
            251, login='login_mentor_of_1',
        ).login,
    ),
    employee.create_employee(
        2,
        login='login_mentor_of_1',
        full_name='name mentor of_1',
        mentor_login=employee.create_mentor(
            252, login='login_mentor_of_2',
        ).login,
    ),
    # employee with id=3 should not be mentor,
    # since he is fired
    employee.create_employee(
        3,
        employment_status='fired',
        login='login_mentor_of_2',
        full_name='name mentor of_2',
        mentor_login=employee.create_mentor(
            252, login='login_mentor_of_3',
        ).login,
    ),
    # employee with id=4 should not be mentor,
    # since he is a mentor of fired man
    employee.create_employee(
        4,
        login='login_mentor_of_3',
        full_name='name mentor of_3',
        mentor_login=employee.create_mentor(
            252, login='login_mentor_of_4',
        ).login,
    ),
]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_get(taxi_effrat_employees, mockserver, taxi_config):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _(_):
        return mockserver.make_response(
            status=200,
            json={
                'next_cursor': 5,
                'operators': [
                    emp.to_callcenter_response() for emp in _EMPLOYEES
                ],
            },
        )

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    response = await taxi_effrat_employees.get(
        '/admin/v1/mentors', headers={'X-WFM-Domain': 'taxi'},
    )
    assert response.status_code == 200
    response = list(
        map(
            employee.mentor_from_ee_response,
            sorted(response.json()['mentors'], key=lambda x: x['login']),
        ),
    )
    should_be = [
        employee.create_mentor(
            1, login='login_mentor_of_0', name='name mentor of_0',
        ),
        employee.create_mentor(
            2, login='login_mentor_of_1', name='name mentor of_1',
        ),
        employee.create_mentor(3, login='login_mentor_of_4', name=None),
    ]
    should_be = list(sorted(should_be, key=lambda x: x.login))
    assert should_be == response
