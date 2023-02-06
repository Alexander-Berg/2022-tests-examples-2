# pylint: disable=redefined-outer-name
import datetime
import functools
import json
import re
import typing

import aiohttp.web
import pytest

from taxi import config
from taxi.clients import tvm
from taxi.pytest_plugins import core

import hiring_partners_app.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301

pytest_plugins = ['hiring_partners_app.generated.service.pytest_plugins']


YA_CC_LINK = 'https://ya.cc/6_dCx'

ResponseType = core.Response

FILE_DATA_MARKUP = 'data_markup_response.json'
FILE_LEADS = 'hiring_candidates_leads.json'
FILE_PERMISSION_CREATE = 'permissions_create.json'
FILE_PERMISSION_FIND = 'requests.json'
FILE_PERMISSION_UPDATE = 'requests.json'
FILE_TARIFFS_CREATE = 'create_tariffs.json'
FILE_TARIFFS_UPDATE = 'update_tariffs.json'
FILE_USERS_CREATE = 'users_create.json'
FILE_USERS_UPDATE = 'users_update.json'

ROUTE_PERMISSION_CREATE = '/admin/v1/permission-groups/create'
ROUTE_PERMISSION_UPDATE = '/admin/v1/permission-groups/update'
ROUTE_PERMISSION_FIND = '/admin/v1/permission-groups'
ROUTE_TARIFF_CREATE = '/admin/v1/tariffs/create'
ROUTE_TARIFF_UPDATE = '/admin/v1/tariffs/update'
ROUTE_TARIFFS_GET = '/admin/v1/tariffs'
ROUTE_USER_CREATE_ADMIN = '/admin/v1/users/account/create'
ROUTE_USER_UPDATE_ADMIN = '/admin/v1/users/account/update'
ROUTE_USERS_LIST = '/admin/v1/users/list'

TARIFF_SKIP_CHECK_FIELDS_CREATE = ['id', 'created_at']
TARIFF_SKIP_CHECK_FIELDS_UPDATE = [
    *TARIFF_SKIP_CHECK_FIELDS_CREATE,
    'started_at',
]

PHONES_MATCH = {
    '+79998887766': '1104248e26074dd88e46f350037459fa',
    '+79998887782': 'be5da8c4f4c741afa8887c41502c441b',
    '1104248e26074dd88e46f350037459fa': '+79998887766',
    'be5da8c4f4c741afa8887c41502c441b': '+79998887782',
    '+79999999999': None,
}
LICENSES_MATCH = {
    '12AT123456': '1104248e26074dd88e46f350037459fa',
    '1104248e26074dd88e46f350037459fa': '12AT123456',
}
YANDEX_LOGINS_MATCH = {
    'yandexlogin_agent': 'a95c01defa9d4909910e084cbdabecca',
    'yandexlogin_scout': 'jr2r8gudfghlfdskmi9u322104re3fiw',
    'yandexlogin_admin': 'j9r2jgig92if32hfdsfh8fh2u23uh328',
    'yet_another_user': 'nfjew9r3i9rnfdv934u843ry8hr89gh9',
    'fake_user': 'wd13rg5gttjregr4r2rfsfdfdsfd',
    'yandexlogin_user_v1': 'YANDEXLOGIN_USER_V1',
    'yandexlogin_user_v2': 'YANDEXLOGIN_USER_V2',
    'yandexlogin_user_domestic_v1': 'YANDEXLOGIN_USER_DOMESTIC_V1',
    'yandexlogin_user_international_v1': 'YANDEXLOGIN_USER_INTERNATIONAL_V1',
    'yandexlogin_user_not_active': 'YANDEXLOGIN_USER_NOT_ACTIVE',
    'yandexlogin_new': 'YANDEXLOGIN_NEW',
}

PERSONAL_NULL_RESPONSE = {
    'code': '400',
    'message': 'Field \'value\' is of a wrong type...',
}


@pytest.fixture  # noqa: F405
def make_hiring_partners_request(taxi_hiring_partners_app_web):
    async def func(
            route,
            *,
            method='post',
            data=None,
            params=None,
            headers=None,
            status_code=200,
            response_body=None,
    ):
        response: ResponseType
        method = getattr(taxi_hiring_partners_app_web, method)
        response = await method(
            route, json=data, params=params, headers=headers,
        )
        assert response.status == status_code
        body = await response.json()
        if response_body:

            body = await response.json()
            assert body == response_body
        return body

    return func


