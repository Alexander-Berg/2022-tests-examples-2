import typing

# flake8: noqa
# pylint: disable=wildcard-import, unused-wildcard-import, import-error, import-only-modules
from eats_catalog_storage_cache import (  # noqa: F403 F401
    eats_catalog_storage_cache,  # noqa: F403 F401
)
import pytest

from eats_restapp_marketing_plugins import *  # noqa: F403 F401


from tests_eats_restapp_marketing import direct
from tests_eats_restapp_marketing import sql


from .mock_services.canvas import mock_canvas  # noqa: F403 F401 E501 I202

from .mock_services.direct_internal import (
    mock_direct_internal,
)  # noqa: F403 F401 E501 I202

from .mock_services.feeds_admin import (
    mock_feeds_admin,
)  # noqa: F403 F401 E501 I202

TEST_PARTNER_ID = 1
TEST_UID = '100'
TEST_DISPLAY_NAME = 'Козьма Прутков'
TEST_FIO = 'Козьма Прутков'
TEST_AVATAR_ID = '123'
TEST_LOGIN = 'kozmaprutkov'


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture for eats-catalog-storage places cache',
    )
    config.addinivalue_line(
        'markers', 'adverts: [adverts] fixture for inserting adverts',
    )
    config.addinivalue_line(
        'markers',
        'campaigns: [campaigns] fixture for inserting cpm campaigns',
    )
    config.addinivalue_line(
        'markers', 'banners: [banners] fixture for inserting cpm banners',
    )


@pytest.fixture
def mock_retrieve_ids(mockserver, request):
    @mockserver.json_handler(
        '/eats-catalog-storage/'
        'internal/eats-catalog-storage/v1/places/retrieve-by-ids',
    )
    def _mock_retrieve_ids(request):
        return mockserver.make_response(
            status=200,
            json={
                'places': [
                    {
                        'id': 1,
                        'revision_id': 1,
                        'updated_at': '2020-04-28T12:00:00+03:00',
                        'archived': False,
                    },
                ],
                'not_found_place_ids': [],
            },
        )


@pytest.fixture
def mock_authorizer_allowed(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)


@pytest.fixture
def mock_communications(mockserver, request):
    @mockserver.json_handler(
        '/eats-restapp-communications/internal/communications/v1/send-event',
    )
    def _mock_communications(request):
        return mockserver.make_response(status=204)


@pytest.fixture
def mock_authorizer_forbidden(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'Forbidden',
                'place_ids': request.json['place_ids'],
            },
        )


