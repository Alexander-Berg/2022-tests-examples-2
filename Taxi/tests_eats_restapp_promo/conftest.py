# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from eats_catalog_storage_cache import (  # noqa: F403 F401
    eats_catalog_storage_cache,  # noqa: F403 F401
)
from eats_restapp_promo_plugins import *  # noqa: F403 F401


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture fo service cache',
    )


@pytest.fixture
def mock_authorizer_allowed(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(status=200)


@pytest.fixture
def mock_authorizer_403(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'Forbidden',
                'details': {
                    'place_ids': request.json['place_ids'],
                    'permissions': [],
                },
            },
        )


@pytest.fixture
def mock_authorizer_403_no_perm(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=403,
            json={
                'code': '403',
                'message': 'Forbidden',
                'details': {
                    'place_ids': [],
                    'permissions': request.json['permissions'],
                },
            },
        )


@pytest.fixture
def mock_marketing_403(mockserver, request):
    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo',
    )
    def _mock_marketing(request):
        return mockserver.make_response(
            status=403, json={'code': '403', 'message': 'Marketing 403'},
        )


@pytest.fixture
def mock_marketing_400(mockserver, request):
    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo',
    )
    def _mock_marketing(request):
        return mockserver.make_response(
            status=400, json={'code': '400', 'message': 'Marketing 400'},
        )


@pytest.fixture
def mock_marketing_404(mockserver, request):
    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo',
    )
    def _mock_marketing(request):
        return mockserver.make_response(
            status=404, json={'code': '404', 'message': 'Marketing 404'},
        )


@pytest.fixture
def mock_discount_500(mockserver, request):
    @mockserver.json_handler('/eats-discounts/v1/partners/discounts/create')
    def _mock_eats_discounts(request):
        return mockserver.make_response(
            status=500, json={'code': '500', 'message': 'Discount 500'},
        )


@pytest.fixture
def mock_authorizer_400(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=400,
            json={'code': '400', 'message': 'Пользователь не найден'},
        )


@pytest.fixture
def mock_authorizer_500(mockserver, request):
    @mockserver.json_handler('/eats-restapp-authorizer/v1/user-access/check')
    def _mock_authorizer(request):
        return mockserver.make_response(
            status=500, json={'code': '500', 'message': 'Internal Error'},
        )


@pytest.fixture(name='plus_availability', autouse=True)
def mock_plus_availability(mockserver, request):
    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/plus_availability',
    )
    def _mock_plus_availability(request):
        latitude = request.query.get('latitude', None)
        longitude = request.query.get('longitude', None)
        region_id = request.query.get('region_id', None)

        if (
                latitude is not None
                and longitude is not None
                and [latitude, longitude] == [1.0, 1.0]
                or region_id is not None
                and region_id == '1'
        ):
            return mockserver.make_response(
                status=200, json={'is_available': True},
            )

        return mockserver.make_response(
            status=200, json={'is_available': False},
        )


@pytest.fixture(name='plus_settings_cashback', autouse=True)
def mock_plus_settings_cashback(mockserver, request):
    @mockserver.json_handler(
        '/eats-plus/internal/eats-plus/v1/settings/cashback',
    )
    def _mock_plus_settings_cashback(request):
        return mockserver.make_response(status=200)


@pytest.fixture(name='eats_plus_place_cashback', autouse=True)
def mock_eats_plus_place_cashback(mockserver, request):
    @mockserver.json_handler('/eats-plus/internal/eats-plus/v1/place/cashback')
    def _mock_eats_plus_place_cashback(request):
        return mockserver.make_response(status=404)


@pytest.fixture(name='login_salesforce', autouse=True)
def mock_login_salesforce(mockserver, request):
    @mockserver.json_handler('/login-salesforce/services/oauth2/token')
    def _mock_login_salesforce(request):
        return mockserver.make_response(
            status=200,
            json={
                'access_token': 'access_token',
                'instance_url': 'instance_url',
                'id': 'id',
                'token_type': 'Bearer',
                'issued_at': 'issued_at',
                'signature': 'signature',
            },
        )


@pytest.fixture(name='sf_create_commission', autouse=True)
def mock_sf_create_commission(mockserver, request):
    @mockserver.json_handler(
        '/salesforce-commission/services/apexrest/commission/createCommission',
    )
    def _mock_sf_create_commission(request):
        authorization = request.headers.get('Authorization', None)
        if authorization is None and authorization != 'Bearer access_token':
            return mockserver.make_response(status=400)

        return mockserver.make_response(status=200)


