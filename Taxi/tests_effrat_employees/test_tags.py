import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils

_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

_EMPLOYEES = [
    employee.create_employee(
        0,
        departments=[
            department.generate_department(0, 'Subdivision'),
            department.generate_department(0, 'Division'),
        ],
    ),
    employee.create_employee(
        1,
        departments=[
            department.generate_department(0, 'Subdivision'),
            department.generate_department(0, 'Division'),
        ],
    ),
]


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_get(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        pgsql,
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
    cursor.execute(
        'insert into tags.entity(id, value)' 'values(1, \'login1\')',
    )
    cursor.execute(
        'insert into '
        'tags.entity_to_tags(tag_id, ttl, entity_id, updated_at)'
        'values(1, now(), 1, now())',
    )
    cursor.execute(
        'insert into '
        'tags.tag(id, name, description, '
        'domain, color, updated_at)'
        'values(1, \'name_tag1\', \'tag1 about employee1\', '
        '\'taxi\', \'red\', \'1970-01-01 00:00:00+00:00\')',
    )

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 10},
        headers={'Content-Type': 'application/json'},
    )
    response = response.json()
    assert len(response['employees'][0]['tags']) == 1
    should_be = 'name_tag0'
    response_tag = response['employees'][0]['tags'][0]
    assert should_be == response_tag

    assert len(response['employees'][1]['tags']) == 1
    should_be = 'name_tag1'
    response_tag = response['employees'][1]['tags'][0]
    assert should_be == response_tag
