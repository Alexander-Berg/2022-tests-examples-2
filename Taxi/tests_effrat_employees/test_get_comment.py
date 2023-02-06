import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils

_EMPLOYEES = [
    employee.create_employee(0, yandex_uid='uid0', domain='taxi'),
    employee.create_employee(1, yandex_uid='uid1', domain='taxi'),
    employee.create_employee(2, yandex_uid='uid2', domain='taxi'),
]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_get(
        taxi_effrat_employees,
        mockserver,
        pgsql,
        taxi_config,
        department_context,
        mock_department,
        synched_gen_staff_dpts_config,
):
    await synched_gen_staff_dpts_config(taxi_config, 1)

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

    db = pgsql['effrat_employees']
    cursor = db.cursor()
    cursor.execute(
        'update effrat_employees.employee '
        'set comment=\'comment about employee-0\' '
        'where yandex_uid=\'uid0\'',
    )
    cursor.execute(
        'update effrat_employees.employee '
        'set comment=\'comment about employee-1\' '
        'where yandex_uid=\'uid1\'',
    )
    cursor.execute(
        'update effrat_employees.employee '
        'set comment=\'comment about employee-2\', '
        'timezone=\'Asia/Yekaterinburg\' '
        'where yandex_uid=\'uid2\'',
    )

    response = await taxi_effrat_employees.get(
        '/admin/v1/employee?yandex_uid=uid0', headers={'X-WFM-Domain': 'taxi'},
    )
    assert response.status_code == 200
    should_be = 'comment about employee-0'
    assert should_be == response.json()['employee']['comment']
    assert response.json()['employee']['timezone'] == 'Europe/Moscow'

    response = await taxi_effrat_employees.get(
        '/admin/v1/employee?yandex_uid=uid1', headers={'X-WFM-Domain': 'taxi'},
    )
    assert response.status_code == 200
    should_be = 'comment about employee-1'
    assert should_be == response.json()['employee']['comment']
    assert response.json()['employee']['timezone'] == 'Europe/Moscow'

    response = await taxi_effrat_employees.get(
        '/admin/v1/employee?yandex_uid=uid2', headers={'X-WFM-Domain': 'taxi'},
    )
    assert response.status_code == 200
    should_be = 'comment about employee-2'
    assert should_be == response.json()['employee']['comment']
    assert response.json()['employee']['timezone'] == 'Asia/Yekaterinburg'
