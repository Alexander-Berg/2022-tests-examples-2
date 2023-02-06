import copy
import datetime
import json

import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import time_utils

_EMPLOYEES = [
    employee.create_employee(
        0,
        departments=[
            department.generate_department(0, 'Subdivision'),
            department.generate_department(0, 'Division'),
        ],
        domain='taxi',
    ),
]

# pylint: disable=W0102
async def _add_tags(taxi_effrat_employees, domains=['taxi', 'lavka']):
    for domain in domains:
        await taxi_effrat_employees.put(
            '/admin/v1/tags?name=новичок',
            headers={'X-WFM-Domain': domain},
            json={'color': '#6900ff', 'description': 'самый новый оператор'},
        )
        await taxi_effrat_employees.put(
            '/admin/v1/tags?name=ньюнью',
            headers={'X-WFM-Domain': domain},
            json={'color': '#f8f8f8', 'description': 'сваоипвопшя'},
        )
        await taxi_effrat_employees.put(
            '/admin/v1/tags?name=оченьдлинныйтегдлятеста',
            headers={'X-WFM-Domain': domain},
            json={'color': '#fa2000', 'description': 'собирается уволиться'},
        )
        await taxi_effrat_employees.put(
            '/admin/v1/tags?name=потеряшка',
            headers={'X-WFM-Domain': domain},
            json={'color': '#ff6f6f', 'description': 'собирается уволиться'},
        )


async def _persons_handler(local_employees):
    return {
        'page': 1,
        'links': {},
        'limit': 1,
        'result': [
            emp.to_staff_response(time_utils.NOW) for emp in local_employees
        ],
    }


async def _operators_handler(request, local_operators):
    request_json = json.loads(request.get_data())
    operators = list(
        filter(
            lambda x: x['domain'] == request.headers['X-WFM-Domain']
            and x['yandex_uid'] in request_json['yandex_uids'],
            local_operators,
        ),
    )[request_json['offset'] : request_json['offset'] + request_json['limit']]
    return {'operators': operators, 'full_count': len(operators)}


async def _add_employees(
        taxi_effrat_employees,
        taxi_config,
        mocked_time,
        local_employees,
        mockserver,
        department_context,
        mock_department,
):
    staff_departments = [
        department.StaffDepartment(
            department.generate_department(0, 'Division'), 'taxi',
        ),
    ]
    department_context.set_data(staff_departments)
    department.set_staff_departments_config(taxi_config, staff_departments)
    local_employees.append(
        employee.create_employee(
            1,
            departments=[
                department.generate_department(0, 'Subdivision'),
                department.generate_department(0, 'Division'),
            ],
        ),
    )
    local_employees.append(
        employee.create_employee(
            2,
            departments=[
                department.generate_department(0, 'Subdivision'),
                department.generate_department(0, 'Division'),
            ],
        ),
    )
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')


async def _add_employees_with_different_domains(
        taxi_effrat_employees,
        taxi_config,
        mocked_time,
        local_employees,
        mockserver,
        department_context,
        mock_department,
):
    staff_departments = [
        department.StaffDepartment(
            department.generate_department(0, 'Division'), 'taxi',
        ),
    ]
    department_context.set_data(staff_departments)
    department.set_staff_departments_config(taxi_config, staff_departments)
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')

    del local_employees[0]
    staff_departments.append(
        department.StaffDepartment(
            department.generate_department(1, 'Division'), 'lavka',
        ),
    )
    department.set_staff_departments_config(taxi_config, staff_departments)
    local_employees.append(
        employee.create_employee(
            1,
            departments=[
                department.generate_department(1, 'Subdivision'),
                department.generate_department(1, 'Division'),
            ],
            domain='lavka',
        ),
    )
    mocked_time.set(time_utils.NOW + datetime.timedelta(minutes=1))
    await taxi_effrat_employees.invalidate_caches()
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')


