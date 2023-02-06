# pylint: disable=redefined-outer-name
# pylint: disable=too-many-lines
import contextlib
import copy
import dataclasses
import inspect
import typing

from aiohttp import abc
from aiohttp import web
import bson
import pytest

from taxi.clients import tvm
from taxi.pytest_plugins import service

from taxi_corp import app_stq
from taxi_corp import config
from test_taxi_corp import load_util

DELETE_FIELD = object()

SETTINGS_OVERRIDE = {
    'CORP_CRM_TOKEN': '',
    'DADATA_TOKEN': '',
    'YQL_TOKEN': '',
    'YT_CONFIG': {
        'hahn': {
            'prefix': '//home/taxi/',
            'proxy': {'url': 'hahn.yt.yandex.net'},
        },
    },
}

pytest_plugins = ['taxi.pytest_plugins.stq_agent']


def pytest_configure(config):
    config.addinivalue_line('markers', 'settings: settings')


@pytest.fixture
async def taxi_corp_app_stq(loop, db, simple_secdist):
    app = app_stq.TaxiCorpSTQApplication(loop=loop, db=db)
    await app.startup()
    yield app
    await app.shutdown()


@pytest.fixture
def settings_patcher(monkeypatch):
    def patcher(**kwargs):
        for config_key, value in kwargs.items():
            monkeypatch.setattr(
                'taxi_corp.settings.{}'.format(config_key), value,
            )

    return patcher


@pytest.fixture
def config_patcher(monkeypatch):
    def patcher(**kwargs):
        for config_key, value in kwargs.items():
            monkeypatch.setattr(
                'taxi_corp.config.Config.{}'.format(config_key), value,
            )

    return patcher


@pytest.fixture(autouse=True)
def _config(request, config_patcher, configs_mock):
    all_kwargs = {}
    markers = request.node.iter_markers('config')
    for marker in markers:
        all_kwargs.update(marker.kwargs)
    if all_kwargs:
        config_patcher(**all_kwargs)


@pytest.fixture(autouse=True)
def _settings(request, settings_patcher):
    all_kwargs = {}
    markers = request.node.iter_markers('settings')
    for marker in markers:
        all_kwargs.update(marker.kwargs)
    if all_kwargs:
        settings_patcher(**all_kwargs)


@pytest.fixture
def simple_secdist(simple_secdist):
    simple_secdist['settings_override'].update(SETTINGS_OVERRIDE)
    return simple_secdist


@pytest.fixture()
def autotranslations(monkeypatch):
    def _get_string(self, key, language, num=None):
        items = [key]
        if language != 'ru':
            items.append(language)
        if num is not None:
            items.append(num)
        return ' '.join(items)

    monkeypatch.setattr(
        'taxi.translations.TranslationBlock.get_string', _get_string,
    )


@pytest.fixture
def passport_mock(patch, request):
    param = getattr(request, 'param', 'default')

    if isinstance(param, list):
        prefix = param[0]
        attributes = param[1] if len(param) > 1 else None
    else:
        prefix = param
        attributes = None

    if prefix is None:
        return None

    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args, **kwargs):

        res = {
            'uid': '{}_uid'.format(prefix),
            'login': '{}_login'.format(prefix),
        }

        if attributes is not None:
            res.update(attributes)

        return res

    return prefix


@pytest.fixture
def passport_mock_with_call_checks(patch, request):
    class PassportNoMock:
        prefix = None

    param = getattr(request, 'param', 'default')

    if isinstance(param, list):
        mock_prefix = param[0]
        attributes = param[1] if len(param) > 1 else None
    else:
        mock_prefix = param
        attributes = None

    if mock_prefix is None:
        return PassportNoMock()

    class PassportMock:
        prefix = mock_prefix

        @staticmethod
        @patch('taxi.clients.passport.get_passport_info')
        async def get_passport_info(*args, **kwargs):

            res = {
                'uid': '{}_uid'.format(mock_prefix),
                'login': '{}_login'.format(mock_prefix),
            }

            if attributes is not None:
                res.update(attributes)

            return res

    return PassportMock()


