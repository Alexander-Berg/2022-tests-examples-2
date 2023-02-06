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


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_append(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag0'], ['login0'],
    )
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag1'], ['login1'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0'], ['test_taxi_tag1']],
    )
    await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0', 'test_taxi_tag1'],
        ['login0'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees,
        [['test_taxi_tag0', 'test_taxi_tag1'], ['test_taxi_tag1']],
    )
    await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0', 'test_taxi_tag1'],
        ['login0', 'login1'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees,
        [
            ['test_taxi_tag0', 'test_taxi_tag1'],
            ['test_taxi_tag0', 'test_taxi_tag1'],
        ],
    )


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_replace(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag0'], ['login0'],
    )
    await tags.update_employee_tags(
        taxi_effrat_employees, 'replace', ['test_taxi_tag1'], ['login0'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag1']],
    )
    await tags.update_employee_tags(
        taxi_effrat_employees,
        'replace',
        ['test_taxi_tag0', 'test_taxi_tag1'],
        ['login0'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0', 'test_taxi_tag1']],
    )


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_no_duplicates(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    await employee_fetcher_activate_task()
    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag0'], ['login0'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0']],
    )
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag0'], ['login0'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0']],
    )


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_no_duplicates_bulk(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0', 'test_taxi_tag1'],
        ['login0'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0', 'test_taxi_tag1']],
    )
    await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0', 'test_taxi_tag1'],
        ['login0', 'login1'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees,
        [
            ['test_taxi_tag0', 'test_taxi_tag1'],
            ['test_taxi_tag0', 'test_taxi_tag1'],
        ],
    )


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_delete_tags(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0', 'test_taxi_tag1'],
        ['login0'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0', 'test_taxi_tag1']],
    )
    await tags.update_employee_tags(
        taxi_effrat_employees, 'replace', [], ['login0'],
    )
    await tags.check_employees_tags(taxi_effrat_employees, [[]])


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_empty_append(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()

    await employee_fetcher_activate_task()
    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0', 'test_taxi_tag1'],
        ['login0'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0', 'test_taxi_tag1']],
    )
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', [], ['login0'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0', 'test_taxi_tag1']],
    )


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_duplicate_entities(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0'],
        ['login0', 'login0'],
    )
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0']],
    )


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_duplicate_tags(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    await tags.add_tags(taxi_effrat_employees)
    response = await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0', 'test_taxi_tag0'],
        ['login0'],
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Duplicate tag \"test_taxi_tag0\"'


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_bad_tag(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    await tags.add_tags(taxi_effrat_employees)

    response = await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag3'], ['login0'],
    )
    assert response.status_code == 400
    assert response.json()['message'] == 'Nonexistent tags were passed'


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_updated_employee(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        mocked_time,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index', json={'limit': 1},
    )
    cursor = response.json()['cursor']
    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()
    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0', 'test_taxi_tag1'],
        ['login0'],
    )
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index', json={'limit': 1, 'cursor': cursor},
    )
    assert response.json()['employees']


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_tags_with_different_domains(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    await tags.add_tags(taxi_effrat_employees)
    await tags.add_tags(
        taxi_effrat_employees, ['test_taxi_tag0', 'test_taxi_tag1'], 'lavka',
    )
    response = await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0', 'test_taxi_tag1'],
        ['login0'],
    )
    assert response.status_code == 200
    await tags.check_employees_tags(
        taxi_effrat_employees, [['test_taxi_tag0', 'test_taxi_tag1']],
    )


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_updated_employee_with_deleted_tag(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        mocked_time,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()

    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees,
        'append',
        ['test_taxi_tag0', 'test_taxi_tag1'],
        ['login0'],
    )
    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()

    await taxi_effrat_employees.delete(
        '/admin/v1/tags?name=test_taxi_tag0', headers={'X-WFM-Domain': 'taxi'},
    )
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1, 'cursor': mocked_time.now().isoformat()},
    )
    assert response.json()['employees']


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_not_updated_employee_after_delete_tag(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        mocked_time,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler()

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    await employee_fetcher_activate_task()

    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()

    await tags.add_tags(taxi_effrat_employees)
    await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag0'], ['login0'],
    )
    mocked_time.set(mocked_time.now() + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()

    await taxi_effrat_employees.delete(
        '/admin/v1/tags?name=test_taxi_tag1', headers={'X-WFM-Domain': 'taxi'},
    )
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1, 'cursor': mocked_time.now().isoformat()},
    )
    assert not response.json()['employees']


@pytest.mark.now(time_utils.NOW.isoformat('T'))
@pytest.mark.pgsql('effrat_employees', files=['employee_domain_switch.sql'])
async def test_employee_tags_with_domain_switch(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        mocked_time,
        department_context,
        mock_department,
        pgsql,
):
    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=15))
    response = await tags.update_employee_tags(
        taxi_effrat_employees, 'append', ['test_taxi_tag1'], ['login0'],
    )
    assert response.status_code == 200

    employee_response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 10},
        headers={'Content-Type': 'application/json'},
    )
    assert employee_response.status_code == 200
    assert (await tags.get_employee_tags(taxi_effrat_employees)) == [
        {'login': 'login0', 'domain': 'lavka', 'tags': ['test_lavka_tag3']},
        {
            'login': 'login0',
            'domain': 'taxi',
            'tags': ['test_taxi_tag0', 'test_taxi_tag1'],
        },
    ]

    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=25))
    response = await tags.update_employee_tags(
        taxi_effrat_employees,
        'replace',
        tags=['test_taxi_tag0'],
        entities=['login0'],
        domain='taxi',
    )
    assert response.status_code == 200

    assert (await tags.get_employee_tags(taxi_effrat_employees)) == [
        {'login': 'login0', 'domain': 'lavka', 'tags': ['test_lavka_tag3']},
        {'login': 'login0', 'domain': 'taxi', 'tags': ['test_taxi_tag0']},
    ]
