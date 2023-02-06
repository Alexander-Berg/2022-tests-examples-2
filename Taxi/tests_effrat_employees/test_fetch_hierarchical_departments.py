import datetime
import re
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


# This is root department for taxi_config, all child departments with relations
# described in staff_v3_groups_tree.json
_USED_DEPARTMENT_IDS_FROM_JSON = (2543,)


def get_untouched_records(pgsql):
    db = pgsql['effrat_employees']
    cur = db.cursor()
    cur.execute(
        'select department_url, department_id, department_level '
        + 'from effrat_employees.subdepartments '
        + 'where department_url = \'this_department_must_be_left_1543\'',
    )
    untouched_departments = cur.fetchall()

    cur.execute(
        'select employee_id, organization_id '
        + 'from effrat_employees.employee_to_organization '
        + 'order by employee_id, organization_id;',
    )
    untouched_organizations = cur.fetchall()
    return untouched_departments, untouched_organizations


@pytest.mark.pgsql('effrat_employees', files=['subdepartments.sql'])
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_fetch_hierarchical_departments_preprofile(
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

    # Check subdepartments tree synchronized
    # Expected /v3/groups calls:
    # 1  headed departments for 10000000000004,10000000000002,10000000000005
    # -  for 10000000000004 (+1)
    # 2    url_division_2543
    # 3    - url_division_3876
    # 4      - url_division_10898
    # 5      - url_division_10899
    # 6      - url_division_10900
    # -  for 10000000000002 (+1)
    # 7    url_division_3876
    # 8    - url_division_10898
    # 9    - url_division_10899
    # 10   - url_division_10900
    # 11   url_division_3876_2
    # 12   - url_division_3876_2_child
    # 13   url_division_3876_3
    # -  for 10000000000005 (empty)
    expected_subdepartment = set(
        [
            'cleaned::this_department_must_be_clean_2543_1',
            'cleaned::this_department_must_be_clean_2543_2',
            'cleaned::this_department_must_be_clean_3876',
            'url_division_10898',
            'url_division_10899',
            'url_division_10900',
            'url_division_2543',
            'url_division_3876',
            'url_division_3876_2',
            'url_division_3876_2_child',
            'url_division_3876_3',
        ],
    )
    await subdepartment_job.wait_call()
    deadline = time.time() + 10.0
    while (
            len(subdepartment_processed) < len(expected_subdepartment)
            and time.time() < deadline
    ):
        await subdepartment_job.wait_call()

    assert subdepartment_processed == expected_subdepartment

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
            'cursor': '2020-06-30T10:10:00+0000_3',
            'employees': load_json('expected-result.json'),
        },
        generated_uuids,
    )

    untouched_departments, untouched_organizations = get_untouched_records(
        pgsql,
    )
    assert untouched_departments == [
        ('this_department_must_be_left_1543', None, None),
    ]
    assert untouched_organizations == [(1, 1), (2, 2), (3, 1)]
