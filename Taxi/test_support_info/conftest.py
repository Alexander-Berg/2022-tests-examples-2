# pylint: disable=redefined-outer-name, unused-variable
import datetime
import uuid

import pytest

from taxi import discovery
from taxi.clients import archive_api
from taxi.clients import chatterbox
from taxi.clients import personal
from taxi.clients import startrack
from taxi.clients import tvm
from taxi.clients import zendesk
from taxi.maintenance import run
from taxi.pytest_plugins import service
from taxi.util import helpers

from support_info import app
from support_info import app_stq
from support_info import cron_run
from test_support_info import helpers as support_info_helpers


pytest_plugins = [
    'taxi.pytest_plugins.stq_agent',
    'taxi.pytest_plugins.order_archive',
]

service.install_service_local_fixtures(__name__)

TELPHIN_API_KEY = 'test_telphin_api_key'


@pytest.fixture
def simple_secdist(simple_secdist):
    settings_override = simple_secdist['settings_override']
    settings_override['TVM_SERVICES'] = {'personal': {'secret': 1337}}
    settings_override['SUPPORT_INFO_API_ROLES_BY_KEY'].update(
        {TELPHIN_API_KEY: 'telphin'},
    )
    settings_override['YT_CONFIG'] = {
        'hahn': {
            'prefix': '//home/taxi',
            'token': 'test_token',
            'proxy': {'url': 'hahn.yt.yandex.net'},
        },
    }
    settings_override['DRIVER_CALLBACK_DB'] = {
        'host': 'db',
        'user': 'user',
        'password': 'password',
        'database': 'db',
    }
    return simple_secdist


@pytest.fixture
def mock_personal_single_response(monkeypatch):
    def mock_single_personal(unique: str):
        async def response_patch(*args, **kwargs):
            return {'phone': unique, 'license': unique, 'id': unique + '_id'}

        monkeypatch.setattr(
            personal.PersonalApiClient, 'store', response_patch,
        )
        monkeypatch.setattr(
            personal.PersonalApiClient, 'retrieve', response_patch,
        )

    return mock_single_personal


@pytest.fixture
async def support_info_app(loop, db, simple_secdist):
    application = app.create_app(loop=loop, db=db)
    yield application
    await application.close_sessions()


@pytest.fixture
async def support_info_context(loop, db, simple_secdist):
    async for context_data in cron_run.create_app(loop, db):
        yield run.StuffContext(
            None, 'test_task_id', datetime.datetime.utcnow(), context_data,
        )


@pytest.fixture
async def support_info_app_stq(loop, db, simple_secdist):
    app = app_stq.SupportInfoSTQApplication(loop=loop, db=db)
    for func in app.on_startup:
        await func(app)
    yield app
    for func in app.on_shutdown:
        await func(app)


@pytest.fixture(autouse=True)
def patch_stq_put(patch):
    @patch('taxi.stq.client.put')
    async def put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    return put


@pytest.fixture
def mock_driver_profiles(mockserver, load_json):
    def _get_profile(driver_uuid, profiles):
        for profile in profiles:
            if profile['data']['park_driver_profile_id'] == driver_uuid:
                return profile
        return {}

    driver_profiles = load_json('driver_profile_retrieve.json')

    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def mock_retrieve(request, *args, **kwargs):
        uuids = request.json['id_in_set']
        return {
            'profiles': [
                {
                    'park_driver_profile_id': driver_uuid,
                    **_get_profile(driver_uuid, driver_profiles),
                }
                for driver_uuid in uuids
            ],
        }


@pytest.fixture
def support_info_client(aiohttp_client, support_info_app, loop):
    return loop.run_until_complete(aiohttp_client(support_info_app))


@pytest.fixture
def archive_api_url(support_info_app):
    return support_info_app.settings.ARCHIVE_API_URL


@pytest.fixture
def mock_st_create_ticket(monkeypatch, mock):
    @mock
    async def _dummy_create_ticket(**kwargs):
        if 'unique' in kwargs and 'duplicate' in kwargs['unique']:
            raise startrack.ConflictError
        return {'key': kwargs['queue'] + '-1'}

    monkeypatch.setattr(
        startrack.StartrackAPIClient, 'create_ticket', _dummy_create_ticket,
    )
    return _dummy_create_ticket


@pytest.fixture
def mock_zendesk_search(monkeypatch):
    search_patcher = support_info_helpers.BaseAsyncPatcher(
        target=zendesk.ZendeskApiClient,
        method='search',
        response_body={'results': []},
    )
    search_patcher.patch(monkeypatch)
    return search_patcher


