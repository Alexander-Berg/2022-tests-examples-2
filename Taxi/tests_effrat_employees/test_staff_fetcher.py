import dataclasses
import datetime
import typing as tp

import pytest

from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import employee
from tests_effrat_employees import personal
from tests_effrat_employees import staff
from tests_effrat_employees import time_utils
from tests_effrat_employees import utils

_EMPLOYEES = [
    employee.create_employee(0),
    employee.create_employee(1),
    employee.create_employee(
        2, departments=department.generate_departments(0),
    ),
]


_GROUP_SIZE = 2


def make_chunks(
        array: tp.List[tp.Any], chunk_size: int,
) -> tp.List[tp.List[tp.Any]]:
    index = 0
    size = len(array)
    answer = []
    while index < size:
        answer.append(array[index : min(size, index + chunk_size)])
        index += chunk_size
    return answer


# Each group will be paginated separately.
# If testcase has 3 groups, firstly it will iterate over first group
# by incrementing _page parameter. Then employees from second group
# will be processed.
# As if each next group becomes available only after previous one was read
@dataclasses.dataclass
class StaffResponseGroup:
    employees: tp.List[employee.EmployeeModel]
    updated_at_from_request: datetime.timedelta


@pytest.mark.now(time_utils.NOW.isoformat('T'))
@pytest.mark.config(
    EFFRAT_EMPLOYEES_STAFF_FETCHER_SETTINGS={'limit': 1, 'lag_m': 30},
)
@pytest.mark.parametrize(
    'employee_responses, empty_update_indices',
    [
        pytest.param(
            [
                employee.create_employee(0),
                employee.create_employee(0),
                employee.create_employee(
                    1, departments=department.generate_departments(0),
                ),
                employee.create_employee(
                    0, phone_pd_id=personal.encode_entity('phone1'),
                ),
                employee.create_employee(0, positions=['hozyaushka']),
                employee.create_employee(
                    0, departments=department.generate_departments(359),
                ),
                employee.create_employee(
                    0, supervisor=employee.create_supervisor(0),
                ),
            ],
            [1],
            id='employee is being updated',
        ),
    ],
)
async def test_single_department_update(
        taxi_effrat_employees,
        mockserver,
        employee_responses,
        empty_update_indices,
        mocked_time,
        taxi_config,
        department_context,
        mock_department,
        generated_uuids,
):
    modified_at = time_utils.NOW - datetime.timedelta(hours=10)
    chunks = make_chunks(employee_responses, _GROUP_SIZE)
    groups = []
    for i, chunk in enumerate(chunks):
        groups.append(
            StaffResponseGroup(
                chunk,
                time_utils.EPOCH
                if i == 0
                else modified_at
                + datetime.timedelta(minutes=i * _GROUP_SIZE - 1),
            ),
        )
    # add empty group
    groups.insert(1, StaffResponseGroup([], groups[1].updated_at_from_request))
    current_group = 0
    index_in_group = 0

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def handler(request):
        nonlocal modified_at
        nonlocal current_group
        nonlocal index_in_group
        nonlocal groups
        if index_in_group == len(groups[current_group].employees):
            res = {
                'page': index_in_group,
                'links': {},
                'limit': 1,
                'result': [],
            }
            current_group += 1
            index_in_group = 0
            return res

        emp = groups[current_group].employees[index_in_group]
        index_in_group += 1
        response = emp.to_staff_response(modified_at)
        modified_at += datetime.timedelta(minutes=1)

        return {
            'page': index_in_group - 1,
            'links': {},
            'limit': 1,
            'result': [response],
        }

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()

    cursor = None

    iteration = 0
    for group in groups:
        for i, emp in enumerate(group.employees):
            now = time_utils.NOW + datetime.timedelta(minutes=iteration)
            mocked_time.set(now)
            await taxi_effrat_employees.invalidate_caches()
            await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
            request_query = handler.next_call()['request'].query
            query = staff.StaffDepartmentsQuery(request_query['_query'])
            assert int(request_query['_limit']) == 1
            assert int(request_query['_page']) == i + 1
            assert query.modified_at == group.updated_at_from_request
            assert (
                query.departments
                == [
                    department.generate_staff_departments(
                        0,
                    ).department.external_id,
                ]
                * 2
            )

            request = {}
            if cursor is not None:
                request['cursor'] = cursor
            response = await taxi_effrat_employees.post(
                '/internal/v1/employees/index',
                json={'limit': 1, 'cursor': cursor},
                headers={'Content-Type': 'application/json'},
            )
            # update is empty, because staff's update
            # didn't change fields of our interest
            response_should_be = (
                [] if iteration in empty_update_indices else [emp]
            )
            cursor = utils.verify_response(
                response, response_should_be, generated_uuids,
            )
            iteration += 1

        await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
        request_query = handler.next_call()['request'].query
        assert int(request_query['_page']) == len(group.employees) + 1


