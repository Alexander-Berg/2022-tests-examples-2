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


def mock_callcenter_operators(mockserver):
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


async def test_responses(taxi_effrat_employees, pgsql, mockserver, testpoint):
    @testpoint('employee-fetcher-done')
    def fetcher_handler(data):
        pass

    mock_callcenter_operators(mockserver)

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    await fetcher_handler.wait_call()
    db = pgsql['effrat_employees']
    cursor = db.cursor()

    cursor.execute(
        'select comment from effrat_employees.employee '
        'where yandex_uid=\'uid0\'',
    )
    rows = cursor.fetchall()
    assert rows[0][0] is None
    await taxi_effrat_employees.post(
        '/admin/v1/employee/update',
        json={'yandex_uid': 'uid0', 'comment': 'comment 0'},
    )
    cursor.execute(
        'select comment from effrat_employees.employee '
        'where yandex_uid=\'uid0\'',
    )
    rows = cursor.fetchall()
    assert rows[0][0] == 'comment 0'
    await taxi_effrat_employees.post(
        '/admin/v1/employee/update',
        json={'yandex_uid': 'uid0', 'comment': ''},
    )
    cursor.execute(
        'select comment from effrat_employees.employee '
        'where yandex_uid=\'uid0\'',
    )
    rows = cursor.fetchall()
    assert rows[0][0] is None


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_updated_employee(
        taxi_effrat_employees, mockserver, mocked_time, testpoint,
):
    @testpoint('employee-fetcher-done')
    def fetcher_handler(data):
        pass

    mock_callcenter_operators(mockserver)
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    await fetcher_handler.wait_call()
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index', json={'limit': 1},
    )
    cursor = response.json()['cursor']
    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.post(
        '/admin/v1/employee/update',
        json={'yandex_uid': 'uid0', 'comment': 'comment 0'},
    )
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index', json={'limit': 1, 'cursor': cursor},
    )
    assert response.json()['employees']


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_updated_employee_timezone(
        taxi_effrat_employees, mockserver, mocked_time, testpoint,
):
    @testpoint('employee-fetcher-done')
    def fetcher_handler(data):
        pass

    mock_callcenter_operators(mockserver)
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    await fetcher_handler.wait_call()
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index', json={'limit': 1},
    )
    cursor = response.json()['cursor']

    for multiplier, set_timezone in enumerate(
            ['Europe/Moscow', 'Asia/Yekaterinburg', ''],
    ):
        mocked_time.set(
            time_utils.NOW + datetime.timedelta(seconds=(multiplier + 1) * 15),
        )
        await taxi_effrat_employees.post(
            '/admin/v1/employee/update',
            json={'yandex_uid': 'uid0', 'timezone': set_timezone},
        )
        response = await taxi_effrat_employees.post(
            '/internal/v1/employees/index',
            json={'limit': 1, 'cursor': cursor},
        )
        response_json = response.json()
        cursor = response_json['cursor']
        assert response_json['employees']
        if set_timezone != '':
            assert response_json['employees'][0]['timezone'] == set_timezone
        else:
            assert 'timezone' not in response_json['employees'][0]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_updated_employee_timezone_comment_crossimmutable(
        taxi_effrat_employees, mockserver, mocked_time,
):
    async def validate_timezone(cursor, timezone):
        body = {'limit': 1}
        if cursor is not None:
            body['cursor'] = cursor
        response = await taxi_effrat_employees.post(
            '/internal/v1/employees/index', json=body,
        )
        response_json = response.json()
        assert response_json['employees']
        if timezone is not None:
            assert response_json['employees'][0]['timezone'] == timezone
        else:
            assert 'timezone' not in response_json['employees'][0]
        return response_json['cursor']

    async def validate_comment(comment):
        response = await taxi_effrat_employees.get(
            '/admin/v1/employee?yandex_uid=uid0',
            headers={'X-WFM-Domain': 'taxi'},
        )
        response_json = response.json()
        if comment is not None:
            assert response_json['employee']['comment'] == comment
        else:
            assert 'comment' not in response_json['employee']

    mock_callcenter_operators(mockserver)
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    await taxi_effrat_employees.post(
        '/admin/v1/employee/update',
        json={'yandex_uid': 'uid0', 'timezone': 'Asia/Yekaterinburg'},
    )
    await taxi_effrat_employees.post(
        '/admin/v1/employee/update',
        json={'yandex_uid': 'uid0', 'comment': 'some comment'},
    )

    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=5))
    cursor = await validate_timezone(None, 'Asia/Yekaterinburg')
    await validate_comment('some comment')

    await taxi_effrat_employees.post(
        '/admin/v1/employee/update',
        json={'yandex_uid': 'uid0', 'timezone': 'Europe/Moscow'},
    )
    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=15))
    cursor = await validate_timezone(cursor, 'Europe/Moscow')
    await validate_comment('some comment')

    await taxi_effrat_employees.post(
        '/admin/v1/employee/update',
        json={'yandex_uid': 'uid0', 'timezone': '', 'comment': ''},
    )
    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=30))
    cursor = await validate_timezone(cursor, None)
    await validate_comment(None)