@pytest.fixture
def mock_chatterbox_search(monkeypatch):
    search_patcher = support_info_helpers.BaseAsyncPatcher(
        target=chatterbox.ChatterboxApiClient,
        method='search',
        response_body={'tasks': []},
    )
    search_patcher.patch(monkeypatch)
    return search_patcher


@pytest.fixture
def mock_tvm_get_service_name(monkeypatch):
    patcher = support_info_helpers.BaseAsyncPatcher(
        target=tvm.TVMClient,
        method='get_allowed_service_name',
        response_body='noname_service',
    )
    patcher.patch(monkeypatch)
    yield patcher
    patcher.assert_called()


@pytest.fixture
def custom_request(support_info_app):
    class Request:
        def __init__(self, app):
            self.app = app
            self.match_info = {}

        def __getitem__(self, item):
            if hasattr(self, item):
                return getattr(self, item)
            return None

    return Request(support_info_app)


@pytest.fixture
def admin_api_url(support_info_app):
    return (
        support_info_app.settings.TARIFF_EDITOR_URL
        + support_info_app.settings.TARIFF_EDITOR_API_PREFIX
    )


@pytest.fixture
def mock_csrf(patch_aiohttp_session, response_mock, admin_api_url):
    dict_cookies = {
        'Session_id': 'user_sid',
        'sessionid2': 'user_sid2',
        'yandexuid': 'user_uid',
    }
    str_cookies = helpers.cookies_string(dict_cookies)
    csrf_token = '0bdda419121ckcaba211c1ee583136400ce3ef9c:1555326888'

    # pylint: disable=unused-variable
    @patch_aiohttp_session(admin_api_url + '/me/', 'GET')
    def _csrf(*args, **kwargs):
        assert 'X-Real-Ip' in kwargs['headers']
        assert 'X-Forwarded-For' in kwargs['headers']
        assert kwargs['headers']['Cookie'] == str_cookies
        return response_mock(json={'csrf_token': csrf_token})

    return {
        'dict_cookies': dict_cookies,
        'str_cookies': str_cookies,
        'csrf_token': csrf_token,
    }


@pytest.fixture
def mock_get_user_info(
        patch_aiohttp_session, response_mock, mock_csrf, admin_api_url,
):
    def wrapper(response=None, status=200):
        @patch_aiohttp_session(admin_api_url + '/user_info/', 'GET')
        def _get_user_info(*args, **kwargs):
            assert kwargs['params'] == {'csrf_token': mock_csrf['csrf_token']}
            assert 'X-Real-Ip' in kwargs['headers']
            assert 'X-Forwarded-For' in kwargs['headers']

            result = response if response is not None else {'filters': {}}
            return response_mock(json=result, status=status)

        return _get_user_info

    return wrapper


@pytest.fixture
def mock_select_rows(monkeypatch, mock):
    @mock
    async def _dummy_select_rows(**kwargs):
        return [{'id': 'some_order_id'}]

    monkeypatch.setattr(
        archive_api.ArchiveApiClient, 'select_rows', _dummy_select_rows,
    )
    return _dummy_select_rows


@pytest.fixture
def patch_get_order_by_id(
        patch_aiohttp_session, response_mock, archive_api_url,
):
    def wrapper(order):
        @patch_aiohttp_session(archive_api_url + '/archive/order', 'POST')
        def get_archived_order(*args, **kwargs):
            assert kwargs['json']['id'] == order['_id']
            return response_mock(json={'doc': order})

        return get_archived_order

    return wrapper


@pytest.fixture
def patch_quality_control_cpp_empty(patch_aiohttp_session, response_mock):
    def wrapper():
        qc_cpp_service = discovery.find_service('quality_control_cpp')

        @patch_aiohttp_session(qc_cpp_service.url, 'POST')
        def _patch_request(method, url, **kwargs):
            assert method == 'POST'
            return response_mock(json={})

        return _patch_request

    return wrapper


@pytest.fixture
def mock_billing_reports_empty(mockserver):
    @mockserver.json_handler('/billing-reports/v1/docs/select')
    def _mock_request(request, *args, **kwargs):
        assert request.method == 'POST'
        return mockserver.make_response(json={'docs': []})

    return _mock_request


@pytest.fixture
def patch_order_proc_retrieve(
        patch_aiohttp_session,
        response_mock,
        archive_api_url,
        order_archive_mock,
):
    def wrapper(order):
        if order:
            order_archive_mock.set_order_proc(order)

        return order_archive_mock.order_proc_retrieve

    return wrapper


