import typing as tp

import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils

_EMPLOYEES = [
    employee.create_employee(0, yandex_uid='uid0', domain='taxi'),
    employee.create_employee(1, yandex_uid='uid1', domain='taxi'),
    employee.create_employee(2, yandex_uid='uid2', domain='taxi'),
]


async def _persons_handler():
    return {
        'page': 1,
        'links': {},
        'limit': 1,
        'result': [
            emp.to_staff_response(time_utils.NOW) for emp in _EMPLOYEES
        ],
    }


async def _update_employees(
        taxi_effrat_employees, yandex_uid: str, comment: tp.Optional[str],
):
    response = await taxi_effrat_employees.post(
        '/admin/v1/employee/update',
        headers={'X-WFM-Domain': 'taxi'},
        json={'yandex_uid': yandex_uid, 'comment': comment},
    )
    assert response.status_code == 200


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

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    await _update_employees(
        taxi_effrat_employees, 'uid0', 'comment about employee-0',
    )
    await _update_employees(
        taxi_effrat_employees, 'uid1', 'comment about employee-1',
    )
    await _update_employees(taxi_effrat_employees, 'uid2', None)

    response = await taxi_effrat_employees.post(
        '/admin/v1/employees/list',
        headers={'X-WFM-Domain': 'taxi'},
        json={
            'employees_values': [
                {'yandex_uid': 'uid0'},
                {'yandex_uid': 'uid1'},
                {'yandex_uid': 'uid2'},
            ],
        },
    )
    assert response.status_code == 200
    response = list(
        sorted(response.json()['employees'], key=lambda x: x['yandex_uid']),
    )
    should_be = [
        {
            'yandex_uid': 'uid0',
            'comment': 'comment about employee-0',
            'timezone': 'Europe/Moscow',
        },
        {
            'yandex_uid': 'uid1',
            'comment': 'comment about employee-1',
            'timezone': 'Europe/Moscow',
        },
        {'yandex_uid': 'uid2', 'timezone': 'Europe/Moscow'},
    ]
    assert should_be == response


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_bad_yandex_uid(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        synched_gen_staff_dpts_config,
):
    await synched_gen_staff_dpts_config(taxi_config, 1)

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    await _update_employees(
        taxi_effrat_employees, 'uid0', 'comment about employee-0',
    )

    response = await taxi_effrat_employees.post(
        '/admin/v1/employees/list',
        headers={'X-WFM-Domain': 'taxi'},
        json={
            'employees_values': [
                {'yandex_uid': 'uid0'},
                {'yandex_uid': 'uid3'},
            ],
        },
    )
    assert response.status_code == 200
    response = list(
        sorted(response.json()['employees'], key=lambda x: x['yandex_uid']),
    )
    should_be = [
        {
            'yandex_uid': 'uid0',
            'comment': 'comment about employee-0',
            'timezone': 'Europe/Moscow',
        },
    ]
    assert should_be == response


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_empty_request(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        synched_gen_staff_dpts_config,
):
    await synched_gen_staff_dpts_config(taxi_config, 1)

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    await _update_employees(
        taxi_effrat_employees, 'uid0', 'comment about employee-0',
    )

    response = await taxi_effrat_employees.post(
        '/admin/v1/employees/list',
        headers={'X-WFM-Domain': 'taxi'},
        json={'employees_values': []},
    )
    assert response.status_code == 200
    response = list(
        sorted(response.json()['employees'], key=lambda x: x['yandex_uid']),
    )
    should_be = []
    assert should_be == response
