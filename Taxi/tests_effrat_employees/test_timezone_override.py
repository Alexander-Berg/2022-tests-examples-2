import datetime

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
]


def mock_callcenter_operators(mockserver, response):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _(_):
        return mockserver.make_response(status=200, json=response)


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_updated_employee_timezone_twice(
        taxi_effrat_employees, mockserver, mocked_time, testpoint,
):
    @testpoint('employee-fetcher-done')
    def fetcher(data):
        pass

    handle_response = {
        'next_cursor': 5,
        'operators': [
            emp.to_callcenter_response(timezone=None) for emp in _EMPLOYEES
        ],
    }
    mock_callcenter_operators(mockserver, handle_response)

    for multiplier, set_timezone in enumerate(
            ['Europe/Moscow', 'Asia/Yekaterinburg', ''],
    ):
        handle_response['operators'] = [
            emp.to_callcenter_response(timezone='Europe/Moscow')
            for emp in _EMPLOYEES
        ]

        await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
        await fetcher.wait_call()
        mocked_time.set(
            time_utils.NOW
            + datetime.timedelta(seconds=(multiplier * 2 + 1) * 15),
        )
        await taxi_effrat_employees.post(
            '/admin/v1/employee/update',
            json={'yandex_uid': 'uid0', 'timezone': set_timezone},
        )

        response = await taxi_effrat_employees.post(
            '/internal/v1/employees/index', json={'limit': 1},
        )
        response_json = response.json()
        assert response_json['employees']
        if set_timezone != '':
            assert response_json['employees'][0]['timezone'] == set_timezone
        else:
            assert 'timezone' not in response_json['employees'][0]

        handle_response['operators'] = [
            emp.to_callcenter_response(timezone=None) for emp in _EMPLOYEES
        ]
        mocked_time.set(
            time_utils.NOW
            + datetime.timedelta(seconds=(multiplier * 2 + 2) * 15),
        )
        await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
        await fetcher.wait_call()
        response = await taxi_effrat_employees.post(
            '/internal/v1/employees/index', json={'limit': 1},
        )
        response_json = response.json()
        assert response_json['employees']
        if set_timezone:
            assert response_json['employees'][0]['timezone'] == set_timezone
        else:
            assert 'timezone' not in response_json['employees'][0]