@pytest.fixture
def patch_support_chat_create_chat(patch_aiohttp_session, response_mock):
    def wrapper(response, status=200):
        support_chat_url = discovery.find_service('support_chat').url

        @patch_aiohttp_session(support_chat_url + '/v1/chat', 'POST')
        def create_chat_request(method, url, **kwargs):
            return response_mock(json=response, status=status)

        return create_chat_request

    return wrapper


@pytest.fixture
def patch_chatterbox_tasks(patch_aiohttp_session, response_mock):
    def wrapper(response, status=200):
        chatterbox_url = discovery.find_service('chatterbox').url

        @patch_aiohttp_session(chatterbox_url + '/v1/tasks', 'POST')
        def tasks_request(method, url, **kwargs):
            return response_mock(json=response, status=status)

        return tasks_request

    return wrapper


@pytest.fixture
def patch_chatterbox_get_by_id(patch_aiohttp_session, response_mock):
    def wrapper(response, status=200):
        chatterbox_url = discovery.find_service('chatterbox').url

        @patch_aiohttp_session(chatterbox_url + '/v1/tasks/{task_id}', 'GET')
        def tasks_request(method, url, **kwargs):
            return response_mock(json=response, status=status)

        return tasks_request

    return wrapper


@pytest.fixture
def patch_get_startrack_ticket(patch_aiohttp_session, response_mock):
    def wrapper(response, status=200):
        @patch_aiohttp_session('http://test-startrack-url/issues/', 'GET')
        def get_ticket(*args, **kwargs):
            return response_mock(json=response, status=status)

        return get_ticket

    return wrapper


@pytest.fixture
def patch_get_startrack_tickets(patch_aiohttp_session, response_mock):
    def wrapper(tickets):
        @patch_aiohttp_session(
            'http://test-startrack-url/issues/_search/', 'POST',
        )
        def get_tickets(*args, **kwargs):
            return response_mock(json=tickets)

        return get_tickets

    return wrapper


@pytest.fixture
def patch_created_startrack_ticket(patch_aiohttp_session, response_mock):
    def wrapper(ticket_info, contract_id=None, ticket_data=None, status=200):
        @patch_aiohttp_session('http://test-startrack-url/issues', 'POST')
        def get_created_ticket(*args, **kwargs):
            if contract_id:
                assert contract_id in kwargs['json'].values()
            if ticket_data:
                assert ticket_data == kwargs['json']
            return response_mock(json=ticket_info, status=status)

        return get_created_ticket

    return wrapper


@pytest.fixture
def patch_get_driver_ratings(mockserver, response_mock):
    def wrapper(unique_driver_id, mock_data):
        @mockserver.json_handler('/driver-ratings/v1/driver/ratings/retrieve')
        def get_driver_ratings(request):
            assert request.json == {'id_in_set': [unique_driver_id]}
            assert request.query == {'consumer': 'support_info'}
            return mock_data

        return get_driver_ratings

    return wrapper


@pytest.fixture
def patch_get_driver_weariness(patch_aiohttp_session, response_mock):
    def wrapper(unique_driver_id, mock_data):
        driver_weariness = discovery.find_service('driver-weariness').url

        @patch_aiohttp_session(
            driver_weariness + '/v1/driver_weariness', 'POST',
        )
        def get_driver_weariness(method, url, **kwargs):
            assert kwargs['json'] == {'unique_driver_id': unique_driver_id}
            return response_mock(json=mock_data)

        return get_driver_weariness

    return wrapper


@pytest.fixture
def patch_get_dms(patch_aiohttp_session, response_mock):
    def wrapper(mock_data):
        dms = discovery.find_service('driver_metrics_storage').url

        @patch_aiohttp_session(dms + '/v3/events/processed', 'POST')
        def get_dms(method, url, **kwargs):
            return response_mock(json=mock_data)

        return get_dms

    return wrapper


@pytest.fixture
def mock_personal_single_phone(monkeypatch):
    def mock_single_personal(phone: str):
        async def response_patch(*args, **kwargs):
            return {'phone': phone, 'id': phone + '_id'}

        monkeypatch.setattr(
            personal.PersonalApiClient, 'store', response_patch,
        )
        monkeypatch.setattr(
            personal.PersonalApiClient, 'retrieve', response_patch,
        )

    return mock_single_personal


@pytest.fixture
def mock_personal_single_email(monkeypatch):
    def mock_single_personal(email: str):
        async def response_patch(*args, **kwargs):
            return {'email': email, 'id': email + '_id'}

        monkeypatch.setattr(
            personal.PersonalApiClient, 'store', response_patch,
        )
        monkeypatch.setattr(
            personal.PersonalApiClient, 'retrieve', response_patch,
        )

    return mock_single_personal