@pytest.fixture
def mock_authorizer_500(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_authorizer_400(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400,
            json={'code': '400', 'message': 'Пользователь не найден'},
        )


@pytest.fixture(name='request_proxy')
async def _request_proxy(taxi_eats_restapp_marketing):
    async def do_request_proxy(method, url, data, partner_id):
        headers = {
            'X-YaEda-PartnerId': str(partner_id),
            'Content-type': 'application/json',
        }
        extra = {'headers': headers}
        if data is not None:
            extra['json'] = data
        return await getattr(taxi_eats_restapp_marketing, method.lower())(
            url, **extra,
        )

    return do_request_proxy


@pytest.fixture(name='mock_any_handler')
async def _mock_any_handler(mockserver):
    async def do_mock_handler(url, response):
        @mockserver.json_handler(url)
        def _do_mock_handler(request):
            return mockserver.make_response(**response)

        return _do_mock_handler

    return do_mock_handler


@pytest.fixture
def mock_blackbox_all(mockserver, request):
    @mockserver.json_handler('/blackbox')
    def _mock_authorizer(request):
        if request.args['method'] != 'userinfo':
            return mockserver.make_response(
                status=200,
                json={
                    'oauth': {
                        'uid': '1229582676',
                        'token_id': '2498905377',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'direct:api',
                        'ctime': '2020-12-07 20:49:55',
                        'issue_time': '2021-03-08 16:15:39',
                        'expire_time': '2022-03-08 16:15:39',
                        'is_ttl_refreshable': True,
                        'client_id': 'cfe379f646f3446ea1e6bc43e1385e3f',
                        'client_name': 'Яндекс.Еда для ресторанов',
                        'client_icon': (
                            'https://avatars.mds.yandex.net/.../normal'
                        ),
                        'client_homepage': '',
                        'client_ctime': '2020-11-10 13:16:25',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '1229582676',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'yndx-eda-direct-test',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'yndx-eda-direct-test'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:2498905377',
                    'login_id': 's:1592308671257:XXXXX:c',
                },
            )
        assert request.args['method'] == 'userinfo'
        assert request.args['uid'] == '1229582678,1229582676'
        assert request.args['attributes'] == '1007'
        assert request.args['regname'] == 'yes'
        assert 'get_public_name' not in request.args
        display_name = TEST_DISPLAY_NAME
        fio = TEST_FIO
        avatar = TEST_AVATAR_ID
        fails = False
        not_found = False
        if fails:
            return mockserver.make_response(status=500)

        if not_found:
            return {
                'id': 1229582676,
                'uid': {},
                'karma': {'value': 0},
                'karma_status': {'value': 0},
            }

        attributes = {}
        if fio:
            attributes['1007'] = fio

        avatar_attr = {'empty': True}
        if avatar:
            avatar_attr['default'] = avatar
            avatar_attr['empty'] = False

        return mockserver.make_response(
            status=200,
            json={
                'users': [
                    {
                        'aliases': {},
                        'dbfields': {},
                        'attributes': attributes,
                        'id': '1229582676',
                        'karma': {'value': 0},
                        'karma_status': {'value': 0},
                        'login': 'login_1',
                        'phones': [],
                        'emails': [],
                        'uid': {'value': '1229582676'},
                        'display_name': {
                            'name': display_name,
                            'avatar': avatar_attr,
                        },
                    },
                    {
                        'aliases': {},
                        'dbfields': {},
                        'attributes': attributes,
                        'id': '1229582678',
                        'karma': {'value': 0},
                        'karma_status': {'value': 0},
                        'login': 'login_2',
                        'phones': [],
                        'emails': [],
                        'uid': {'value': '1229582678'},
                        'display_name': {'name': display_name},
                    },
                ],
            },
        )


@pytest.fixture
def mock_blackbox_one(mockserver, request):
    @mockserver.json_handler('/blackbox')
    def _mock_authorizer(request):
        if request.args['method'] != 'userinfo':
            return mockserver.make_response(
                status=200,
                json={
                    'oauth': {
                        'uid': '1229582676',
                        'token_id': '2498905377',
                        'device_id': '',
                        'device_name': '',
                        'scope': 'direct:api',
                        'ctime': '2020-12-07 20:49:55',
                        'issue_time': '2021-03-08 16:15:39',
                        'expire_time': '2022-03-08 16:15:39',
                        'is_ttl_refreshable': True,
                        'client_id': 'cfe379f646f3446ea1e6bc43e1385e3f',
                        'client_name': 'Яндекс.Еда для ресторанов',
                        'client_icon': (
                            'https://avatars.mds.yandex.net/.../normal'
                        ),
                        'client_homepage': '',
                        'client_ctime': '2020-11-10 13:16:25',
                        'client_is_yandex': False,
                        'xtoken_id': '',
                        'meta': '',
                    },
                    'uid': {
                        'value': '1229582676',
                        'lite': False,
                        'hosted': False,
                    },
                    'login': 'yndx-eda-direct-test',
                    'have_password': True,
                    'have_hint': False,
                    'aliases': {'1': 'yndx-eda-direct-test'},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                    'dbfields': {'subscription.suid.669': ''},
                    'status': {'value': 'VALID', 'id': 0},
                    'error': 'OK',
                    'connection_id': 't:2498905377',
                    'login_id': 's:1592308671257:XXXXX:c',
                },
            )
        assert request.args['method'] == 'userinfo'
        assert request.args['uid'] == '1229582676'
        assert request.args['attributes'] == '1007'
        assert request.args['regname'] == 'yes'
        assert 'get_public_name' not in request.args
        display_name = TEST_DISPLAY_NAME
        fio = TEST_FIO
        avatar = TEST_AVATAR_ID
        fails = False
        not_found = False
        if fails:
            return mockserver.make_response(status=500)

        if not_found:
            return {
                'id': 1229582676,
                'uid': {},
                'karma': {'value': 0},
                'karma_status': {'value': 0},
            }

        attributes = {}
        if fio:
            attributes['1007'] = fio

        avatar_attr = {'empty': True}
        if avatar:
            avatar_attr['default'] = avatar
            avatar_attr['empty'] = False

        return mockserver.make_response(
            status=200,
            json={
                'users': [
                    {
                        'aliases': {},
                        'dbfields': {},
                        'attributes': attributes,
                        'id': '1229582676',
                        'karma': {'value': 0},
                        'karma_status': {'value': 0},
                        'login': 'login_1',
                        'phones': [],
                        'emails': [],
                        'uid': {'value': '1229582676'},
                        'display_name': {
                            'name': display_name,
                            'avatar': avatar_attr,
                        },
                    },
                ],
            },
        )


@pytest.fixture(name='mock_blackbox_userinfo')
async def _mock_blackbox_userinfo(mockserver):
    async def do_mock_blackbox_userinfo(
            uid=TEST_UID,
            display_name=TEST_DISPLAY_NAME,
            fio=TEST_FIO,
            avatar=TEST_AVATAR_ID,
            login=TEST_LOGIN,
            fails=False,
            not_found=False,
    ):
        @mockserver.json_handler('/blackbox')
        async def _do_mock_blackbox(request):
            assert request.args['method'] == 'userinfo'
            assert request.args['uid'] == uid
            assert request.args['attributes'] == '1007'
            assert request.args['regname'] == 'yes'
            assert 'get_public_name' not in request.args

            if fails:
                return mockserver.make_response(status=500)

            if not_found:
                return {
                    'id': uid,
                    'uid': {},
                    'karma': {'value': 0},
                    'karma_status': {'value': 0},
                }

            attributes = {}
            if fio:
                attributes['1007'] = fio

            avatar_attr = {'empty': True}
            if avatar:
                avatar_attr['default'] = avatar
                avatar_attr['empty'] = False

            return {
                'users': [
                    {
                        'aliases': {},
                        'dbfields': {},
                        'attributes': attributes,
                        'id': uid,
                        'karma': {'value': 0},
                        'karma_status': {'value': 0},
                        'login': login,
                        'phones': [],
                        'emails': [],
                        'uid': {'value': uid},
                        'display_name': {
                            'name': display_name,
                            'avatar': avatar_attr,
                        },
                    },
                ],
            }

        return _do_mock_blackbox

    return do_mock_blackbox_userinfo


@pytest.fixture
def mock_blackbox_400(mockserver, request):
    @mockserver.json_handler('/blackbox')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'bad request'},
        )


