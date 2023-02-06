import datetime

import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils

_EMPLOYEES = [
    employee.create_employee(
        0, departments=department.generate_departments(0),
    ),
]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_update(
        taxi_effrat_employees, mockserver, pgsql, taxi_config, mocked_time,
):
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
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index', json={'limit': 10},
    )
    assert response.status_code == 200

    db = pgsql['effrat_employees']
    cursor = db.cursor()
    cursor.execute(
        'insert into tags.entity(id, value)' 'values(0, \'login0\')',
    )
    cursor.execute(
        'insert into '
        'tags.entity_to_tags(tag_id, ttl, entity_id, updated_at)'
        'values(0, now(), 0, now())',
    )
    cursor.execute(
        'insert into '
        'tags.tag(id, name, description, '
        'domain, color, updated_at)'
        'values(0, \'name_tag0\', \'tag0 about employee0\', '
        '\'taxi\', \'red\', \'1970-01-01 00:00:00+00:00\')',
    )

    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    response_updated = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1, 'cursor': response.json()['cursor']},
    )
    assert response_updated.status_code == 200

    assert response_updated.json()['cursor'] == response.json()['cursor']