@pytest.fixture
def client(request):
    """
    Provide multiple clients. Only for indirect case.

    Usage:
    >>> @pytest.mark.parametrize(
    >>>     'client',
    >>>     ['taxi_corp_auth_client', 'taxi_corp_tvm_client'],
    >>>     indirect=['client'],
    >>> )
    """
    return request.getfixturevalue(request.param)


@pytest.fixture
def acl_access_data_patch(patch, request, load_json):
    @patch('taxi_corp.api.acl.get_access_data')
    async def _get_access_data(*args, **kwargs):
        from taxi_corp.api import acl
        perms_by_role = load_json('access_data_permissions_by_role.json')
        return getattr(
            request,
            'param',
            acl.AccessData(
                yandex_uid='0',
                role='client',
                client_id='client_id',
                department_id=None,
                permissions=perms_by_role['client'],
            ),
        )


@pytest.fixture
def access_data_mock(mockserver, load_json):
    class AccessDataMock:
        @staticmethod
        @mockserver.json_handler('/corp-managers/v1/managers/access-data')
        def corp_managers_access_data(request):
            yandex_uid = request.query['yandex_uid']
            access_data = load_util.load_access_data(load_json, yandex_uid)
            if access_data is not None:
                role = access_data['role']
                return mockserver.make_response(
                    json={
                        'role': role,
                        'roles': [role],
                        'permissions': access_data['permissions'],
                        'client_id': access_data['client_id'],
                        'department_id': access_data.get('department_id'),
                    },
                    status=200,
                )

            return mockserver.make_response(json={}, status=404)

    return AccessDataMock()


@pytest.fixture
def save_to_history_mock(monkeypatch):
    def _save_to_history_mock(func):
        return func

    monkeypatch.setattr(
        'taxi_corp.internal.decorators.save_to_history', _save_to_history_mock,
    )


@pytest.fixture(autouse=True)
def _deprecated_time_context(patch):
    @patch('taxi.util.context_timings.time_context')
    @contextlib.contextmanager
    def _time_context(scope_name):
        if 'db.' in scope_name:
            raise Exception('misuse time_context for db: ' + scope_name)
        yield

    @patch('taxi.util.aiohttp_kit.api.log_time_storage')
    def _log_time_storage(*args, **kwargs):
        pass


@pytest.fixture(autouse=True)
def _translations_mock(patch):
    @patch('taxi.translations.Translations.refresh_cache')
    async def _refresh_cache(*args, **kwargs):
        pass


@pytest.fixture
def acl_mock(patch):
    @patch('taxi_corp.api.acl.predicates.ConditionPredicate.__call__')
    async def _function_predicate(*args):
        return True

    @patch('taxi_corp.api.acl.predicates.PermissionPredicate.__call__')
    async def _roles_predicate(*args):
        return True

    @patch('taxi.clients.passport.get_passport_info')
    async def _get_passport_info(*args):
        return {'uid': 0, 'login': 'login', 'is_staff': False}


@pytest.fixture
def taxi_corp_mock_auth(patch, acl_mock):
    @patch('taxi.util.aiohttp_kit.middleware.auth_middleware')
    def _auth_middleware(skip_paths):
        @web.middleware
        async def _auth_middleware_mock(request, handler):
            return await handler(request)

        return _auth_middleware_mock

    @patch('taxi.clients.passport.PassportClient._request_bb_method')
    async def _request_bb_method(
            method, user_ip, log_extra=None, **passport_params,
    ):
        raise AssertionError(
            'direct blackbox access is prohibited'
            '(mock around PassportClient._request_bb_method)',
        )


@pytest.fixture
async def taxi_corp_auth_app(
        loop,
        db,
        mongodb_init,
        simple_secdist,
        autotranslations,
        territories_mock,
        access_data_mock,
):
    from taxi_corp import app as corp_app
    from taxi_corp import settings

    settings.DEBUG = False

    app = await corp_app.init_app(loop=loop)
    app.access_data_mock = access_data_mock
    yield app
    # if use app without test_client
    if not app.frozen:
        app.freeze()
        await app.shutdown()