async def _check_employee_tags(taxi_effrat_employees, should_be):
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 10},
        headers={'Content-Type': 'application/json'},
    )
    response = list(
        sorted(response.json()['employees'], key=lambda x: x['login']),
    )
    assert len(response) == len(should_be)
    for response_operator, should_be_tags in zip(response, should_be):
        operator_tags = list(sorted(response_operator['tags']))
        should_be_tags = list(sorted(should_be_tags))
        assert operator_tags == should_be_tags


@pytest.mark.config(
    EFFRAT_EMPLOYEES_TAGS_FETCHER_SETTINGS={
        'interval_m': 1,
        'is_working': True,
        'limit': 1,
        'timeout_ms': 0,
    },
)
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_config_update(
        taxi_effrat_employees,
        taxi_config,
        mocked_time,
        mockserver,
        department_context,
        mock_department,
):
    local_operators = [
        {
            'yandex_uid': 'uid0',
            'login': 'login0',
            'full_name': 'surname0 name0 fathername0',
            'domain': 'taxi',
            'tags': ['новичок', 'ньюнью'],
        },
        {
            'yandex_uid': 'uid1',
            'login': 'login1',
            'full_name': 'surname1 name1 fathername1',
            'domain': 'lavka',
            'tags': ['новичок', 'потеряшка'],
        },
    ]
    local_employees = copy.deepcopy(_EMPLOYEES)

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler(local_employees)

    @mockserver.json_handler('workforce-management/v2/operators/values')
    async def _(request):
        return await _operators_handler(
            request, local_operators=local_operators,
        )

    await _add_employees_with_different_domains(
        taxi_effrat_employees,
        taxi_config,
        mocked_time,
        local_employees,
        mockserver,
        department_context,
        mock_department,
    )
    await _add_tags(taxi_effrat_employees)
    await cron.activate_task(taxi_effrat_employees, 'wfm-tags-fetcher')

    await _check_employee_tags(
        taxi_effrat_employees,
        [['новичок', 'ньюнью'], ['новичок', 'потеряшка']],
    )


@pytest.mark.config(
    EFFRAT_EMPLOYEES_TAGS_FETCHER_SETTINGS={
        'interval_m': 1,
        'is_working': True,
        'limit': 2,
        'timeout_ms': 0,
    },
)
@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_limit(
        taxi_effrat_employees,
        taxi_config,
        mocked_time,
        mockserver,
        department_context,
        mock_department,
):
    local_operators = [
        {
            'yandex_uid': 'uid0',
            'login': 'login0',
            'full_name': 'surname0 name0 fathername0',
            'domain': 'taxi',
            'tags': ['новичок', 'ньюнью'],
        },
        {
            'yandex_uid': 'uid1',
            'login': 'login1',
            'full_name': 'surname1 name1 fathername1',
            'domain': 'taxi',
            'tags': ['новичок', 'потеряшка'],
        },
        {
            'yandex_uid': 'uid2',
            'login': 'login2',
            'full_name': 'surname2 name2 fathername2',
            'domain': 'taxi',
            'tags': ['потеряшка', 'оченьдлинныйтегдлятеста'],
        },
    ]
    local_employees = copy.deepcopy(_EMPLOYEES)

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        return await _persons_handler(local_employees)

    @mockserver.json_handler('workforce-management/v2/operators/values')
    async def _(request):
        return await _operators_handler(request, local_operators)

    await _add_employees(
        taxi_effrat_employees,
        taxi_config,
        mocked_time,
        local_employees,
        mockserver,
        department_context,
        mock_department,
    )
    await _add_tags(taxi_effrat_employees)
    await cron.activate_task(taxi_effrat_employees, 'wfm-tags-fetcher')

    await _check_employee_tags(
        taxi_effrat_employees,
        [
            ['новичок', 'ньюнью'],
            ['новичок', 'потеряшка'],
            ['потеряшка', 'оченьдлинныйтегдлятеста'],
        ],
    )
