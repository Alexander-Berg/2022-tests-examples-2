import datetime
import typing

import pytest

from tests_effrat_employees import employee
from tests_effrat_employees import time_utils

_EMPLOYEES = [
    employee.create_employee(0, yandex_uid='uid0', domain='taxi'),
    employee.create_employee(1, yandex_uid='uid1', domain='taxi'),
    employee.create_employee(2, yandex_uid='uid2', domain='taxi'),
]


def __persons_handler():
    return {
        'page': 1,
        'links': {},
        'limit': 1,
        'result': [
            emp.to_staff_response(time_utils.NOW) for emp in _EMPLOYEES
        ],
    }


async def _get_employees_list(taxi_effrat_employees, yandex_uids: list):
    response = await taxi_effrat_employees.post(
        '/admin/v1/employees/list',
        headers={'X-WFM-Domain': 'taxi'},
        json={
            'employees_values': [
                {'yandex_uid': yandex_uid} for yandex_uid in yandex_uids
            ],
        },
    )
    assert response.status_code == 200
    return list(
        sorted(response.json()['employees'], key=lambda x: x['yandex_uid']),
    )


def __fetch_tz_sources(pgsql):
    cur = pgsql['effrat_employees'].cursor()
    cur.execute(
        'select staff_login,domain,timezone_source'
        + ' from effrat_employees.employee order by staff_login,domain',
    )
    return cur.fetchall()


async def _update_employees(
        taxi_effrat_employees, yandex_uid: str, timezone: typing.Optional[str],
):
    response = await taxi_effrat_employees.post(
        '/admin/v1/employee/update',
        headers={'X-WFM-Domain': 'taxi'},
        json={'yandex_uid': yandex_uid, 'timezone': timezone},
    )
    return response.status_code


@pytest.mark.pgsql('effrat-employees-greenplum', files=['base_gp.sql'])
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_oracle_import(
        taxi_effrat_employees,
        taxi_config,
        mockserver,
        mock_department,
        employee_fetcher_activate_task,
        oracle_timezone_activate_task,
        synched_gen_staff_dpts_config,
        pgsql,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _persons_handler(_):
        return __persons_handler()

    await synched_gen_staff_dpts_config(taxi_config, 1)

    await employee_fetcher_activate_task()

    response = await _get_employees_list(taxi_effrat_employees, ['uid0'])
    should_be = [{'yandex_uid': 'uid0', 'timezone': 'Europe/Moscow'}]
    assert response == should_be

    await oracle_timezone_activate_task()

    response = await _get_employees_list(taxi_effrat_employees, ['uid0'])
    should_be = [{'yandex_uid': 'uid0', 'timezone': 'Asia/Novosibirsk'}]
    assert response == should_be

    assert __fetch_tz_sources(pgsql) == [
        ('login0', 'taxi', 'oracle'),
        ('login1', 'taxi', 'staff'),
        ('login2', 'taxi', 'staff'),
    ]

    await employee_fetcher_activate_task()

    response = await _get_employees_list(taxi_effrat_employees, ['uid0'])
    should_be = [{'yandex_uid': 'uid0', 'timezone': 'Asia/Novosibirsk'}]
    assert response == should_be

    assert __fetch_tz_sources(pgsql) == [
        ('login0', 'taxi', 'oracle'),
        ('login1', 'taxi', 'staff'),
        ('login2', 'taxi', 'staff'),
    ]

    update_res = await _update_employees(
        taxi_effrat_employees, 'uid0', 'Europe/Rome',
    )
    assert update_res == 200

    assert __fetch_tz_sources(pgsql) == [
        ('login0', 'taxi', 'manual'),
        ('login1', 'taxi', 'staff'),
        ('login2', 'taxi', 'staff'),
    ]

    response = await _get_employees_list(taxi_effrat_employees, ['uid0'])
    should_be = [{'yandex_uid': 'uid0', 'timezone': 'Europe/Rome'}]
    assert response == should_be


async def _get_employees_by_index(
        taxi_effrat_employees, cursor: typing.Optional[str] = None,
) -> typing.Tuple[str, dict]:
    body: dict = {'limit': 100}
    if cursor:
        body['cursor'] = cursor
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index', json=body,
    )
    assert response.status_code == 200
    resp = response.json()
    return (
        resp['cursor'],
        {emp['yandex_uid']: emp for emp in resp['employees']},
    )


def __fetch_employees_updated_at(pgsql):
    cur = pgsql['effrat_employees'].cursor()
    cur.execute(
        'select yandex_uid,staff_login,domain,updated_at'
        + ' from effrat_employees.employee order by staff_login,domain',
    )
    return {
        empl[0]: (empl[1], empl[2], empl[3].astimezone(datetime.timezone.utc))
        for empl in cur.fetchall()
    }


@pytest.mark.pgsql('effrat-employees-greenplum', files=['base_gp.sql'])
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_oracle_import_set_employees_updated(
        taxi_effrat_employees,
        mocked_time,
        taxi_config,
        mockserver,
        mock_department,
        employee_fetcher_activate_task,
        oracle_timezone_activate_task,
        synched_gen_staff_dpts_config,
        pgsql,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _persons_handler(_):
        return __persons_handler()

    await synched_gen_staff_dpts_config(taxi_config, 1)

    await employee_fetcher_activate_task()

    (cursor_snap, response_snap) = await _get_employees_by_index(
        taxi_effrat_employees,
    )
    assert response_snap

    now_snap = mocked_time.now().replace(tzinfo=datetime.timezone.utc)
    mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=15))
    await taxi_effrat_employees.invalidate_caches()

    await oracle_timezone_activate_task()

    updated_at = __fetch_employees_updated_at(pgsql)
    assert updated_at == {
        'uid0': ('login0', 'taxi', now_snap + datetime.timedelta(minutes=15)),
        'uid1': ('login1', 'taxi', now_snap),
        'uid2': ('login2', 'taxi', now_snap),
    }
    (cursor_new, response_new) = await _get_employees_by_index(
        taxi_effrat_employees, cursor_snap,
    )
    assert cursor_new != cursor_snap
    assert len(response_new) == 1
    assert 'uid0' in response_new
    assert response_snap['uid0'] != response_new['uid0']