@pytest.fixture
def mock_get_tags(mockserver):
    def _wrap(response, tags_service='tags', next_response=None):
        tags_v1_match = f'/{tags_service}/v1/match'
        tags_v1_match_profile = f'/{tags_service}/v1/drivers/match/profile'
        tags_v2_match_single = f'/{tags_service}/v2/match_single'
        tags_v3_match_single = f'/{tags_service}/v3/match_single'
        state = {'already_called': False}

        @mockserver.json_handler(tags_v3_match_single)
        @mockserver.json_handler(tags_v2_match_single)
        @mockserver.json_handler(tags_v1_match_profile)
        @mockserver.json_handler(tags_v1_match)
        def dummy_match(request):
            if next_response is None:
                return response
            if state['already_called']:
                return next_response
            state['already_called'] = True
            return response

        return dummy_match

    return _wrap


@pytest.fixture
def mock_support_tags(mockserver):
    def _wrap(response):
        @mockserver.json_handler('/support-tags/v1/tags')
        def dummy_tags(request):
            return response

        return dummy_tags

    return _wrap


@pytest.fixture
def mock_get_user_phones(mockserver, load_json):
    user_phones = load_json('user_api_user_phones.json')
    for user_phone in user_phones:
        if 'type' not in user_phone:
            user_phone['type'] = 'yandex'
        if 'stat' not in user_phone:
            user_phone['stat'] = {}
        if 'is_loyal' not in user_phone:
            user_phone['is_loyal'] = False
        if 'is_taxi_staff' not in user_phone:
            user_phone['is_taxi_staff'] = False
        if 'is_yandex_staff' not in user_phone:
            user_phone['is_yandex_staff'] = False

    @mockserver.json_handler('/user-api/user_phones/get')
    def _get_user_phone(request):
        for user_phone in user_phones:
            if request.json['id'] == user_phone['id']:
                return user_phone
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/user-api/user_phones/by_number/retrieve')
    def _retrieve_user_phone(request):
        request_phone = request.json['phone']
        request_type = request.json['type']
        for user_phone in user_phones:
            if (
                    user_phone['phone'] == request_phone
                    and user_phone['type'] == request_type
            ):
                return user_phone
        return mockserver.make_response(status=404)


@pytest.fixture
def mock_get_users(mockserver, load_json):
    try:
        users = load_json('user_api_users.json')
    except FileNotFoundError:
        users = []

    @mockserver.json_handler('/user-api/users/get')
    def _get_user(request):
        for user in users:
            if request.json['id'] == user['id']:
                return user
        return mockserver.make_response(status=404)

    @mockserver.json_handler('/user-api/users/search')
    def _search_user(request):
        phone_id = request.json['phone_ids'][0]
        application = request.json.get('applications', [None])[0]

        response = []
        for user in users:
            if (user.get('phone_id') == phone_id) and (
                    not application or user.get('application') == application
            ):
                response.append(user)
        return {'items': response}


@pytest.fixture
def mock_uuid_fixture(patch):
    @patch('uuid.uuid4')
    def uuid4():
        return uuid.UUID('2104653b-dac3-43e3-9ac5-7869d0bd738d')


@pytest.fixture
def mock_personal(mockserver, load_json, patch):

    pd_data = load_json('personal_data.json')

    @patch('taxi.clients.personal.PersonalApiClient._get_auth_headers')
    async def _get_auth_headers_mock(*args, **kwargs):
        return {'auth': 'ticket'}

    @mockserver.json_handler('/personal/v1/driver_licenses/store')
    def mock_store_license(request, *args, **kwargs):
        licenses = pd_data['driver_licenses']
        for driver_license in licenses:
            if driver_license['value'] == request.json['value']:
                return driver_license
        return None

    @mockserver.json_handler('/personal/v1/driver_licenses/retrieve')
    def mock_retrieve_license(request, *args, **kwargs):
        licenses = pd_data['driver_licenses']
        for driver_license in licenses:
            if driver_license['id'] == request.json['id']:
                return driver_license
        return None

    @mockserver.json_handler('/personal/v1/phones/retrieve')
    def mock_retrieve_phone(request, *args, **kwargs):
        phones = pd_data['phones']
        for phone in phones:
            if phone['id'] == request.json['id']:
                return phone
        return None

    @mockserver.json_handler('/personal/v1/phones/bulk_retrieve')
    def mock_bulk_retrieve_phone(request, *args, **kwargs):
        pd_ids = [item['id'] for item in request.json['items']]
        phones = pd_data['phones']
        return {'items': [phone for phone in phones if phone['id'] in pd_ids]}