@pytest.fixture
async def meta_app_version_mock(monkeypatch):
    from taxi_corp import corp_web

    @property
    def _meta_app_version(self):
        return '1'

    monkeypatch.setattr(
        corp_web.Request, 'meta_app_version', _meta_app_version,
    )


@pytest.fixture
async def taxi_corp_auth_client(
        aiohttp_client,
        taxi_corp_mock_auth,  # order is important
        save_to_history_mock,
        taxi_corp_auth_app,
):
    return await aiohttp_client(taxi_corp_auth_app)


@pytest.fixture
async def taxi_corp_real_auth_client(
        aiohttp_client, taxi_corp_auth_app, meta_app_version_mock,
):
    return await aiohttp_client(taxi_corp_auth_app)


@pytest.fixture
async def taxi_corp_tvm_client(
        patch, aiohttp_client, taxi_corp_auth_app, meta_app_version_mock,
):
    @patch('taxi.clients.tvm.check_tvm')
    async def _check_tvm(*args, **kwargs):
        return tvm.CheckResult(src_service_name='external_service')

    return await aiohttp_client(taxi_corp_auth_app)


@pytest.fixture
async def taxi_corp_authproxy_client(
        patch, aiohttp_client, taxi_corp_auth_app,
):
    @patch('taxi.clients.tvm.check_tvm')
    async def _check_tvm(*args, **kwargs):
        return tvm.CheckResult(src_service_name='corp-authproxy')

    return await aiohttp_client(taxi_corp_auth_app)


def _patch_doc(base_doc: dict, template: dict) -> dict:
    """
    The function updates the base document in a predetermined pattern.
    The template is a dictionary. The key can be written through the point.
    If the value is specified None, then this field is deleted.

    Example:
        >>> base = {
        ...             'foo': {
        ...                 'bar': {
        ...                     'a': 1,
        ...                     'b': 2
        ...                 }
        ...             }
        ...         }
        >>> _patch_doc(base, {'foo.bar.a': 42, 'foo.bar.b': None})
        {'foo': {'bar': {'a': 42}}}
    """
    result = copy.deepcopy(base_doc)
    for key, value in template.items():
        doc = result
        keys = key.split('.')
        for part in keys[:-1]:
            doc = doc[part]
        if DELETE_FIELD == value:
            del doc[keys[-1]]
        else:
            doc[keys[-1]] = value
    return result


@pytest.fixture
def patch_doc():
    return _patch_doc


@pytest.fixture(autouse=True)
def mock_handle_error(patch):
    from taxi_corp.api.middlewares import _handle_error as orig_handle_error

    @patch('taxi_corp.api.middlewares._handle_error')
    def _handle_error(error, exception, request):
        if isinstance(error, web.HTTPInternalServerError):
            raise exception

        return orig_handle_error(error, exception, request)


@pytest.fixture
async def access_client(patch, taxi_corp_auth_app, aiohttp_client):
    """
    Client for checking access rules.
    Skip swagger validation and all handlers return empty dict
    """
    # pylint: disable=protected-access
    from taxi_corp.api import acl
    from taxi_corp.api.handlers.base import base_handler

    for route in taxi_corp_auth_app.router.routes():
        if not inspect.isclass(route._handler):
            handler = route._handler
        elif issubclass(route._handler, base_handler.BaseHandler):
            handler = route._handler.handle_request
        elif issubclass(route._handler, abc.AbstractView):
            handler = getattr(route._handler, route.method.lower(), None)
            if not handler:
                continue
        else:
            handler = route._handler

        async def _handler(*args, **kwargs):
            return web.json_response({})

        if hasattr(handler, 'access_meta'):
            _handler = acl.access(handler.access_meta)(_handler)

            route._handler = _handler

    return await aiohttp_client(taxi_corp_auth_app)


