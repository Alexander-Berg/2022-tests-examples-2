import datetime

import pytest

from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import tags
from tests_effrat_employees import time_utils

_EMPLOYEES = [employee.create_employee(0), employee.create_employee(1)]


async def _persons_handler():
    return {
        'page': 1,
        'links': {},
        'limit': 1,
        'result': [
            emp.to_staff_response(time_utils.NOW) for emp in _EMPLOYEES
        ],
    }


@pytest.mark.config(EFFRAT_EMPLOYEES_TAGS_TTL_SETTINGS={'is_working': True})
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_tags_with_ttl(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        mocked_time,
        pgsql,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
        tags_ttl_actlzr_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()

    await employee_fetcher_activate_task()
    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag0'], ['login0'],
    )
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    ttl = mocked_time.now() + datetime.timedelta(seconds=30)
    db = pgsql['effrat_employees']
    cursor = db.cursor()
    cursor.execute(
        f'update tags.entity_to_tags ' f'set ttl=\'{ttl.isoformat()}\';',
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0']],
    )
    mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    await tags_ttl_actlzr_activate_task()
    await tags.check_employees_tags(taxi_effrat_employees, [[]])


@pytest.mark.config(EFFRAT_EMPLOYEES_TAGS_TTL_SETTINGS={'is_working': True})
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_tags_with_ttl_early(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        mocked_time,
        pgsql,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
        tags_ttl_actlzr_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag0'], ['login0'],
    )
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    ttl = mocked_time.now() + datetime.timedelta(minutes=2)
    db = pgsql['effrat_employees']
    cursor = db.cursor()
    cursor.execute(
        f'update tags.entity_to_tags ' f'set ttl=\'{ttl.isoformat()}\';',
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0']],
    )
    mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    await tags_ttl_actlzr_activate_task()
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0']],
    )


@pytest.mark.config(EFFRAT_EMPLOYEES_TAGS_TTL_SETTINGS={'is_working': True})
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_updated_employee_after_ttl(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        mocked_time,
        department_context,
        mock_department,
        pgsql,
        employee_fetcher_activate_task,
        tags_ttl_actlzr_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()

    await employee_fetcher_activate_task()
    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag0'], ['login0'],
    )
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    ttl = mocked_time.now() + datetime.timedelta(minutes=1)
    db = pgsql['effrat_employees']
    cursor = db.cursor()
    cursor.execute(
        f'update tags.entity_to_tags ' f'set ttl=\'{ttl.isoformat()}\';',
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0']],
    )
    mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=1))
    await tags_ttl_actlzr_activate_task()
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1, 'cursor': mocked_time.now().isoformat()},
    )
    assert response.json()['employees']


@pytest.mark.config(EFFRAT_EMPLOYEES_TAGS_TTL_SETTINGS={'is_working': True})
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_updated_employee_after_ttl_(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        mocked_time,
        department_context,
        mock_department,
        pgsql,
        employee_fetcher_activate_task,
        tags_ttl_actlzr_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()

    await employee_fetcher_activate_task()
    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag0'], ['login0'],
    )
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag1'], ['login1'],
    )
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await tags_ttl_actlzr_activate_task()
    ttl_1 = mocked_time.now() + datetime.timedelta(minutes=1)
    ttl_2 = mocked_time.now() + datetime.timedelta(seconds=30)
    db = pgsql['effrat_employees']
    cursor = db.cursor()
    cursor.execute(
        f'update tags.entity_to_tags '
        f'set ttl=\'{ttl_1.isoformat()}\' where tag_id = \'1\';',
    )
    cursor.execute(
        f'update tags.entity_to_tags '
        f'set ttl=\'{ttl_2.isoformat()}\' where tag_id = \'2\';',
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0'], ['test_taxi_tag1']],
    )
    mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    await tags_ttl_actlzr_activate_task()
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1, 'cursor': mocked_time.now().isoformat()},
    )
    assert len(response.json()['employees']) == 1
    assert response.json()['employees'][0]['login'] == 'login0'