@pytest.fixture
def mock_blackbox_tokeninfo(mockserver, request):
    @mockserver.json_handler('/blackbox')
    def _mock_authorizer(request):
        if request.args['method'] == 'userinfo':
            uids = request.args['uid'].split(',')
            users = []
            for uid in uids:
                users.append(
                    {
                        'aliases': {},
                        'dbfields': {},
                        'attributes': {'1007': f'{uid}_attributes'},
                        'id': uid,
                        'karma': {'value': 0},
                        'karma_status': {'value': 0},
                        'login': f'{uid}_login',
                        'phones': [],
                        'emails': [],
                        'uid': {'value': uid},
                        'display_name': {
                            'name': f'{uid}_display_name',
                            'avatar': {
                                'default': f'{uid}_avatar',
                                'empty': False,
                            },
                        },
                    },
                )
            return {'users': users}
        return mockserver.make_response(
            status=200,
            json={
                'oauth': {
                    'uid': '1229582676',
                    'token_id': '2498905377',
                    'device_id': '',
                    'device_name': '',
                    'scope': 'direct:api',
                    'ctime': '2020-12-07 20:49:55',
                    'issue_time': '2021-03-08 16:15:39',
                    'expire_time': '2022-03-08 16:15:39',
                    'is_ttl_refreshable': True,
                    'client_id': 'cfe379f646f3446ea1e6bc43e1385e3f',
                    'client_name': 'Яндекс.Еда для ресторанов',
                    'client_icon': 'https://avatars.mds.yandex.net/.../normal',
                    'client_homepage': '',
                    'client_ctime': '2020-11-10 13:16:25',
                    'client_is_yandex': False,
                    'xtoken_id': '',
                    'meta': '',
                },
                'uid': {'value': '1229582676', 'lite': False, 'hosted': False},
                'login': 'yndx-eda-direct-test',
                'have_password': True,
                'have_hint': False,
                'aliases': {'1': 'yndx-eda-direct-test'},
                'karma': {'value': 0},
                'karma_status': {'value': 0},
                'dbfields': {'subscription.suid.669': ''},
                'status': {'value': 'VALID', 'id': 0},
                'error': 'OK',
                'connection_id': 't:2498905377',
                'login_id': 's:1592308671257:XXXXX:c',
            },
        )


