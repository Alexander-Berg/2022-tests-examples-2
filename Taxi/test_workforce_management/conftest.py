# pylint: disable=redefined-outer-name
import collections
import copy
import typing as tp

import pytest

from test_workforce_management.web import util as test_util
import workforce_management.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from workforce_management.storage.postgresql import forecast

pytest_plugins = ['workforce_management.generated.service.pytest_plugins']


EFFRAT_EMPLOYEES = '/effrat-employees'
EMPLOYEES_LIST = f'{EFFRAT_EMPLOYEES}/internal/v1/employees/index'
START_DATE = '27-02-2020'

DEFAULT_EMPLOYEES_LIST: tp.List[tp.Dict] = [
    {
        'yandex_uid': 'uid1',
        'employee_uid': '00000000-0000-0000-0000-000000000001',
        'login': 'abd-damir',
        'staff_login': 'abd-damir',
        'departments': ['1'],
        'subdepartments': ['1', '2', '3'],
        'full_name': 'Abdullin Damir',
        'employment_status': 'in_staff',
        'phone_pd_id': '111',
        'supervisor_login': 'aladin227',
        'mentor_login': 'supervisor@unit.test',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['nokia', 'nokia2'],
        'source': 'taxi',
        'tags': ['naruto'],
        'organization': {'name': 'Google', 'country_code': 'vacanda'},
        'timezone': 'Europe/Saratov',
        'hr_ticket': 'some_ticket',
    },
    {
        'yandex_uid': 'uid2',
        'employee_uid': '00000000-0000-0000-0000-000000000002',
        'login': 'chakchak',
        'staff_login': 'chakchak',
        'departments': ['2'],
        'subdepartments': ['2', '3'],
        'full_name': 'Gilgenberg Valeria',
        'employment_status': 'in_staff',
        'supervisor_login': 'abd-damir',
        'created_at': '2020-07-21 00:00:00Z',
        'updated_at': '2020-07-21 00:00:00Z',
        'mentor_login': 'mentor@unit.test',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['nokia', 'nokia2'],
        'telegram_login_pd_id': 'vasya_iz_derevni',
        'source': 'taxi',
        'tags': ['naruto', 'driver'],
    },
    {
        'yandex_uid': 'uid3',
        'employee_uid': '00000000-0000-0000-0000-000000000003',
        'login': 'tatarstan',
        'staff_login': 'tatarstan',
        'departments': ['999'],
        'full_name': 'Minihanov Minihanov',
        'employment_status': 'in_staff',
        'supervisor_login': 'abd-damir',
        'created_at': '2020-07-21 00:00:00Z',
        'updated_at': '2020-07-21 00:00:00Z',
        'mentor_login': 'supervisor@unit.test',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['iphone', 'iphone2'],
        'telegram_login_pd_id': 'morozhenka',
        'source': 'taxi',
    },
    {
        'yandex_uid': 'not-existing',
        'employee_uid': 'deadbeef-0000-0000-0000-000000000000',
        'login': 'unknown',
        'staff_login': 'unknown',
        'departments': ['666'],
        'full_name': 'Anonymous Anonymous',
        'employment_status': 'in_staff',
        'supervisor_login': 'anonym222',
        'created_at': '2020-07-21 00:00:00Z',
        'updated_at': '2020-07-21 00:00:00Z',
        'mentor_login': 'supervisor@unit.test',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['super-role', 'super2'],
        'source': 'taxi',
    },
    {
        'yandex_uid': 'uid5',
        'employee_uid': '00000000-0000-0000-0000-000000000005',
        'login': 'deleted',
        'staff_login': 'deleted',
        'departments': ['666'],
        'full_name': 'Deleted Deleted',
        'employment_status': 'fired',
        'supervisor_login': 'anonym222',
        'created_at': '2020-07-21 00:00:00Z',
        'updated_at': '2020-07-21 00:00:00Z',
        'mentor_login': 'admin@unit.test',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['super-role'],
        'telegram_login_pd_id': 'Dota2Lover',
        'source': 'taxi',
    },
    {
        'yandex_uid': 'uid10',
        'employee_uid': '00000000-0000-0000-0000-000000000010',
        'login': 'kazimir_black_square',
        'staff_login': 'kazimir_black_square',
        'departments': ['1', 'avant-garde'],
        'full_name': 'Kazimir Malevich',
        'employment_status': 'preprofile_approved',
        'supervisor_login': 'tatarstan',
        'created_at': '2020-07-21 00:00:00Z',
        'updated_at': '2020-07-21 00:00:00Z',
        'mentor_login': 'admin@unit.test',
        'employment_datetime': '2020-07-21T00:00:00+03:00',
        'positions': ['artist'],
        'telegram_login_pd_id': 'alphabet',
        'source': 'taxi',
    },
]