@pytest.mark.now(time_utils.NOW.isoformat('T'))
@pytest.mark.config(
    EFFRAT_EMPLOYEES_STAFF_FETCHER_SETTINGS={'limit': 42, 'lag_m': 30},
)
@pytest.mark.parametrize(
    'employee_responses, empty_update_indices, number_of_staff_departments',
    [pytest.param(_EMPLOYEES, [], 2, id='employees are only added')],
)
async def test_several_departments(
        taxi_effrat_employees,
        mockserver,
        employee_responses,
        empty_update_indices,
        number_of_staff_departments,
        mocked_time,
        taxi_config,
        department_context,
        mock_department,
        generated_uuids,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def handler(request):
        nonlocal modified_at
        nonlocal curr_employee
        emp = employee_responses[curr_employee]
        curr_employee += 1
        response = emp.to_staff_response(modified_at)
        modified_at += datetime.timedelta(minutes=1)

        return {'page': 1, 'links': {}, 'limit': 1, 'result': [response]}

    modified_at = time_utils.NOW - datetime.timedelta(hours=10)
    curr_employee = 0
    department.gen_staff_departments_config(
        taxi_config, number_of_staff_departments,
    )
    await taxi_effrat_employees.invalidate_caches()

    cursor = None

    query_modification_times = (
        [time_utils.EPOCH] * number_of_staff_departments
        + [
            time_utils.NOW
            - datetime.timedelta(hours=10)
            + datetime.timedelta(minutes=i)
            for i in range(len(employee_responses))
        ]
    )
    for i, emp in enumerate(employee_responses):
        now = time_utils.NOW + datetime.timedelta(minutes=i)
        mocked_time.set(now)
        await taxi_effrat_employees.invalidate_caches()
        await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
        request_query = handler.next_call()['request'].query
        query = staff.StaffDepartmentsQuery(request_query['_query'])
        assert int(request_query['_limit']) == 42
        assert int(request_query['_page']) == 1
        assert query.modified_at == query_modification_times[i]
        assert (
            query.departments
            == [
                department.generate_staff_departments(
                    i % number_of_staff_departments,
                ).department.external_id,
            ]
            * 2
        )

        request = {}
        if cursor is not None:
            request['cursor'] = cursor
        response = await taxi_effrat_employees.post(
            '/internal/v1/employees/index',
            json={'limit': 1, 'cursor': cursor},
            headers={'Content-Type': 'application/json'},
        )
        response_should_be = [] if i in empty_update_indices else [emp]
        cursor = utils.verify_response(
            response, response_should_be, generated_uuids,
        )


@pytest.mark.now(time_utils.NOW.isoformat('T'))
@pytest.mark.config(
    EFFRAT_EMPLOYEES_STAFF_FETCHER_SETTINGS={'limit': 42, 'lag_m': 30},
)
async def test_recent_update(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def handler(request):
        modified_at = time_utils.NOW - datetime.timedelta(minutes=1)
        response = _EMPLOYEES[0].to_staff_response(modified_at)
        return {'page': 1, 'links': {}, 'limit': 1, 'result': [response]}

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    handler.next_call()
    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    request_query = handler.next_call()['request'].query
    query = staff.StaffDepartmentsQuery(request_query['_query'])
    assert query.modified_at == time_utils.NOW - datetime.timedelta(minutes=30)


@pytest.mark.now(time_utils.NOW.isoformat('T'))
@pytest.mark.config(
    EFFRAT_EMPLOYEES_PERSONAL_QUERYING_CONFIGURATION={'chunk_size': 1},
)
async def test_personal_chunk_restriction(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
):
    @mockserver.json_handler(f'/personal/v2/phones/bulk_store')
    async def personal_handler(request):
        return mockserver.make_response(
            status=200,
            json={
                'items': [
                    {'id': x['value'], 'value': x['value']}
                    for x in request.json['items']
                ],
            },
        )

    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(_):
        modified_at = time_utils.NOW
        response = [
            employee.create_employee(i).to_staff_response(modified_at)
            for i in range(10)
        ]
        return {'page': 1, 'links': {}, 'limit': 1, 'result': response}

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    for _ in range(len(_EMPLOYEES)):
        assert len(personal_handler.next_call()['request'].json['items']) == 1


async def test_bad_staff_response(
        taxi_effrat_employees,
        taxi_config,
        mockserver,
        department_context,
        mock_department,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def persons_handler(request):
        response = _EMPLOYEES[0].to_staff_response(time_utils.NOW)
        response.pop('uid')
        return {'page': 1, 'links': {}, 'limit': 1, 'result': [response]}

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher', 200)
    await persons_handler.wait_call()


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_500_callcenter_still_updates_staff(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
        generated_uuids,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _persons_handler(request):
        return {
            'page': 1,
            'links': {},
            'limit': 1,
            'result': [_EMPLOYEES[0].to_staff_response(time_utils.NOW)],
        }

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()

    await employee_fetcher_activate_task()

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1},
        headers={'Content-Type': 'application/json'},
    )
    utils.verify_response(response, [_EMPLOYEES[0]], generated_uuids)


async def test_supervisor_not_from_departments(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        department_context,
        mock_department,
        employee_fetcher_activate_task,
        generated_uuids,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _persons_handler(request):
        nonlocal emp
        return {
            'page': 1,
            'links': {},
            'limit': 1,
            'result': [emp.to_staff_response(time_utils.NOW)],
        }

    department.gen_staff_departments_config(taxi_config, 1)
    await taxi_effrat_employees.invalidate_caches()
    emp = employee.create_employee(
        0, supervisor=employee.create_supervisor(322),
    )

    await employee_fetcher_activate_task()

    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1},
        headers={'Content-Type': 'application/json'},
    )
    utils.verify_response(response, [emp], generated_uuids)


@pytest.mark.now(time_utils.NOW.isoformat('T'))
async def test_updated_at(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        mocked_time,
        department_context,
        mock_department,
        generated_uuids,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(request):
        query = staff.StaffDepartmentsQuery(request.query['_query'])
        result.append(query.departments[0])
        return {
            'page': 1,
            'links': {},
            'limit': 1,
            'result': [
                emp.to_staff_response(time_utils.NOW)
                for emp in filter(
                    lambda x: query.departments[0]
                    in map(lambda y: y.external_id, x.departments),
                    _employees,
                )
            ],
        }

    result = []
    _employees = [
        employee.create_employee(
            0, departments=department.generate_departments(0),
        ),
    ]
    staff_departments = [
        department.StaffDepartment(
            department.generate_department(0, 'Division'), 'taxi',
        ),
        department.StaffDepartment(
            department.generate_department(1, 'Division'), 'taxi',
        ),
    ]
    department.set_staff_departments_config(taxi_config, staff_departments)
    mocked_time.set(time_utils.NOW)
    await taxi_effrat_employees.invalidate_caches()
    for _ in range(4):
        await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
        mocked_time.set(mocked_time.now() + datetime.timedelta(minutes=1))
        await taxi_effrat_employees.invalidate_caches()
    assert result == [f'url_Division_{i%2}' for i in range(4)]


async def test_new_domain(
        taxi_effrat_employees,
        mockserver,
        taxi_config,
        mock_department,
        generated_uuids,
):
    @mockserver.json_handler('staff-for-wfm/v3/persons')
    async def _(request):
        nonlocal emp
        return {
            'page': 1,
            'links': {},
            'limit': 1,
            'result': [emp.to_staff_response(time_utils.NOW)],
        }

    dpt = department.StaffDepartment(
        department.generate_department(1), 'new_domain',
    )
    department.set_staff_departments_config(taxi_config, [dpt])
    await taxi_effrat_employees.invalidate_caches()
    emp = employee.create_employee(0, domain='new_domain')

    await cron.activate_task(taxi_effrat_employees, 'employee-fetcher')
    response = await taxi_effrat_employees.post(
        '/internal/v1/employees/index',
        json={'limit': 1},
        headers={'Content-Type': 'application/json'},
    )
    utils.verify_response(response, [emp], generated_uuids)
