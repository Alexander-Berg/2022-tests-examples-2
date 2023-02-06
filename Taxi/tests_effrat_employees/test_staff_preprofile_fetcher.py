import datetime

import pytest

# flake8: noqa
# pylint: disable=import-error, import-only-modules, redefined-outer-name
from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import time_utils
from tests_effrat_employees.preprofile import preprofile_mock
from tests_effrat_employees import utils

_USED_DEPARTMENT_IDS_FROM_JSON = (7520, 10171, 2543)


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_staff_preprofile_fetcher(
        taxi_effrat_employees,
        mockserver,
        mocked_time,
        load_json,
        taxi_config,
        preprofile_mock,
        testpoint,
        generated_uuids,
):
    department.set_staff_departments_config(
        taxi_config,
        [
            dep
            for idx, dep in preprofile_mock.departments.items()
            if idx in _USED_DEPARTMENT_IDS_FROM_JSON
        ],
    )

    @testpoint('subdepartment-actualizer::job')
    def subdepartment_job(data):
        pass

    for offset, _ in enumerate(_USED_DEPARTMENT_IDS_FROM_JSON):
        mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=offset))
        await taxi_effrat_employees.invalidate_caches()
        await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
        await subdepartment_job.wait_call()
        await preprofile_mock.staff_departmentstaff_handler.wait_call()
        await preprofile_mock.helpdesk_handler.wait_call()

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 10},
        headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json['employees'].sort(key=lambda x: x['yandex_uid'])
    assert response_json == utils.extended_index_response(
        {
            'cursor': '2020-06-30T10:12:00+0000_4',
            'employees': load_json('expected-result.json'),
        },
        generated_uuids,
    )


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_staff_preprofile_fetcher_multiple_domains(
        taxi_effrat_employees,
        mockserver,
        mocked_time,
        load_json,
        taxi_config,
        preprofile_mock,
        testpoint,
        generated_uuids,
):
    local_departments = [7520, 9999]
    cfg_departments = [
        dep
        for idx, dep in preprofile_mock.departments.items()
        if idx in local_departments
    ]
    cfg_departments[1].domain = 'market'

    department.set_staff_departments_config(taxi_config, cfg_departments)

    @testpoint('subdepartment-actualizer::job')
    def subdepartment_job(data):
        pass

    for offset, _ in enumerate(local_departments):
        mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=offset))
        await taxi_effrat_employees.invalidate_caches()
        await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
        await subdepartment_job.wait_call()
        await preprofile_mock.staff_departmentstaff_handler.wait_call()
        await preprofile_mock.helpdesk_handler.wait_call()

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 10},
        headers={'Content-Type': 'application/json'},
    )
    assert response.status_code == 200
    response_json = response.json()
    response_json['employees'].sort(
        key=lambda x: (x['yandex_uid'], x['source']),
    )
    assert response_json == utils.extended_index_response(
        {
            'cursor': '2020-06-30T10:11:00+0000_2',
            'employees': load_json('expected-result.json'),
        },
        generated_uuids,
    )