PatchEffratEmployees = collections.namedtuple(
    'PatchEffratEmployees', ('employees_list',),
)

FIELD_MAPPER = {
    'callcenters': 'callcenter_id',
    'supervisors': 'supervisor_login',
    'roles': 'role_in_telephony',
    'states': None,
}


@pytest.fixture()
async def fill_forecast_values(web_context):

    db = forecast.ForecastRepo(web_context)

    revisions = []

    async def fill(count=2):
        async with db.master.acquire() as conn:
            for index in range(count):
                revision = await db.modify_forecast_entity(
                    conn,
                    record_id=index + 1,
                    forecast_type='hourly',
                    value_type='calls',
                    skill='skill' if index % 2 else 'not_a_skill',
                    name=f'Forecast {index}',
                    target_date=test_util.parse_and_make_step(
                        START_DATE, days=index,
                    ),
                    source='auto',
                    description='description',
                    domain='taxi',
                )

                revisions.append(revision)
                await db.modify_forecast_records(
                    conn,
                    records=[
                        {
                            'base_value': index + 200,
                            'plan_value': index + 200,
                            'lower_value': index + 100,
                            'upper_value': index + 1000,
                            'forecast_id': revision['id'],
                            'target_date': test_util.parse_and_make_step(
                                START_DATE,
                                hours=index + row_index,
                                days=index,
                            ),
                        }
                        for row_index in range(10)
                    ],
                )
        return revisions

    return fill


_KEYS_TO_DEPERSONALIZE = ['phone_pd_id', 'telegram_login_pd_id']

_PERSONAL_PREFIX = 'super_duper_secret_'


def _encode_entity(value: tp.Optional[str]) -> tp.Optional[str]:
    if value is None:
        return None
    return _PERSONAL_PREFIX + value


@pytest.fixture()
def mock_effrat_employees(mockserver):
    def patch_request(
            operators_list: tp.Optional[tp.List[tp.Dict]] = None,
            cursor: tp.Optional[int] = None,
    ):
        operators_list = operators_list or DEFAULT_EMPLOYEES_LIST

        @mockserver.json_handler(EMPLOYEES_LIST)
        def employees_list_handler(request, *args, **kwargs):
            response = copy.deepcopy(operators_list)
            for employee in response:
                for key in _KEYS_TO_DEPERSONALIZE:
                    if key in employee.keys():
                        employee[key] = _encode_entity(employee[key])
            return {'employees': response, 'cursor': cursor or '0'}

        return PatchEffratEmployees(employees_list=employees_list_handler)

    return patch_request


@pytest.fixture(autouse=True)
def mock_operators_cache(mock_effrat_employees):
    mock_effrat_employees([])


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override']['YT_CONFIG']['hahn'] = {
        'prefix': 'hahn',
        'token': 'test-token',
        'api_version': 'latest',
        'proxy': {'url': 'hahn.yt.yandex-team.ru'},
    }
    return simple_secdist


def _decode_entity(value: tp.Optional[str]) -> tp.Optional[str]:
    if value is None:
        return None
    return value[len(_PERSONAL_PREFIX) :]


def _decode_value(x):
    pd_id = x['id']
    return {'id': pd_id, 'value': _decode_entity(pd_id)}


def _decode_request(request):
    return {'items': [_decode_value(x) for x in request.json['items']]}


@pytest.fixture(autouse=True)
def mock_personal(mockserver):
    for data_type in ['phones', 'telegram_logins']:

        @mockserver.json_handler(f'/personal/v1/{data_type}/bulk_retrieve')
        async def _(request):
            return mockserver.make_response(
                status=200, json=_decode_request(request),
            )