@pytest.fixture
def mock_driver_trackstory(mockserver):
    @mockserver.json_handler('/driver-trackstory/position')
    def mock_get_last_track(request, *args, **kwargs):
        assert 'driver_id' in request.json
        assert isinstance(request.json['driver_id'], str)
        return {
            'position': {
                'lat': 55.749893,
                'lon': 37.625894,
                'speed': 11.110533714294434,
                'direction': 264,
                'timestamp': 1627564607,
            },
            'type': 'adjusted',
        }


@pytest.fixture
def mock_driver_priority(mockserver):
    @mockserver.json_handler('/driver-priority/v1/priority/diagnostics')
    def mock_get_screen_driver_priority(request, *args, **kwargs):
        assert request.method == 'GET'
        assert 'Accept-Language' in request.headers
        assert len(request.query) == 4
        for key in ['lat', 'lon', 'park_id', 'uuid']:
            assert key in request.query
        return {
            'screen': {
                'items': [
                    {
                        'id': 'covid',
                        'title': 'Дезинфекция машины',
                        'value': 2,
                        'status': 'achievable',
                    },
                    {
                        'id': 'ya_music',
                        'title': 'Поездки с музыкой',
                        'subtitle': 'Действует до 01.07',
                        'value': 2,
                        'status': 'achievable',
                    },
                ],
            },
        }


@pytest.fixture
def mock_persey_payments(mockserver, load_json):
    data = load_json('persey_payments.json')

    @mockserver.json_handler(
        '/persey-payments/internal/v1/charity/ride_donations',
    )
    def mock_get_ride_donations(request, *args, **kwargs):
        assert request.method == 'GET'
        assert len(request.query) == 1
        assert 'order_ids' in request.query
        order_id = request.query['order_ids']
        for order in data:
            if order_id == order['order_id']:
                return {
                    'orders': [
                        {
                            'order_id': order_id,
                            'donation': {
                                'status': 'finished',
                                'amount_info': {'amount': order['charity']},
                            },
                        },
                    ],
                }
        return mockserver.make_response(status=404)


@pytest.fixture
def mock_taxi_fleet(mockserver):
    @mockserver.json_handler('/taxi-fleet/internal/v1/cards/orders/details')
    def mock_get_order_info(request, *args, **kwargs):
        assert request.method == 'GET'
        assert 'order_id' in request.query
        assert 'park_id' in request.query
        return {
            'order': {
                'cancellation_description': 'some_reason',
                'surge': 'x1,0',
                'cancelled_by': 'driver',
            },
        }


@pytest.fixture(autouse=True)
def mock_candidates(mockserver):
    @mockserver.json_handler('/candidates/profiles')
    def get_available_driver_categories(request, *args, **kwargs):
        assert request.method == 'POST'
        assert len(request.json) == 2
        assert 'driver_ids' in request.json
        assert len(request.json['driver_ids'][0]) == 2
        assert 'dbid' in request.json['driver_ids'][0]
        assert 'uuid' in request.json['driver_ids'][0]
        assert 'data_keys' in request.json
        assert request.json['data_keys']
        assert 'classes' in request.json['data_keys'][0]

        return {
            'drivers': [
                {'classes': ['econom', 'uberblack', 'uberx', 'maybach']},
            ],
        }


@pytest.fixture(autouse=True)
def mock_driver_diagnostics(mockserver):
    @mockserver.json_handler(
        '/driver-diagnostics'
        '/internal/driver-diagnostics/v1/common/restrictions',
    )
    def get_common_restrictions(request, *args, **kwargs):
        assert request.method == 'POST'
        assert len(request.query) == 2
        assert 'park_id' in request.query
        assert 'contractor_profile_id' in request.query

        return {
            'checks': [
                {
                    'id': 'temp',
                    'type': 'block',
                    'title': 'Доступ ограничен',
                    'items': [{'id': 'dkk', 'title': 'Пройдите dkk'}],
                },
            ],
            'tariffs': [
                {
                    'id': 'maybach',
                    'reasons': [
                        {
                            'id': 'disabled_in_zone_category',
                            'title': 'Отключено парком',
                        },
                    ],
                },
                {'id': 'econom', 'reasons': []},
            ],
        }


@pytest.fixture()
def mock_maas(mockserver):
    @mockserver.json_handler('/internal/v1/mark-maas-orders')
    def _dummy_maas_info(request):
        return {
            'maas_infos': [
                {
                    'order_id': 'order_id_1',
                    'is_maas_order': True,
                    'subscription_applied': False,
                },
            ],
        }

    return _dummy_maas_info
