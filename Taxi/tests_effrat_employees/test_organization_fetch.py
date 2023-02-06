import datetime
import time

import pytest

# flake8: noqa
# pylint: disable=import-only-modules, redefined-outer-name
from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import time_utils
from tests_effrat_employees.preprofile import preprofile_mock
from tests_effrat_employees.staff import StaffGroupsQuery
from tests_effrat_employees import utils

_USED_DEPARTMENT_IDS_FROM_JSON = (2543, 2534)


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_organization_fetch(
        taxi_effrat_employees,
        mockserver,
        mocked_time,
        load_json,
        taxi_config,
        preprofile_mock,
        testpoint,
        pgsql,
        generated_uuids,
):
    staff_groups_query = StaffGroupsQuery(load_json)
    preprofile_mock.staff_groups_response = staff_groups_query.response

    subdepartment_processed = set()

    @testpoint('subdepartment-actualizer::job')
    def subdepartment_job(data):
        subdepartment_processed.add(data['url'])
        for clean in data.get('cleaned', []):
            subdepartment_processed.add('cleaned::' + clean)

    department.set_staff_departments_config(
        taxi_config,
        [
            dep
            for idx, dep in preprofile_mock.departments.items()
            if idx in _USED_DEPARTMENT_IDS_FROM_JSON
        ],
    )
    await taxi_effrat_employees.invalidate_caches()

    for offset in range(len(_USED_DEPARTMENT_IDS_FROM_JSON)):
        mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=offset))
        await taxi_effrat_employees.invalidate_caches()
        await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
        await preprofile_mock.staff_departmentstaff_handler.wait_call()
        await preprofile_mock.helpdesk_handler.wait_call()

    expected_subdepartment = set(['url_division_2543', 'url_division_2534'])
    await subdepartment_job.wait_call()
    deadline = time.time() + 10.0
    while (
            len(subdepartment_processed) < len(expected_subdepartment)
            and time.time() < deadline
    ):
        await subdepartment_job.wait_call()

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index', json={'limit': 10},
    )
    assert response.status_code == 200
    response_json = response.json()
    for employee in response_json['employees']:
        employee['subdepartments'].sort()
    response_json['employees'].sort(key=lambda x: x['yandex_uid'])
    assert response_json == utils.extended_index_response(
        {
            'cursor': '2020-06-30T10:11:00+0000_2',
            'employees': [
                {
                    'departments': ['url_division_2534'],
                    'employee_uid': 'be23e3e8-0787-4602-9081-4ec48cac90df',
                    'employment_datetime': '2022-01-27T00:00:00+00:00',
                    'employment_status': 'preprofile_approved',
                    'full_name': 'ПоследнееИмя_0 ПервоеИмя_0 ',
                    'login': 'Login_0',
                    'organization': {'country_code': 'RU', 'name': 'Орг 003'},
                    'positions': [],
                    'source': 'eats',
                    'subdepartments': [],
                    'tags': [],
                    'timezone': 'Europe/Moscow',
                    'yandex_uid': '1100000000000001',
                },
                {
                    'departments': ['url_division_2543'],
                    'employee_uid': 'b29796b6-108f-4ffa-ab14-5974c0522e3b',
                    'employment_datetime': '2022-01-27T00:00:00+00:00',
                    'employment_status': 'preprofile_approved',
                    'full_name': 'ПоследнееИмя_0 ПервоеИмя_0 ',
                    'login': 'Login_0',
                    'organization': {'country_code': 'RU', 'name': 'Орг 003'},
                    'positions': [],
                    'source': 'taxi',
                    'subdepartments': [],
                    'tags': [],
                    'timezone': 'Europe/Moscow',
                    'yandex_uid': '1100000000000001',
                },
            ],
        },
        generated_uuids,
    )