@functools.lru_cache(None)
def personal_response(type_, id_):
    if type_ == 'license':
        value = LICENSES_MATCH[id_]
    elif type_ == 'license_id':
        value = id_
        id_ = LICENSES_MATCH[value]
    elif type_ == 'phone':
        value = PHONES_MATCH[id_]
    elif type_ == 'phone_id':
        value = id_
        id_ = PHONES_MATCH[value]
    elif type_ == 'login_id':
        value = id_
        id_ = YANDEX_LOGINS_MATCH[value]
    else:
        raise ValueError
    return {'value': value, 'id': id_}


@pytest.fixture  # noqa: F405
def personal(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def retrieve_phones(request):
        return personal_response('phone', request.json['id'])

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def retrieve_licenses(request):
        return personal_response('license', request.json['id'])

    @mockserver.json_handler('/personal/v1/phones/store')
    def store_phones(request):
        value = request.json['value']
        if not value or not re.match(r'^\+\d+$', value):
            return mockserver.make_response(
                json=PERSONAL_NULL_RESPONSE, status=400,
            )
        return personal_response('phone_id', value)

    @mockserver.json_handler('/personal/v1/yandex_logins/store')
    def store_yandex_logins(request):
        value = request.json['value']
        if not value:
            return mockserver.make_response(
                json=PERSONAL_NULL_RESPONSE, status=400,
            )
        return personal_response('login_id', value)

    # pylint: disable=unused-variable
    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def store_licenses(request):
        value = request.json['value']
        if not value:
            return mockserver.make_response(
                json=PERSONAL_NULL_RESPONSE, status=400,
            )
        return personal_response('license_id', value)


@pytest.fixture
def mock_personal_api(mockserver):
    @mockserver.json_handler(
        r'/personal/v1/(?P<personal_type>[a-z_]+)/store', regex=True,
    )
    def _store(request, personal_type):
        # personal_type is one of (phones, driver_licenses, yandex_logins...)
        value: str = request.json['value']
        if value == '*&*^%$%^':
            return {}, 400
        prefix = personal_type[:-1].replace('_', '')
        if value.startswith(prefix):
            assert value.islower()
            return {'id': value.upper(), 'value': value}
        return {'id': '14139b62ad34493eb2a87ed19863cccc', 'value': value}

    @mockserver.json_handler(
        r'/personal/v1/(?P<personal_type>[a-z_]+)/retrieve', regex=True,
    )
    def _retrieve(request, personal_type):
        personal_id: str = request.json['id']
        return {'id': personal_id, 'value': personal_id.lower()}

    @mockserver.json_handler(
        r'/personal/v1/(?P<personal_type>[a-z_]+)/bulk_store', regex=True,
    )
    def _bulk_store(request, personal_type):
        items: typing.List[dict] = request.json['items']
        prefix = personal_type[:-1].replace('_', '')
        result = []
        for item in items:
            value = item['value']
            if value.startswith(prefix):
                assert value.islower()
                result.append({'id': value.upper(), 'value': value})
        return {'items': result}

    @mockserver.json_handler(
        r'/personal/v1/(?P<personal_type>[a-z_]+)/bulk_retrieve', regex=True,
    )
    def _bulk_retrieve(request, personal_type):
        items: typing.List[dict] = request.json['items']
        prefix = personal_type[:-1].replace('_', '')
        result = []
        for item in items:
            value = item['id']
            if value.startswith(prefix):
                assert value.islower()
                result.append({'id': value.upper(), 'value': value})
        return {'items': result}


@pytest.fixture
def mock_data_markup(mockserver, load_json):
    @mockserver.json_handler('/hiring-data-markup/v1/experiments/perform')
    def _markup_user(request):
        return load_json(FILE_DATA_MARKUP)['hiring_partners_app_lead_markup']


@pytest.fixture
def mock_data_markup_factory(mockserver, load_json):
    def _wrapper(expected=None):
        @mockserver.json_handler('/hiring-data-markup/v1/experiments/perform')
        def _data_markup(request):
            return expected

        return _data_markup

    return _wrapper


@pytest.fixture
def mock_partners_taximeter(mock_taximeter_admin):
    def _wrapper(expected):
        @mock_taximeter_admin('/api/support/newdriver')
        async def _taximeter(request):
            if not expected:
                return {}
            return {'DriverId': expected, 'Id': 'ID', 'ParkId': 'PARK_ID'}

        return _taximeter

    return _wrapper


@pytest.fixture
def mock_ya_cc(mockserver):
    storage = {'response': [YA_CC_LINK, False]}

    @mockserver.json_handler('/ya-cc/--')
    def _store_yandex_login(_):
        return aiohttp.web.Response(
            headers={'Content-Type': 'text/javascript; charset=utf-8'},
            text=json.dumps(storage['response']),
        )

    return storage


@pytest.fixture  # noqa: F405
def tariff_create(make_hiring_partners_request, load_json):
    async def func(request_type='valid', case='valid'):
        data = load_json(FILE_TARIFFS_CREATE)[request_type][case]
        for task in data:
            request_body = task['request']
            status_code = task['response']['status_code']
            result = await make_hiring_partners_request(
                ROUTE_TARIFF_CREATE,
                data=request_body,
                status_code=status_code,
            )
            if status_code == 200:
                response_body = task['response']['body']['tariffs'][0]
                tariff = result['tariffs'][0]
                for key, value in tariff.items():
                    if key not in TARIFF_SKIP_CHECK_FIELDS_CREATE:
                        assert response_body[key] == value

    return func


@pytest.fixture  # noqa: F405
def tariffs_fetch(make_hiring_partners_request):
    async def func(tariff_name=None, status_code=200):
        params = None
        if tariff_name:
            params = {'tariff_name': tariff_name}
        return await make_hiring_partners_request(
            route=ROUTE_TARIFFS_GET,
            method='get',
            params=params,
            status_code=status_code,
        )

    return func


@pytest.fixture  # noqa: F405
def tariff_update(
        make_hiring_partners_request, load_json, tariff_create, tariffs_fetch,
):
    async def func(request_type, case):
        tasks = load_json(FILE_TARIFFS_UPDATE)[request_type][case]
        for task in tasks:
            request_body = task['request']
            status_code = task['response']['status_code']
            result = await make_hiring_partners_request(
                ROUTE_TARIFF_UPDATE,
                data=request_body,
                status_code=status_code,
            )
            if status_code == 200:
                assert result['tariffs']
                updates = task['response']['check']
                for key, value in updates.items():
                    assert result['tariffs'][0][key] == value

    return func


def _check_users(task, users):
    login_id = task['response']['body']['yandex_login']
    new_user = next(
        (
            user
            for user in users['users']
            if user['personal_yandex_login_id'] == login_id.upper()
        ),
        None,
    )
    assert new_user
    assert new_user.items() >= task['response']['user'].items()


@pytest.fixture  # noqa: F405
def user_create(make_hiring_partners_request, load_json, users_list):
    async def func(request_type='valid', case='default'):
        data = load_json(FILE_USERS_CREATE)[request_type][case]
        route = ROUTE_USER_CREATE_ADMIN
        for task in data:
            status_code = task['response']['status_code']
            await make_hiring_partners_request(
                route,
                headers=task['headers'],
                data=task['request'],
                status_code=status_code,
                response_body=task['response']['body'],
            )
            if status_code >= 400:
                return
            users = await users_list()
            _check_users(task, users)

    return func


@pytest.fixture  # noqa: F405
def user_update_admin(
        make_hiring_partners_request,
        user_create,
        load_json,
        users_list,
        pgsql,
):
    async def func(request_type='valid', case='default'):
        if request_type != 'valid':
            await user_create()
        else:
            await user_create(request_type, case)
        data = load_json(FILE_USERS_UPDATE)[request_type][case]
        for task in data:
            status_code = task['response']['status_code']
            await make_hiring_partners_request(
                ROUTE_USER_UPDATE_ADMIN,
                headers=task['headers'],
                data=task['request'],
                status_code=status_code,
                response_body=task['response']['body'],
            )
            if status_code >= 400:
                return
            users = await users_list()
            _check_users(task, users)
            # check idempotency
            await make_hiring_partners_request(
                ROUTE_USER_UPDATE_ADMIN,
                headers=task['headers'],
                data=task['request'],
                status_code=200,
                response_body=task['response']['body'],
            )

    return func


@pytest.fixture  # noqa: F405
def users_list(make_hiring_partners_request):
    async def func():
        now = datetime.datetime.utcnow()
        return await make_hiring_partners_request(
            ROUTE_USERS_LIST,
            data={
                'created_at_gt': str(now - datetime.timedelta(days=10)),
                'created_at_lte': str(now + datetime.timedelta(days=10)),
            },
        )

    return func


@pytest.fixture  # noqa: F405
def get_superuser(make_hiring_partners_request):
    async def func():
        return await make_hiring_partners_request(
            ROUTE_USERS_LIST,
            data={
                'created_at_gt': '2030-08-09T13:00:00',
                'created_at_lte': '2030-08-10T13:00:00',
            },
        )

    return func


@pytest.fixture  # noqa: F405
def permissions_create_or_update(
        make_hiring_partners_request, load_json, permissions_list,
):
    async def func(request_type='valid', case='default', kind='create'):
        file = FILE_PERMISSION_CREATE
        route = ROUTE_PERMISSION_CREATE
        if kind == 'update':
            file = FILE_PERMISSION_UPDATE
            route = ROUTE_PERMISSION_UPDATE
        data = load_json(file)[request_type][case]
        for task in data:
            status_code = task['response']['status_code']
            response = await make_hiring_partners_request(
                route,
                headers=task['headers'],
                data=task['request'],
                status_code=status_code,
                response_body=task['response']['body'],
            )
            if status_code >= 400:
                return
            permissions = await permissions_list()
            default = None
            for permission in permissions['permissions']:
                if permission['is_default_for_organization']:
                    assert default is None
                    default = permission['id']
            if task['request'].get('is_default_for_organization'):
                assert response['permissions'][0]['id'] == default
            else:
                assert response['permissions'][0]['id'] != default

    return func


@pytest.fixture  # noqa: F405
def permissions_list(make_hiring_partners_request, load_json):
    async def func(request_type=None, case=None):
        if not request_type and not case:
            return await make_hiring_partners_request(
                ROUTE_PERMISSION_FIND,
                method='get',
                headers={'X-Yandex-Login': 'Some'},
            )
        tasks = load_json(FILE_PERMISSION_FIND)[request_type][case]
        for task in tasks:
            await make_hiring_partners_request(
                ROUTE_PERMISSION_FIND,
                method='get',
                headers=task['headers'],
                params=task['params'],
                response_body=task['response']['body'],
            )

    return func


class CandidatesContext:
    def __init__(self):
        self.iter = 1

    @property
    def return_iter(self):
        result = self.iter % 2
        self.iter += 1
        if result == 0:
            return 2
        return result


@pytest.fixture
def candidates_context():
    return CandidatesContext()


@pytest.fixture
def mock_hiring_candidates_py3(mockserver, candidates_context, load_json):
    @mockserver.json_handler('/hiring-candidates-py3/v1/leads/list')
    def _handler(request):
        key = 'ITER_{}'.format(candidates_context.return_iter)
        return load_json(FILE_LEADS)['valid'][key]


@pytest.fixture
def mock_candidates_v1_leads_list(mockserver):
    def _wrapper(response, status=200):
        @mockserver.json_handler('/hiring-candidates-py3/v1/leads/list')
        async def _handler(request):
            return aiohttp.web.json_response(response, status=status)

        return _handler

    return _wrapper


@pytest.fixture
def mock_hiring_api_v2_leads_create(mockserver, mock_hiring_api):
    def _wrapper(response, status=200):
        @mock_hiring_api('/v2/leads/create')
        async def _handler(request):
            return aiohttp.web.json_response(response, status=status)

        return _handler

    return _wrapper


# pylint: disable=C0103
@pytest.fixture
def mock_hiring_api_external_v2_leads_create(mockserver, mock_hiring_api):
    def _wrapper(response, status=200):
        @mock_hiring_api('/external/v2/leads/create')
        async def _handler(request):
            return aiohttp.web.json_response(response, status=status)

        return _handler

    return _wrapper


@pytest.fixture
def mock_hiring_api_v1_lead_act(mockserver, mock_hiring_api):
    def _wrapper(response, status=200):
        @mock_hiring_api('/v1/lead/activate')
        async def _handler(request):
            return aiohttp.web.json_response(response, status=status)

        return _handler

    return _wrapper


@pytest.fixture
def tvm_client(simple_secdist, patch):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    return tvm.TVMClient(
        service_name='hiring-partners-app',
        secdist=simple_secdist,
        config=config,
        session=None,
    )


@pytest.fixture
def request_leads_activation_list(taxi_hiring_partners_app_web):
    async def _wrapper(request: str, user_login: str, status_code: int = 200):
        response = await taxi_hiring_partners_app_web.post(
            '/v1/leads/activation-list',
            json=request,
            headers={tvm.YANDEX_LOGIN_HEADER: user_login},
        )
        assert response.status == status_code
        return await response.json()

    return _wrapper


@pytest.fixture
def mock_personal(mockserver):
    @mockserver.json_handler('/personal/v1/yandex_logins/store')
    async def _yandex_logins_store(request):
        value = request.json['value']
        return {'id': value + '_pd_id', 'value': value}

    @mockserver.json_handler('/personal/v1/yandex_logins/retrieve')
    async def _yandex_logins_retrieve(request):
        pd_id = request.json['id']
        value = pd_id[0 : pd_id.find('_pd_id')]
        return {'id': pd_id, 'value': value}


@pytest.fixture
def mock_configs3(mockserver):
    def wrapper(response):
        @mockserver.json_handler('/experiments3/v1/configs')
        def handler(request):
            return response

        return handler

    return wrapper


@pytest.fixture
def mock_user_permissions(mock_configs3):
    def wrapper(permission_flags):
        return mock_configs3(
            {
                'items': [
                    {
                        'name': 'hiring_partners_app_permission_flags',
                        'value': {'permission_flags': permission_flags},
                    },
                ],
            },
        )

    return wrapper