@pytest.fixture
def mock_eats_core(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/service-schedule/update')
    def _mock_sessions(req):
        return mockserver.make_response(status=200, json={'isSuccess': True})


@pytest.fixture
def mock_eats_core_500(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/service-schedule/update')
    def _mock_sessions(req):
        return mockserver.make_response(status=500)


@pytest.fixture
def mock_eats_core_404(mockserver, request):
    @mockserver.json_handler('/eats-core/v1/places/service-schedule/update')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=404,
            json={'isSuccess': False, 'statusCode': 404, 'type': 'error'},
        )


@pytest.fixture
def mock_eats_advert_resume(mockserver, request):
    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def _mock_sessions(req):
        assert req.headers['Authorization'].count('Bearer') == 1
        return mockserver.make_response(
            status=200,
            json={
                'result': {
                    'ResumeResults': [
                        {
                            'Warnings': [
                                {
                                    'Message': 'Object is not stopped',
                                    'Code': 10021,
                                    'Details': 'Campaign is not stopped',
                                },
                            ],
                            'Id': 399264,
                        },
                    ],
                },
            },
        )


@pytest.fixture
def mock_eats_advert_resume_error(mockserver, request):
    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def _mock_sessions(req):
        assert req.headers['Authorization'].count('Bearer') == 1
        return mockserver.make_response(
            status=200,
            json={
                'result': {
                    'ResumeResults': [
                        {
                            'Errors': [
                                {
                                    'Details': 'Campaign not found',
                                    'Code': 8800,
                                    'Message': 'Object not found',
                                },
                            ],
                        },
                    ],
                },
            },
        )


@pytest.fixture
def mock_eats_advert_statistics(mockserver, request):
    @mockserver.json_handler('/direct/json/v5/reports')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=200,
            response='\n'.join(
                [
                    '"Actual Data (2021-02-05 - 2021-02-06)"',
                    'Clicks	Cost Date',
                    '1	2130000	2021-05-04',
                    '1	2150000	2021-05-23',
                    'Total rows: 2',
                    '',
                ],
            ),
        )