@pytest.fixture
def tvm_client(simple_secdist, aiohttp_client, patch):
    @patch('taxi.clients.tvm.TVMClient.get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {tvm.TVM_TICKET_HEADER: 'ticket'}

    return tvm.TVMClient(
        service_name='corp-cabinet',
        secdist=simple_secdist,
        config=config,
        session=aiohttp_client,
    )


@pytest.fixture
def pd_patch(patch):
    @patch('taxi.clients.personal.PersonalApiClient.store')
    async def _store(data_type, request_value, *args, **kwargs):
        return {'id': 'pd_id'}

    @patch('taxi.clients.personal.PersonalApiClient.bulk_store')
    async def _bulk_store(data_type, request_values, *args, **kwargs):
        return [{'id': 'pd_id'} for _ in request_values]

    @patch('taxi.clients.personal.PersonalApiClient.bulk_retrieve')
    async def _retrieve(data_type, request_values, *args, **kwargs):
        return [
            {'id': phone_id, 'phone': _hex_to_phone(phone_id)}
            for phone_id in request_values
        ]

    @patch('taxi.clients.user_api.UserApiClient.get_user_phone_bulk')
    async def _get_user_phone_bulk(phone_ids, *args, **kwargs):
        return [
            {'id': phone_id, 'phone': _hex_to_phone(phone_id)}
            for phone_id in phone_ids
        ]

    @patch('taxi.clients.user_api.UserApiClient.create_user_phone')
    async def _create_user_phone(phone, *args, **kwargs):
        def phone_to_hex(phone):
            hex_size = 24
            if phone.startswith('+'):
                phone = phone[1:]
            hex_start = 'A' * (hex_size - len(phone))
            phone_hex = hex_start + phone
            return phone_hex

        identifier = bson.ObjectId(phone_to_hex(phone))

        return {'_id': identifier, 'phone': phone}


def _hex_to_phone(hex_phone):
    phone = hex_phone.strip('a')
    if not phone.startswith('+'):
        phone = '+' + phone
    return phone


@pytest.fixture
def drive_patch(patch):
    @patch('taxi.clients.drive.DriveClient.get_user_id_by_yandex_uid')
    async def _get_user_id_by_yandex_uid(*args, **kwargs):
        return {'users': [{'12345': 'user_id'}]}

    @patch('taxi.clients.drive.DriveClient.accounts_by_user_id')
    async def _accounts_by_user_id(*args, **kwargs):
        return {
            'accounts': [
                {
                    'id': 100,
                    'type_name': 'example',
                    'soft_limit': 10000,
                    'hard_limit': 10000,
                    'is_active': True,
                    'parent': {'id': 123},
                    'spent': 100500,
                    'details': {
                        'expenditure': 123400,
                        'next_refresh': 1622505600,
                    },
                },
            ],
        }

    @patch('taxi.clients.drive.DriveClient.accounts_by_users_ids')
    async def _accounts_by_users_ids(*args, **kwargs):
        list_users_ids = args[0]
        result = {'accounts': {}}

        for user_id in list_users_ids:
            result['accounts'][user_id] = [
                {
                    'id': 100,
                    'type_name': 'example',
                    'soft_limit': 10000,
                    'hard_limit': 10000,
                    'is_active': True,
                    'parent': {'id': 123},
                    'spent': 100500,
                    'details': {
                        'expenditure': 123400,
                        'next_refresh': 1622505600,
                    },
                },
            ]

        return result

    @patch('taxi.clients.drive.DriveClient.link')
    async def _link(*args, **kwargs):
        return {'account_ids': [100]}

    @patch('taxi.clients.drive.DriveClient.activate')
    async def _activate(*args, **kwargs):
        pass

    @patch('taxi.clients.drive.DriveClient.update_limits')
    async def _update_limits(*args, **kwargs):
        pass


@pytest.fixture
def corp_orders_mock(load_json):
    class CorpOrdersMock:
        def __init__(self, data):
            self._data = data

        def find_eats_orders(self, params, **kwargs):
            limit = params.get('limit', 50)
            offset = params.get('offset', 0)
            return {'orders': self._data[offset : offset + limit]}

        def find_drive_orders(self, params, **kwargs):
            limit = params.get('limit', 50)
            offset = params.get('offset', 0)
            return {'orders': self._data[offset : offset + limit]}

        def find_tanker_orders(self, params, **kwargs):
            limit = params.get('limit', 50)
            offset = params.get('offset', 0)
            return {'orders': self._data[offset : offset + limit]}

    return CorpOrdersMock(load_json('corp_orders_data.json'))


class Context:
    def __init__(self):
        self.req_id = None
        self.error = None
        self.client_id = None

    def set_data(self, req_id, error=None, client_id=None):
        self.req_id = req_id
        self.error = error
        self.client_id = client_id


@pytest.fixture
def client_requests_collection(db):
    return db.corp_client_requests


@pytest.fixture
def admin_context():
    return Context()


@pytest.fixture
def exp_client_mock(load_json):
    class ExpClientMock:
        new_configs = []

        def __init__(self, load_json):
            self.load_json = load_json

        async def get_config(self, name):
            body = self.load_json('get_exp_response.json')
            body['name'] = name
            return body

        async def load_file(
                self,
                data,
                file_name,
                experiment_name,
                transform,
                phone_type,
                arg_type,
                content_type,
        ):
            files = self.load_json('files_data.json')
            assert phone_type == 'yandex'
            assert transform == 'REPLACE_PHONE_TO_PHONE_ID'
            assert file_name in files.keys()
            assert experiment_name == files[file_name]['exp_name']
            assert data == files[file_name]['data']
            return {
                'id': files[file_name]['file_id'],
                'lines': 1,
                'hash': 'test_hash',
            }

        async def update_config(self, name, last_modified_at, data):
            check_data = self.load_json('expected_update_' + name + '.json')
            assert check_data == data
            assert check_data['last_modified_at'] == last_modified_at

        async def create_config(self, exp_name, exp_body):
            self.new_configs.append(exp_name)

    return ExpClientMock(load_json)


@pytest.fixture
def approvals_client_mock():
    class ApprovalsClientMock:
        data = ''
        params = {}

        async def create_draft(self, data, login, params=None, log_extra=None):
            self.data = data
            self.params = params
            return {'id': 1}

    return ApprovalsClientMock()


@pytest.fixture
def mock_corp_requests(mockserver, client_requests_collection):
    class MockCorpRequests:
        @dataclasses.dataclass
        class CorpRequestsData:
            market_offer_creation_code: typing.Optional[int]
            market_offer_creation_response: typing.Optional[dict]

        data = CorpRequestsData(
            market_offer_creation_code=None,
            market_offer_creation_response=None,
        )

        @staticmethod
        @mockserver.handler('/corp-requests/v1/client-trial')
        async def client_trial(request):
            assert request.method == 'POST'
            return mockserver.make_response(
                json={'client_id': '_id'}, status=200,
            )

        @staticmethod
        @mockserver.handler('/corp-requests/v1/register-trial')
        async def register_trial(request):
            assert request.method == 'POST'
            return mockserver.make_response(
                json={'client_id': '_id'}, status=200,
            )

        @staticmethod
        @mockserver.handler('/corp-requests/v1/client-requests/by-client-ids')
        async def request_by_client_id(request):
            client_ids = request.json.get('client_ids')

            result = await client_requests_collection.find(
                {'client_id': {'$in': client_ids}},
            ).to_list(None)

            response = {'client_requests': result}

            return mockserver.make_response(json=response, status=200)

        @staticmethod
        @mockserver.handler('/corp-requests/v1/client-requests/search')
        async def client_requests_search(request):
            data = request.json
            sort = []

            if data.get('sort'):
                for item in data['sort']:
                    field = item['field']
                    direction = 1 if item['direction'] == 'asc' else -1
                    sort.append((field, direction))

            query = {
                'updated': {'$gte': request.json.get('updated_since')},
                'status': request.json.get('status'),
            }

            result = await client_requests_collection.find(
                query, sort=sort,
            ).to_list(None)

            return mockserver.make_response(
                json={'items': result, **data}, status=200,
            )

        @staticmethod
        @mockserver.handler('/corp-requests/v1/client-requests')
        async def client_requests(request):
            request_id = request.args.get('request_id')
            result = await client_requests_collection.find_one(
                {'_id': request_id},
            )
            return mockserver.make_response(json=result)

        @staticmethod
        @mockserver.handler('/corp-requests/v1/market-offer/create')
        async def market_offer(request):
            return mockserver.make_response(
                json=MockCorpRequests.data.market_offer_creation_response,
                status=MockCorpRequests.data.market_offer_creation_code,
            )

        @staticmethod
        @mockserver.handler('/corp-requests/v1/collaterals/create')
        def create_collateral(request):
            return mockserver.make_response(json={}, status=200)

    return MockCorpRequests()


@pytest.fixture
def mock_corp_clients(mockserver):
    class MockCorpClients:
        @dataclasses.dataclass
        class CorpClientsData:
            get_client_response: dict
            create_client_response: dict
            get_contracts_response: dict
            get_services_response: dict
            get_service_response: dict
            sf_managers_response: dict
            cards_list_response: dict

        data = CorpClientsData(
            get_client_response={},
            create_client_response={'id': 'client_id'},
            get_contracts_response={},
            get_services_response={},
            get_service_response={'is_active': True},
            sf_managers_response={},
            cards_list_response={},
        )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/clients')
        async def clients(request):
            if request.method == 'GET':
                if MockCorpClients.data.get_client_response:
                    return mockserver.make_response(
                        json=MockCorpClients.data.get_client_response,
                        status=200,
                    )
                return mockserver.make_response(json={}, status=404)
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/clients/create')
        async def create_client(request):
            if request.method == 'POST':
                return mockserver.make_response(
                    json=MockCorpClients.data.create_client_response,
                    status=200,
                )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts')
        async def get_contracts(request):
            return mockserver.make_response(
                json=MockCorpClients.data.get_contracts_response, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/contracts/settings/update')
        def update_contract_settings(request):
            return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/services')
        async def get_services(request):
            return mockserver.make_response(
                json=MockCorpClients.data.get_services_response, status=200,
            )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/taxi')
        async def service_taxi(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/cargo')
        async def service_cargo(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/drive')
        async def service_drive(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/eats')
        async def service_eats(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/eats2')
        async def service_eats2(request):
            if request.method == 'GET':
                return mockserver.make_response(
                    json=MockCorpClients.data.get_service_response, status=200,
                )
            if request.method == 'PATCH':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/market')
        async def service_market(request):
            return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/services/tanker')
        async def service_tanker(request):
            return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/sf/managers')
        def get_sf_managers(request):
            return mockserver.make_response(
                json=MockCorpClients.data.sf_managers_response, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/corp-clients/v1/cards/list')
        def get_cards_list(request):
            return mockserver.make_response(
                json=MockCorpClients.data.cards_list_response, status=200,
            )

        @staticmethod
        @mockserver.handler('/corp-clients/v1/cards/main')
        async def cards_main(request):
            if request.method == 'POST':
                return mockserver.make_response(json={}, status=200)
            if request.method == 'DELETE':
                return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.handler('/corp-clients/v1/cards/bindings')
        async def cards_bindings(request):
            return mockserver.make_response(
                json={'binding_url': 'trust.ru/web/binding?purchase_token=a1'},
                status=200,
            )

    return MockCorpClients()


@pytest.fixture
def mock_corp_suggest(mockserver):
    class MockCorpSuggest:
        @dataclasses.dataclass
        class CorpSuggestData:
            get_cities: dict

        data = CorpSuggestData(get_cities={'items': []})

        @staticmethod
        @mockserver.json_handler('/corp-suggest/corp-suggest/v1/cities')
        async def get_cities(request):
            return mockserver.make_response(
                json=MockCorpSuggest.data.get_cities, status=200,
            )

    return MockCorpSuggest()


@pytest.fixture
def mock_drive(mockserver):
    class DriveMock:
        @dataclasses.dataclass
        class DriveData:
            drive_accounts_response: dict
            descriptions_response: dict
            promocode_response: dict
            expected_account_id: typing.Optional[str]

        data = DriveData(
            drive_accounts_response={},
            descriptions_response={},
            promocode_response={},
            expected_account_id=None,
        )

        @staticmethod
        @mockserver.json_handler('/drive/api/b2b/accounts/update_limits')
        def update_limits(request):
            return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.json_handler('/drive/api/b2b/accounts/update')
        def update_accounts(request):
            return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.json_handler('/drive/api/b2b/accounts/activate')
        def activate_wallet(request):
            return mockserver.make_response(json={}, status=200)

        @staticmethod
        @mockserver.json_handler('/drive/api/b2b/accounts')
        def fetch_drive_spending(request):
            if DriveMock.data.expected_account_id:
                assert (
                    request.args.get('account_id')
                    == DriveMock.data.expected_account_id
                )
            return mockserver.make_response(
                json=DriveMock.data.drive_accounts_response, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/drive/api/b2b/accounts/descriptions')
        async def get_descriptions(request):
            return mockserver.make_response(
                json=DriveMock.data.descriptions_response,
            )

        @staticmethod
        @mockserver.json_handler('/drive/api/b2b/accounts/promocode')
        async def create_promocode(request):
            return mockserver.make_response(
                json=DriveMock.data.promocode_response,
            )

    return DriveMock()


@pytest.fixture
def mock_corp_billing(mockserver):
    class CorpBillingMock:
        @dataclasses.dataclass
        class CorpBillingData:
            employees_spending_response: dict

        data = CorpBillingData(employees_spending_response={})

        @staticmethod
        @mockserver.json_handler('/corp-billing/v2/employees-spendings/find')
        def fetch_spending(request):
            return mockserver.make_response(
                json=CorpBillingMock.data.employees_spending_response,
                status=200,
            )

    return CorpBillingMock()


@pytest.fixture
def mock_corp_tariffs(mockserver, load_json):
    class MockCorpTariffs:
        @dataclasses.dataclass
        class CorpTariffsData:
            get_client_tariff_response: dict
            get_tariff_response: dict
            get_client_tariff_plan_response: dict

        data = CorpTariffsData(
            get_client_tariff_response={},
            get_tariff_response={},
            get_client_tariff_plan_response={},
        )

        @staticmethod
        @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
        async def get_client_tariff_current(request):
            return mockserver.make_response(
                json=MockCorpTariffs.data.get_client_tariff_response,
                status=200,
            )

        @staticmethod
        @mockserver.json_handler('/corp-tariffs/v1/tariff/current')
        async def get_tariff_current(request):
            return mockserver.make_response(
                json=MockCorpTariffs.data.get_tariff_response, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/corp-tariffs/v1/client_tariff_plan/current')
        async def get_client_tariff_plan_current(request):
            return mockserver.make_response(
                json=MockCorpTariffs.data.get_client_tariff_plan_response,
                status=200,
            )

    return MockCorpTariffs()


@pytest.fixture
def mock_tariffs(mockserver):
    class MockTariffs:
        @dataclasses.dataclass
        class TariffsData:
            get_tariff_zones_response: dict
            get_tariffs_response: dict

        data = TariffsData(
            get_tariff_zones_response={}, get_tariffs_response={},
        )

        @staticmethod
        @mockserver.json_handler('/tariffs/v1/tariff_zones')
        async def get_tariff_zones(request):
            return mockserver.make_response(
                json=MockTariffs.data.get_tariff_zones_response, status=200,
            )

        @staticmethod
        @mockserver.json_handler('/tariffs/v1/tariffs')
        async def get_tariffs(request):
            return mockserver.make_response(
                json=MockTariffs.data.get_tariffs_response, status=200,
            )

    return MockTariffs()


@pytest.fixture
def mock_corp_users(mockserver):
    class MockCorpUsers:
        @dataclasses.dataclass
        class CorpUsersData:
            get_user_code: int
            get_user_response: dict
            search_users_code: int
            search_users_response: dict
            int_api_cost_centers_list_code: int
            int_api_cost_centers_list_response: dict
            int_api_departments_list_code: int
            int_api_departments_list_response: dict
            list_users_code: int
            list_users_response: dict
            get_limit_code: int
            get_limit_response: dict
            search_limit_code: int
            search_limit_response: dict
            create_limit_code: int
            create_limit_response: dict
            update_limit_code: int
            update_limit_response: dict
            delete_limit_code: int
            delete_limit_response: dict
            get_users_spending_code: int
            get_users_spending_response: dict

        data = CorpUsersData(
            get_user_code=200,
            get_user_response={},
            search_users_code=200,
            search_users_response={},
            int_api_cost_centers_list_code=200,
            int_api_cost_centers_list_response={},
            int_api_departments_list_code=200,
            int_api_departments_list_response={},
            list_users_code=200,
            list_users_response={},
            get_limit_code=200,
            get_limit_response={},
            search_limit_code=200,
            search_limit_response={},
            create_limit_code=200,
            create_limit_response={},
            update_limit_code=200,
            update_limit_response={},
            delete_limit_code=200,
            delete_limit_response={},
            get_users_spending_code=200,
            get_users_spending_response={},
        )

        @staticmethod
        @mockserver.json_handler('/corp-users/v2/users')
        async def get_user(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.get_user_response,
                status=MockCorpUsers.data.get_user_code,
            )

        @staticmethod
        @mockserver.json_handler('/corp-users/v2/users/search')
        async def search_users(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.search_users_response,
                status=MockCorpUsers.data.search_users_code,
            )

        @staticmethod
        @mockserver.json_handler('/corp-users/v2/users/list')
        async def list_users(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.list_users_response,
                status=MockCorpUsers.data.list_users_code,
            )

        @staticmethod
        @mockserver.json_handler('/corp-users/v2/limits')
        async def get_limit(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.get_limit_response,
                status=MockCorpUsers.data.get_limit_code,
            )

        @staticmethod
        @mockserver.json_handler('/corp-users/v2/limits/search')
        async def search_limits(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.search_limit_response,
                status=MockCorpUsers.data.search_limit_code,
            )

        @staticmethod
        @mockserver.json_handler('/corp-users/v2/limits/create')
        async def create_limit(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.create_limit_response,
                status=MockCorpUsers.data.create_limit_code,
            )

        @staticmethod
        @mockserver.json_handler('/corp-users/v2/limits/update')
        async def update_limit(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.update_limit_response,
                status=MockCorpUsers.data.update_limit_code,
            )

        @staticmethod
        @mockserver.json_handler('/corp-users/v2/limits/delete')
        async def delete_limit(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.delete_limit_response,
                status=MockCorpUsers.data.delete_limit_code,
            )

        @staticmethod
        @mockserver.json_handler('/corp-users/v2/users-spending')
        async def get_users_spending(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.get_users_spending_response,
                status=MockCorpUsers.data.get_users_spending_code,
            )

        @staticmethod
        @mockserver.json_handler(
            '/corp-users/integration/v2/cost_centers/list',
        )
        async def int_api_cost_centers_list(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.int_api_cost_centers_list_response,
                status=MockCorpUsers.data.int_api_cost_centers_list_code,
            )

        @staticmethod
        @mockserver.json_handler('/corp-users/integration/v2/departments/list')
        async def int_api_departments_list(request):
            return mockserver.make_response(
                json=MockCorpUsers.data.int_api_departments_list_response,
                status=MockCorpUsers.data.int_api_departments_list_code,
            )

    return MockCorpUsers()


service.install_service_local_fixtures(__name__)