@pytest.fixture(name='sf_get_commission', autouse=True)
def mock_sf_get_commission(mockserver, request):
    @mockserver.json_handler(
        '/salesforce-commission/services/apexrest/commission/getCommission',
    )
    def _mock_sf_get_commission(request):
        authorization = request.headers.get('Authorization', None)
        if authorization is None and authorization != 'Bearer access_token':
            return mockserver.make_response(status=400)

        return mockserver.make_response(
            status=200,
            json=[
                {
                    'type': 'OD',
                    'status': 'Активна',
                    'startDate': '2020-06-05',
                    'placeId': 123,
                    'isEnabled': True,
                    'endDate': None,
                    'commissionFixed': None,
                    'commission': 35.00,
                    'acquiring': 0.0,
                },
            ],
        )


@pytest.fixture(name='eats_restapp_marketing_create_promo', autouse=True)
def marketing_create_promo(mockserver, request):
    @mockserver.json_handler(
        '/eats-restapp-marketing/4.0/restapp-front/marketing/v1/promo',
    )
    def _mock_marketing_create_promo(request):
        response_body = None
        if request.json['type'] == 'gift':
            response_body = {
                'bonuses': [{'item_id': '100'}],
                'description': (
                    'Познакомить пользователей с '
                    'новыми блюдами или поднять средний чек.'
                ),
                'ends_at': '2020-08-28T20:11:25+00:00',
                'id': 228,
                'name': 'Блюдо в подарок',
                'place_ids': [41, 42, 43],
                'requirements': [{'min_order_price': 10}],
                'schedule': [
                    {'day': 2, 'from': 60, 'to': 180},
                    {'day': 7, 'from': 1000, 'to': 1030},
                ],
                'starts_at': '2020-08-28T12:11:25+00:00',
                'status': 'new',
                'type': 'gift',
            }
        if request.json['type'] == 'discount':
            response_body = {
                'bonuses': [{'discount': 10}],
                'description': (
                    'Увеличить выручку ресторана или поднять средний чек.'
                ),
                'ends_at': '2020-08-28T20:11:25+00:00',
                'id': 1,
                'name': 'Скидка на меню или некоторые позиции',
                'place_ids': [41, 42, 43],
                'starts_at': '2020-08-28T12:11:25+00:00',
                'status': 'new',
                'type': 'discount',
                'requirements': [
                    {
                        'category_ids': [1, 2, 3],
                        'item_ids': ['biba', 'boba', 'aboba'],
                    },
                ],
                'schedule': [
                    {'day': 2, 'from': 60, 'to': 180},
                    {'day': 7, 'from': 1000, 'to': 1030},
                ],
            }
        if request.json['type'] == 'one_plus_one':
            response_body = {
                'bonuses': [],
                'schedule': [
                    {'day': 2, 'from': 60, 'to': 180},
                    {'day': 7, 'from': 1000, 'to': 1030},
                ],
                'description': (
                    'Увеличить количество заказов или '
                    'познакомить пользователей c новыми блюдами.'
                ),
                'ends_at': '2020-08-28T20:11:25+00:00',
                'id': 1,
                'name': 'Два по цене одного',
                'place_ids': [41, 42, 43],
                'starts_at': '2020-08-28T12:11:25+00:00',
                'status': 'new',
                'type': 'one_plus_one',
                'requirements': [{'item_ids': ['biba', 'boba', 'aboba']}],
            }
        return mockserver.make_response(status=200, json=response_body)


@pytest.fixture(name='eats_discounts_create_promo', autouse=True)
def eats_discounts_create_promo(mockserver, request):
    @mockserver.json_handler('/eats-discounts/v1/partners/discounts/create')
    def _mock_eats_discounts_create_promo(request):
        response_body = {'task_id': '12345678-1234-1234-1234-123412345678'}
        return mockserver.make_response(status=200, json=response_body)


@pytest.fixture(name='eats_discounts_finish', autouse=True)
def eats_discounts_finish(mockserver, request):
    @mockserver.json_handler('/eats-discounts/v1/partners/discounts/finish')
    def _mock_eats_discounts_finish(request):
        return mockserver.make_response(status=200)


@pytest.fixture(name='eats_discounts_task_statuses', autouse=True)
def eats_discounts_task_statuses(mockserver, request):
    @mockserver.json_handler(
        '/eats-discounts/v1/partners/discounts/get-tasks-status',
    )
    def _mock_eats_discounts_task_statuses(request):
        return mockserver.make_response(
            status=200,
            json={
                'tasks_status': [
                    {
                        'status': 'finished',
                        'task_id': 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaa01',
                        'task_result': {
                            'create_discounts': {
                                'affected_discount_ids': ['6'],
                                'inserted_discount_ids': ['3'],
                            },
                        },
                        'time': '2021-01-02T00:00:00+00:00',
                    },
                ],
            },
        )