@pytest.fixture
def mock_place_access(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/check')
    def _mock_sessions(req):
        return mockserver.make_response(status=200, json={})


@pytest.fixture
def mock_auth_partner(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_auth_partner(request):
        return mockserver.make_response(status=200)


@pytest.fixture
def mock_auth_partner_bad_request(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_auth_partner_bad(request):
        return mockserver.make_response(
            status=400, json={'code': 400, 'message': 'Bad access'},
        )


@pytest.fixture
def mock_auth_partner_not_manager(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_auth_partner(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'forbidden',
                'details': {
                    'permissions': ['permission.restaurant.management'],
                    'place_ids': [123],
                },
            },
        )


@pytest.fixture
def mock_list_places(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/list')
    def _mock_list_places(request):
        return mockserver.make_response(status=200, json={'place_ids': [123]})


@pytest.fixture
def mock_list_places_empty(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/list')
    def _mock_list_places(request):
        return mockserver.make_response(status=200, json={'place_ids': []})


@pytest.fixture
def mock_list_places_400(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/place-access/list')
    def _mock_list_places(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'bad request'},
        )


@pytest.fixture
def mock_eats_advert_balance(mockserver, request):
    @mockserver.json_handler('/direct/live/v4/json')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=200,
            json={
                'data': {
                    'Accounts': [
                        {
                            'EmailNotification': {
                                'SendWarn': None,
                                'PausedByDayBudget': 'Yes',
                                'MoneyWarningValue': 20,
                                'Email': 'yndx-eda-direct-test@yandex.ru',
                            },
                            'Currency': 'RUB',
                            'Discount': 0,
                            'Amount': '8333.33',
                            'AccountID': 403308,
                            'AmountAvailableForTransfer': '8333.33',
                            'SmsNotification': {
                                'MoneyOutSms': 'No',
                                'SmsTimeFrom': '09:00',
                                'PausedByDayBudgetSms': 'Yes',
                                'SmsTimeTo': '21:00',
                                'MoneyInSms': 'No',
                            },
                            'Login': 'yndx-eda-direct-test',
                            'AgencyName': None,
                        },
                    ],
                    'ActionsResult': [],
                },
            },
        )


@pytest.fixture
def mock_balance_token_error(mockserver, request):
    @mockserver.json_handler('/direct/live/v4/json')
    def _mock_sessions(req):
        return mockserver.make_response(
            status=200,
            json={
                'error_str': 'Authorization error',
                'error_detail': '',
                'error_code': 53,
            },
        )


@pytest.fixture
def mock_rating_info_ok(mockserver, request):
    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1/places-rating-info',
    )
    def _mock_rating_info(request):
        return mockserver.make_response(
            status=200,
            json={
                'places_rating_info': [
                    {
                        'average_rating': 4.0,
                        'calculated_at': '2021-01-01',
                        'cancel_rating': 4.0,
                        'place_id': int(place_id),
                        'show_rating': True,
                        'user_rating': 4.0,
                    }
                    for place_id in request.query['place_ids'].split(',')
                ],
            },
        )


@pytest.fixture
def mock_rating_info_low(mockserver, request):
    @mockserver.json_handler(
        '/eats-place-rating/eats/v1/eats-place-rating/v1/places-rating-info',
    )
    def _mock_rating_info(request):
        return mockserver.make_response(
            status=200,
            json={
                'places_rating_info': [
                    {
                        'average_rating': 2.0,
                        'calculated_at': '2021-01-01',
                        'cancel_rating': 4.0,
                        'place_id': int(place_id),
                        'show_rating': True,
                        'user_rating': 4.0,
                    }
                    for place_id in request.query['place_ids'].split(',')
                ],
            },
        )


@pytest.fixture
def mock_places_handle(mockserver, request):
    @mockserver.json_handler(
        r'/eats-core/v1/places/(?P<place_id>\d+)', regex=True,
    )
    def _mock_places_handle(request, place_id):
        return mockserver.make_response(
            status=200,
            json={
                'is_success': True,
                'payload': {
                    'id': place_id,
                    'email': 'qqq@www.ru',
                    'name': 'рога и копыта',
                    'available': True,
                    'disable_details': {
                        'disable_at': '2020-11-27T11:00:00Z',
                        'available_at': '2020-11-27T11:00:00Z',
                        'last_call_date': '2020-11-27T11:00:00Z',
                        'status': 2,
                        'reason': 35,
                    },
                    'full_address': 'qwerty',
                    'description': 'qwerty good',
                    'currency_code': 'RUB',
                    'menu': [
                        {
                            'id': 1,
                            'name': 'бургöры №1',
                            'available': True,
                            'schedule_description': 'at 14:00',
                            'items': [],
                        },
                    ],
                    'phone_numbers': ['+79999999999'],
                    'show_shipping_time': True,
                    'integration_type': 'native',
                    'slug': 'slug',
                },
                'meta': {'count': None},
            },
        )


@pytest.fixture(name='eats_restapp_marketing_db')
def _eats_restapp_marketing_db(pgsql):
    return pgsql['eats_restapp_marketing']


@pytest.fixture(autouse=True)
def setup_markers(request, eats_restapp_marketing_db):
    # Регистрируем маркеры в одной фикстуре для того, чтобы
    # гарантировать строгий порядок записи сущностей в postrgresql

    setup_adverts_marker(request, eats_restapp_marketing_db)
    setup_campaigns_marker(request, eats_restapp_marketing_db)
    setup_banners_marker(request, eats_restapp_marketing_db)


def setup_adverts_marker(request, eats_restapp_marketing_db):
    marker = request.node.get_closest_marker('adverts')
    if marker:
        for item in marker.args:
            if not isinstance(item, sql.Advert):
                raise Exception(
                    f'invalid marker.adverts argument type {type(item)}',
                )
            sql.insert_advert(eats_restapp_marketing_db, item)


def setup_campaigns_marker(request, eats_restapp_marketing_db):
    marker = request.node.get_closest_marker('campaigns')
    if marker:
        for item in marker.args:
            if not isinstance(item, sql.Campaign):
                raise Exception(
                    f'invalid marker.campaigns argument type {type(item)}',
                )
            sql.insert_campaign(eats_restapp_marketing_db, item)


def setup_banners_marker(request, eats_restapp_marketing_db):
    marker = request.node.get_closest_marker('banners')
    if marker:
        for item in marker.args:
            if not isinstance(item, sql.Banner):
                raise Exception(
                    f'invalid marker.banners argument type {type(item)}',
                )
            sql.insert_banner(eats_restapp_marketing_db, item)


@pytest.fixture(name='mock_direct_campaigns')
def _mock_direct_campaigns(mockserver):
    def do_nothing(*args, **kwargs):
        pass

    class Context:
        def __init__(self):
            self.status = 200
            self.request_assertion_callback = do_nothing
            self.add_results = None

        def request_assertion(self, callback):
            self.request_assertion_callback = callback
            return callback

        def add_result(self, add_result: direct.IdResult) -> None:
            if not self.add_results:
                self.add_results = []
            self.add_results.append(add_result)

        def response(self) -> dict:
            add_results = [] if not self.add_results else self.add_results
            return {
                'result': {'AddResults': [r.asdict() for r in add_results]},
            }

        @property
        def times_called(self) -> int:
            return handler.times_called

    ctx = Context()

    @mockserver.json_handler('/direct/json/v5/campaignsext')
    def handler(request):
        ctx.request_assertion_callback(request)

        return mockserver.make_response(status=ctx.status, json=ctx.response())

    return ctx


@pytest.fixture(name='mock_direct_internal_tags')
def _mock_direct_internal_tags(mockserver):
    def do_nothing(*args, **kwargs):
        pass

    class Context:
        def __init__(self):
            self.status = 200
            self.request_assertion_callback = do_nothing
            self.tags = None

        def request_assertion(self, callback):
            self.request_assertion_callback = callback
            return callback

        def set_tags(self, tags: typing.List[str]) -> None:
            self.tags = tags

        @property
        def times_called(self) -> int:
            return handler.times_called

    ctx = Context()

    @mockserver.json_handler('/direct-internal/adgroup_bs_tags/eda_bs_tags')
    def handler(request):
        ctx.request_assertion_callback(request)

        groups = []
        for group_id in request.json['ad_group_ids']:
            groups.append({'ad_group_id': group_id, 'bs_tags': ctx.tags})

        return mockserver.make_response(
            status=ctx.status,
            json={
                'success': True,
                'validation_result': {'errors': []},
                'ad_group_bs_tags': groups,
            },
        )

    return ctx


@pytest.fixture(name='mock_direct_ads')
def _mock_direct_ads(mockserver):
    def do_nothing(*args, **kwargs):
        pass

    class Context:
        def __init__(self):
            self.status = 200
            self.request_assertion_callback = do_nothing
            self.update_results = []

        def request_assertion(self, callback):
            self.request_assertion_callback = callback
            return callback

        def set_update_results(self, results: typing.List[direct.IdResult]):
            self.update_results = results

        @property
        def times_called(self) -> int:
            return handler.times_called

    ctx = Context()

    @mockserver.json_handler('/direct/json/v5/ads')
    def handler(request):
        ctx.request_assertion_callback(request)

        return mockserver.make_response(
            status=ctx.status,
            json={
                'result': {
                    'UpdateResults': [r.asdict() for r in ctx.update_results],
                },
            },
        )

    return ctx
