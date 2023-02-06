# pylint: disable=wildcard-import, unused-wildcard-import, import-error

from coupons_plugins import *  # noqa: F403 F401
import pytest  # pylint: disable=wrong-import-order

from tests_coupons import util
from tests_coupons.referral import util as referral_util


@pytest.fixture
def mongo_db(mongodb):
    return mongodb


@pytest.fixture
def referrals_postgres_db(pgsql):
    return pgsql[referral_util.REFERRALS_DB_NAME].cursor()


@pytest.fixture(name='local_services')
def _local_services(mockserver, load_json, testpoint):
    class Context:
        cards = {'available_cards': []}
        do_check_service_type = False

        mock_cardstorage = None
        mock_user_statistics = None
        mock_user_api = None

        cardstorage_requests = []

        service_type_by_brand = None
        application_map_brand = None
        app_name = None

        sample_card = {
            'valid': True,
            'permanent_card_id': 'permanent_card_id',
            'system': 'VISA',
            'billing_card_id': 'billing_card_id',
            'currency': 'rub',
            'region_id': '181',
            'expiration_year': 2050,
            'expiration_month': 6,
            'card_id': 'card_id',
            'number': '111111***',
            'persistent_id': 'persistent_id',
            'possible_moneyless': False,
            'regions_checked': [],
            'owner': '456',
            'bound': True,
            'unverified': False,
            'from_db': False,
            'busy': False,
            'busy_with': [],
        }
        sample_ya_card = {
            'id': 'ya_card_id',
            'currency': 'RUB',
            'is_hidden': False,
        }

        user_statistics = {
            'data': [
                {
                    'identity': {
                        'type': 'phone_id',
                        'value': '5bbb5faf15870bd76635d5e2',
                    },
                    'counters': [],
                },
            ],
        }

        sample_user_api = {
            'apns_token': 'apns_token',
            'gcm_token': 'gcm_token',
            'device_id': 'device_id',
        }
        user_api = sample_user_api

        def add_card(self):
            self.cards['available_cards'] = [Context.sample_card]

        def add_card_and_ya_card(self):
            self.cards['available_cards'] = [Context.sample_card]

            self.cards['yandex_cards'] = {}
            self.cards['yandex_cards']['available_cards'] = [
                Context.sample_ya_card,
            ]

        def check_service_type(
                self,
                billing_service_name_map_by_brand,
                application_map_brand,
                app_name,
        ):
            self.do_check_service_type = True
            self.service_type_by_brand = billing_service_name_map_by_brand
            self.application_map_brand = application_map_brand
            self.app_name = app_name

    context = Context()

    @testpoint('cardstorage_request')
    def _testpoint_cardstorage(data):
        context.cardstorage_requests.append(data)

    @mockserver.json_handler('/cardstorage/v1/payment_methods')
    def _mock_cardstorage(request):
        if context.do_check_service_type:
            default_brand = context.application_map_brand.get(
                '__dafault__', 'unknown',
            )
            brand = context.application_map_brand.get(
                context.app_name, default_brand,
            )
            default_service_type = context.service_type_by_brand.get(
                '__default__', 'unknown',
            )
            service_type = context.service_type_by_brand.get(
                brand, default_service_type,
            )
            assert request.json['service_type'] == service_type

        return context.cards

    @mockserver.json_handler('/user-statistics/v1/orders')
    def _mock_user_statistics(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        return context.user_statistics

    @mockserver.json_handler('/user-api/users/get')
    def _mock_user_api(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        user_id = request.json['id']
        result = context.user_api.copy()
        result['id'] = user_id
        return result

    @mockserver.json_handler('/grocery-coupons/internal/v1/coupons/validate')
    def _mock_grocery_coupons(request):
        return {
            'valid': True,
            'valid_any': True,
            'descriptions': [],
            'details': [],
        }

    context.mock_cardstorage = _mock_cardstorage
    context.mock_user_statistics = _mock_user_statistics
    context.mock_user_api = _mock_user_api

    return context


@pytest.fixture(name='local_services_card')
def _local_services_card(local_services):
    local_services.add_card()
    return local_services


@pytest.fixture(name='user_statistics_services')
def _user_statistics_services(mockserver):
    class Context:
        mock_user_statistics = None

        user_statistics = {
            'data': [
                {
                    'identity': {
                        'type': 'phone_id',
                        'value': referral_util.REFERRAL_USER_PHONE_ID,
                    },
                    'counters': [
                        {
                            'properties': [
                                {'name': 'tariff_class', 'value': 'econom'},
                            ],
                            'value': 3,
                            'counted_from': '2020-09-01T11:01:55+0000',
                            'counted_to': '2020-09-03T09:24:18.807+0000',
                        },
                    ],
                },
            ],
        }

        def set_total_rides(self, num_rides):
            self.user_statistics['data'][0]['counters'][0]['value'] = num_rides

        def set_detailed_rides(
                self, num_rides, tariff_class='econom', payment_type='cash',
        ):
            self.user_statistics['data'][0]['counters'][0]['value'] = num_rides
            self.user_statistics['data'][0]['counters'][0]['properties'] = [
                {'name': 'tariff_class', 'value': tariff_class},
                {'name': 'payment_type', 'value': payment_type},
            ]

        def set_phone_id(self, phone_id):
            self.user_statistics['data'][0]['identity']['value'] = phone_id

        def add_counter(self, identity, value):
            self.user_statistics['data'].append(
                {
                    'identity': identity,
                    'counters': [
                        {
                            'properties': [
                                {'name': 'tariff_class', 'value': 'econom'},
                                {'name': 'payment_type', 'value': 'card'},
                            ],
                            'value': value,
                            'counted_from': '2020-09-01T11:01:55+0000',
                            'counted_to': '2020-09-03T09:24:18.807+0000',
                        },
                    ],
                },
            )

    context = Context()

    @mockserver.json_handler('/user-statistics/v1/orders')
    def _mock_user_statistics(request):
        assert 'X-Ya-Service-Ticket' in request.headers
        return context.user_statistics

    context.mock_user_statistics = _mock_user_statistics

    return context


class EdaApiContext:
    def __init__(self):
        self.grocery_response = {
            'value': {
                'type': 'total',
                'discount_currency': 'RUB',
                'discount_total': 777,
            },
            'code': 'total_grocery_ref',
            'limit': 500,
            'usages': 0,
        }
        self.status = 200

    def set_error(self, status=500):
        self.grocery_response = {
            'code': status,
            'status': 'error',
            'message': 'error',
        }
        self.status = status

    def set_grocery_response(self, response=None):
        self.grocery_response = response or {}
        self.status = 200


@pytest.fixture(name='eda_promocodes')
def _eda_promocodes(mockserver):
    handler = '/eda-promocodes/internal-api/v1/promocodes/referral/retrieve'
    context = EdaApiContext()

    @mockserver.json_handler(handler)
    def _mock_eda_api(request):
        if context.status == util.TIMEOUT:
            raise mockserver.TimeoutError()

        return mockserver.make_response(
            status=context.status, json=context.grocery_response,
        )

    return context


@pytest.fixture(name='eats_local_server')
def _eats_local_server(
        mockserver,
        request,
        valid,
        eats_result_code,
        error_code,
        promocode_type,
        yandex_uids,
        services,
):
    @mockserver.json_handler('/eats-promocodes/promocodes/superapp/validate')
    def _mock_validate(request):
        assert yandex_uids == request.json['passport_uids']
        assert len(request.json['promocodes']) == 1
        code = request.json['promocodes'][0]

        if eats_result_code == 200:
            if valid is not None and not error_code:
                response = {
                    'results': [
                        {
                            'valid': valid,
                            'promocode': {
                                'code': code,
                                'services': services if services else ['eda'],
                                'constraints': [
                                    {
                                        'type': 'first_order',
                                        'title': 'Промокод на первый заказ',
                                    },
                                ],
                            },
                        },
                    ],
                }

                result_promocode = response['results'][0]
                if promocode_type == 'fixed':
                    result_promocode['promocode']['value'] = {
                        'type': promocode_type,
                        'discount': '100',
                        'currency': 'RUB',
                    }
                elif promocode_type == 'percent':
                    result_promocode['promocode']['value'] = {
                        'type': promocode_type,
                        'discount': '20',
                        'discount_limit': '20000',
                    }
                elif promocode_type == 'text':
                    result_promocode['promocode']['value'] = {
                        'type': promocode_type,
                        'description': 'Подарок за первый заказ',
                    }
            elif error_code:
                response = {
                    'results': [
                        {
                            'valid': valid,
                            'promocode': {'code': 'eda12345'},
                            'error_code': error_code,
                        },
                    ],
                }
            else:
                response = {'results': []}

        elif eats_result_code == 401:
            response = {'code': 1, 'error': 'Invalid Service Ticket'}

        else:
            response = {'message': 'Something bad happened', 'status': 'error'}

        return mockserver.make_response(status=eats_result_code, json=response)