@pytest.fixture
def mock_partners_info_200(mockserver, request):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_func(request):
        assert (
            request.query['partner_id'] == '1'
            or request.query['partner_id'] == '2'
        )
        response_body = {
            'payload': {
                'id': 1,
                'name': 'huba@huba.hub',
                'email': 'huba@huba.hub',
                'is_blocked': False,
                'places': [162, 7323, 305733, 475484],
                'is_fast_food': False,
                'timezone': 'Europe/Moscow',
                'country_code': 'RU',
                'roles': [
                    {'id': 1, 'slug': 'ROLE_OPERATOR', 'title': 'Оператор'},
                    {'id': 2, 'slug': 'ROLE_MANAGER', 'title': 'Управляющий'},
                ],
                'partner_id': '4bccba0a-ddb4-4f92-a45f-6123582e7e8c',
            },
        }
        return mockserver.make_response(status=200, json=response_body)

    return _mock_func


@pytest.fixture
def mock_partners_info(mockserver, request):
    @mockserver.json_handler('/eats-partners/internal/partners/v1/info')
    def _mock_func(request):
        assert request.query['partner_id'] == '1'
        response_body = {
            'payload': {
                'id': 1,
                'name': 'name1',
                'email': 'email1@yandex.ru',
                'is_blocked': False,
                'places': [1, 2],
                'is_fast_food': False,
                'timezone': 'Europe/Moscow',
                'country_code': 'RU',
                'roles': [
                    {'id': 1, 'slug': 'ROLE_OPERATOR', 'title': 'Оператор'},
                    {'id': 2, 'slug': 'ROLE_MANAGER', 'title': 'Управляющий'},
                ],
                'partner_id': '4bccba0a-ddb4-4f92-a45f-6123582e7e8c',
            },
        }
        return mockserver.make_response(status=200, json=response_body)

    return _mock_func


@pytest.fixture
def mock_eats_restapp_core(mockserver, request):
    @mockserver.json_handler(
        '/eats-core-restapp/v1/eats-restapp-menu/place-menu',
    )
    def _mock_eats_restapp_core_place_menu(request):
        response_body = {
            'is_success': True,
            'payload': {
                'menu': {
                    'categories': [
                        {'id': '1', 'name': 'Каша', 'available': True},
                        {'id': '6', 'name': 'Напитки', 'available': True},
                    ],
                    'items': [
                        {
                            'id': '1',
                            'categoryId': '1',
                            'name': 'Греча',
                            'price': 1.0,
                            'available': True,
                            'menuItemId': 100,
                        },
                        {
                            'id': '3',
                            'categoryId': '3',
                            'name': '3',
                            'price': 3.0,
                            'available': True,
                            'menuItemId': 300,
                        },
                        {
                            'id': '4',
                            'categoryId': '4',
                            'name': '4',
                            'price': 4.0,
                            'available': True,
                            'menuItemId': 400,
                        },
                        {
                            'id': '5',
                            'categoryId': '5',
                            'name': '5',
                            'price': 5.0,
                            'available': True,
                            'menuItemId': 500,
                        },
                        {
                            'id': '6',
                            'categoryId': '6',
                            'name': '6',
                            'price': 6.0,
                            'available': True,
                            'menuItemId': 600,
                        },
                        {
                            'id': '8',
                            'categoryId': '6',
                            'name': '8',
                            'price': 8.0,
                            'available': True,
                        },
                        {
                            'id': '10',
                            'categoryId': '10',
                            'name': '10',
                            'price': 10.0,
                            'available': True,
                            'menuItemId': 1000,
                        },
                    ],
                },
            },
        }
        return mockserver.make_response(status=200, json=response_body)

    @mockserver.json_handler(
        '/eats-core-restapp/v1/places-receipts/get-average',
    )
    def _mock_eats_restapp_core_get_average(request):
        assert request.headers['X-YaEda-PartnerId'] == '1'
        response_body = {
            'payload': [
                {'place_id': 1, 'average_cheque': 900},
                {'place_id': 2, 'average_cheque': 920},
                {'place_id': 3, 'average_cheque': 940},
            ],
        }
        return mockserver.make_response(status=200, json=response_body)
