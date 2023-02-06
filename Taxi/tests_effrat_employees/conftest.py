# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import copy
import datetime
import operator
import re
import typing as tp

import pytest

from effrat_employees_plugins import *  # noqa: F403 F401

from tests_effrat_employees import cron
from tests_effrat_employees import department
from tests_effrat_employees import generated_uuids
from tests_effrat_employees import personal


__PREDICATES = {
    '<': operator.lt,
    '>': operator.gt,
    '<=': operator.le,
    '>=': operator.ge,
    '==': operator.eq,
    '!=': operator.ne,
}


def _parse_datetime(strstamp):
    return datetime.datetime.strptime(strstamp, '%Y-%m-%dT%H:%M:%S.%f%z')


@pytest.fixture(autouse=True)
def mock_staff(mockserver):
    @mockserver.json_handler('/callcenter-operators/v1/operators/list')
    def _(_):
        return mockserver.make_response(
            status=200, json={'next_cursor': 0, 'operators': []},
        )


@pytest.fixture(autouse=True)
def mock_callcenter_callcenters(mockserver):
    @mockserver.json_handler('/callcenter-operators/v2/admin/callcenters/')
    async def _(_):
        def generate_callcenter(index: int) -> tp.Dict[str, tp.Any]:
            dep = department.generate_departments(index)[0]
            return {
                'id': dep.external_id,
                'name': dep.name,
                'domain': 'dummy',
                'staff_login_required': False,
                'timezone': 'Europe/Moscow',
            }

        return mockserver.make_response(
            status=200,
            json={'callcenters': [generate_callcenter(i) for i in range(9)]},
        )


@pytest.fixture(autouse=True)
def mock_callcenter_operators(mockserver):
    @mockserver.json_handler('/staff-for-wfm/v3/persons')
    async def _(_):
        return {'page': 1, 'links': {}, 'limit': 1, 'result': []}


@pytest.fixture(autouse=True)
def mock_staff_groups(mockserver):
    @mockserver.json_handler('/staff-for-wfm/v3/groups')
    async def _(_):
        return {'page': 1, 'links': {}, 'limit': 1, 'result': []}


@pytest.fixture(autouse=True)
def mock_staff_organizations(mockserver, load_json):
    @mockserver.json_handler('/staff-for-wfm/v3/organizations')
    async def _(request):
        fields = request.query['_fields'].split(',')
        fields.sort()
        assert fields == [
            '_meta.modified_at',
            'country_code',
            'created_at',
            'id',
            'name',
        ]
        response_raw = load_json('staff_v3_organizations_response.json')
        if '_query' not in request.query:
            return response_raw

        regex = re.compile(r'_meta.modified_at([<>=]=)"([^"]+)"')
        match = regex.findall(request.query['_query'])

        predicate = __PREDICATES.get(match[0][0])
        assert predicate is not None
        modified_at = _parse_datetime(match[0][1])

        result = response_raw.pop('result')
        response = copy.deepcopy(response_raw)
        response['result'] = []
        for org in result:
            meta = org['_meta']
            lookup_modified_at = _parse_datetime(meta['modified_at'])
            if predicate(lookup_modified_at, modified_at):
                response['result'].append(org)

        response['total'] = len(response['result'])
        return response


@pytest.fixture(autouse=True)
def mock_adopt_operators(mockserver):
    @mockserver.json_handler(
        '/staff-preprofile/preprofile-api/export/helpdesk',
    )
    async def _(request):
        return []


def _encode_value(x):
    value = x['value']
    return {'value': value, 'id': personal.encode_entity(value)}


def _encode_request(request):
    return {'items': [_encode_value(x) for x in request.json['items']]}


@pytest.fixture(autouse=True)
def mock_personal(mockserver):
    for data_type in ['phones', 'telegram_logins', 'emails']:

        @mockserver.json_handler(f'/personal/v2/{data_type}/bulk_store')
        async def _(request):
            return mockserver.make_response(
                status=200, json=_encode_request(request),
            )


# pylint: disable=redefined-outer-name
class Context:
    def __init__(self):
        self.data = []

    def set_data(self, data):
        self.data = data


@pytest.fixture
def department_context():
    return Context()


@pytest.fixture
def mock_department(mockserver, department_context):
    class Mocks:
        @mockserver.json_handler('/staff-for-wfm/v3/departmentstaff')
        @staticmethod
        async def foo_handler(request):
            department_url = request.query['department_group.url']
            response_department = list(
                filter(
                    lambda x: department_url == x.department.external_id,
                    department_context.data,
                ),
            )
            if response_department:
                res = [
                    {
                        'department_group': {
                            'url': response_department[
                                0
                            ].department.external_id,
                            'name': response_department[0].department.name,
                        },
                    },
                ]
            else:
                res = []
            return {'page': 1, 'links': {}, 'limit': 1, 'result': res}

    return Mocks()


async def _cron_activate_task(
        taxi_effrat_employees, testpoint, testpoint_name, cron_task_name,
):
    @testpoint(testpoint_name)
    def handler(data):
        pass

    await taxi_effrat_employees.invalidate_caches()

    async def _activate_task():
        await cron.activate_task(taxi_effrat_employees, cron_task_name)
        await handler.wait_call()

    return _activate_task


@pytest.fixture
async def employee_fetcher_activate_task(taxi_effrat_employees, testpoint):
    return await _cron_activate_task(
        taxi_effrat_employees,
        testpoint,
        'employee-fetcher-done',
        'employee-fetcher',
    )


@pytest.fixture
async def tags_ttl_actlzr_activate_task(taxi_effrat_employees, testpoint):
    return await _cron_activate_task(
        taxi_effrat_employees,
        testpoint,
        'tags-ttl-actualizer-done',
        'tags-ttl-actualizer',
    )


@pytest.fixture
async def oracle_timezone_activate_task(taxi_effrat_employees, testpoint):
    return await _cron_activate_task(
        taxi_effrat_employees,
        testpoint,
        'oracle-timezone-importer-done',
        'oracle-timezone-importer',
    )


@pytest.fixture
async def synched_gen_staff_dpts_config(taxi_effrat_employees, testpoint):
    async def _gen_departments_config(taxi_config, number: int):
        @testpoint('staff-departments-actualizer-done')
        def handler(data):
            pass

        # invalidate caches for update enabled testpoints list
        await taxi_effrat_employees.invalidate_caches()

        department.gen_staff_departments_config(taxi_config, number)
        # invalidate caches for update configs
        await taxi_effrat_employees.invalidate_caches()
        await handler.wait_call()

    return _gen_departments_config


@pytest.fixture(name='generated_uuids', autouse=True)
def _generated_uuids(testpoint):
    uuid_gen = generated_uuids.GeneratedUuids()

    @testpoint('generated-uuid')
    def _handler(data):
        uuid_gen.register_uuid(data['identifier'], data['uuid'])

    return uuid_gen
