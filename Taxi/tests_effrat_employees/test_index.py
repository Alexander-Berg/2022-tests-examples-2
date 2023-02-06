import copy
import datetime

import pytest

# flake8: noqa
# pylint: disable=import-only-modules, redefined-outer-name
from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils
from tests_effrat_employees import utils
from tests_effrat_employees.staff import StaffGroupsQuery

_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S%z'

_EMPLOYEES = [
    employee.create_employee(
        0, departments=department.generate_departments(0),
    ),
]

_GEN_DEPARTMENTS_COUNT = 1


async def test_empty_responses(taxi_effrat_employees):
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index', json={'limit': 1},
    )
    assert (
        response.json()['cursor']
        == f'{time_utils.time_to_string(time_utils.EPOCH)}_0'
    )
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1, 'cursor': time_utils.NOW.isoformat()},
    )
    assert (
        response.json()['cursor']
        == f'{time_utils.time_to_string(time_utils.NOW)}_0'
    )


@pytest.mark.parametrize(
    'lag_s, login_idx, login, subdepartments_insert',
    [
        (60, 0, 'login0', None),
        (0, 1, 'login1', None),
        (0, 2, 'login2', 'subdepartments.sql'),
    ],
)
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_lag(
        taxi_effrat_employees,
        mockserver,
        mocked_time,
        taxi_config,
        lag_s,
        login_idx,
        login,
        subdepartments_insert,
        department_context,
        mock_department,
        load_json,
        load,
        pgsql,
        testpoint,
        synched_gen_staff_dpts_config,
        generated_uuids,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def persons_handler(_):
        return {
            'page': 1,
            'links': {},
            'limit': 1,
            'result': [
                emp.to_staff_response(time_utils.NOW)
                for emp in local_employees
            ],
        }

    @mockserver.json_handler('staff-for-wfm/v3/groups')
    def _groups_handler(request):
        if subdepartments_insert:
            return StaffGroupsQuery(load_json).response(request)
        return {'page': 1, 'links': {}, 'limit': 1, 'result': []}

    @testpoint('subdepartment-actualizer::job')
    def subdepartment_job(data):
        pass

    await taxi_effrat_employees.invalidate_caches()

    if subdepartments_insert:
        db = pgsql['effrat_employees']
        cur = db.cursor()
        cur.execute(load(subdepartments_insert))

    local_employees = copy.deepcopy(_EMPLOYEES)
    taxi_config.set_values(
        dict(EFFRAT_EMPLOYEES_INDEX_SETTINGS={'lag_s': lag_s}),
    )
    await taxi_effrat_employees.invalidate_caches()
    await synched_gen_staff_dpts_config(taxi_config, _GEN_DEPARTMENTS_COUNT)

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    for _ in range(1):  # count depends on depth of staff_v3_groups_tree.json
        await subdepartment_job.wait_call()
    await persons_handler.wait_call()

    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()
    local_employees.append(
        employee.create_employee(
            login_idx, departments=department.generate_departments(0),
        ),
    )
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1, 'cursor': mocked_time.now().isoformat()},
    )
    response = response.json()
    for emp in response['employees']:
        emp['subdepartments'].sort()
    assert response == utils.extended_index_response(
        load_json(f'base_{login}.json'), generated_uuids,
    ), f'invalid response for {login}'


@pytest.mark.config(EFFRAT_EMPLOYEES_INDEX_SETTINGS={'lag_s': 0})
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_index_subdepartments_load(
        taxi_effrat_employees,
        mockserver,
        mocked_time,
        taxi_config,
        department_context,
        mock_department,
        load_json,
        testpoint,
        synched_gen_staff_dpts_config,
        generated_uuids,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _persons_handler(_):
        return {
            'page': 1,
            'links': {},
            'limit': 1,
            'result': [
                emp.to_staff_response(time_utils.NOW)
                for emp in local_employees
            ],
        }

    @mockserver.json_handler('staff-for-wfm/v3/groups')
    def _groups_handler(request):
        return StaffGroupsQuery(load_json).response(request)

    @testpoint('subdepartment-actualizer::job')
    def subdepartment_job(data):
        pass

    await synched_gen_staff_dpts_config(taxi_config, _GEN_DEPARTMENTS_COUNT)
    local_employees = copy.deepcopy(_EMPLOYEES)
    await taxi_effrat_employees.invalidate_caches()

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    mocked_time.set(time_utils.NOW + datetime.timedelta(seconds=55))
    await taxi_effrat_employees.invalidate_caches()
    local_login_idx = 2
    local_employees.append(
        employee.create_employee(
            local_login_idx, departments=department.generate_departments(0),
        ),
    )
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    for _ in range(1):  # count depends on depth of staff_v3_groups_tree.json
        await subdepartment_job.wait_call()

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1, 'cursor': mocked_time.now().isoformat()},
    )
    response = response.json()
    for empres in response['employees']:
        empres['subdepartments'].sort()
    assert response == utils.extended_index_response(
        load_json(f'base_login2.json'), generated_uuids,
    )
