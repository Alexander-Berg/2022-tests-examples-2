import typing

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_payment_methods_availability_plugins import *  # noqa: F403 F401
import pytest

TEST_ORDER_ID = 'test_order'
TEST_PAYMENT_ID = '27affbc7-de68-4a79-abba-d9bdf48e6e09'
TEST_CURRENCY = 'RUB'
TEST_CARGO_PAYMENT_REVISION = 1234
TEST_CARGO_PAYMENT_STATUS = 'new'
TEST_CARGO_PAYMENT_CREATED_AT = '2020-03-30T08:29:06+00:00'
TEST_DEFAULT_VIRTUAL_CLIENT_ID = 'b8671563-47fa-42ff-8159-4118eee9fb1f'
TEST_PERSONAL_PHONE_ID = '456'

ALL_POSSIBLE_PAYMENT_METHODS = [
    'add_new_card',
    'card',
    'applepay',
    'googlepay',
    'badge',
    'corp',
    'cash',
    'personal_wallet',
    'sbp',
    'yandex_bank',
    'create_yandex_bank',
]

LIST_PAYMENT_METHODS_RESPONSE_BASE: typing.Dict[str, typing.Any] = {
    'last_used_payment_method': {
        'id': 'badge:yandex_badge:RUB',
        'type': 'corp',
    },
    'payment_methods': [],
}


def make_set_of_payment_types_experiments(  # pylint: disable=invalid-name
        payment_types,
        all_available_payment_types,
        clause_predicate=None,
        visibility: dict = None,
        side_visibility: dict = None,
):
    payment_type_experiments = []
    for possible_payment_type in ALL_POSSIBLE_PAYMENT_METHODS:
        payment_experiment: dict = {
            'name': (
                'eats_payment_methods_availability_'
                + possible_payment_type
                + '_payment_method'
            ),
            'consumers': ['eats-payment-methods-availability/methods'],
            'match': {'predicate': {'type': 'true'}, 'enabled': True},
            'clauses': [
                {
                    'title': 'first clause',
                    'predicate': clause_predicate or {'type': 'true'},
                    'value': {
                        'name': possible_payment_type,
                        'is_available': (
                            possible_payment_type in payment_types
                        ),
                    },
                },
            ],
            'default_value': {
                'name': possible_payment_type,
                'is_available': (
                    possible_payment_type in all_available_payment_types
                ),
            },
        }

        if visibility is not None and possible_payment_type in visibility:
            is_visible = visibility[possible_payment_type]
            payment_experiment['clauses'][0]['value'][
                'is_visible'
            ] = is_visible
            payment_experiment['default_value']['is_visible'] = is_visible

        if side_visibility is not None:
            if possible_payment_type in side_visibility:
                is_side_visible = side_visibility[possible_payment_type]
                payment_experiment['clauses'][0]['value'][
                    'is_side_visible'
                ] = is_side_visible
                payment_experiment['default_value'][
                    'is_side_visible'
                ] = is_side_visible

        # print(payment_type_experiments)
        payment_type_experiments.append(payment_experiment)
    return payment_type_experiments


@pytest.fixture(name='exp_payment_methods')
def _exp_payment_methods(experiments3):
    def wrapper(
            payment_methods,
            all_available_payment_types=None,
            clause_predicate=None,
            visibility=None,
            side_visibility=None,
    ):
        if all_available_payment_types is None:
            all_available_payment_types = payment_methods
        experiments = make_set_of_payment_types_experiments(
            payment_methods,
            all_available_payment_types,
            clause_predicate,
            visibility,
            side_visibility,
        )
        for experiment in experiments:
            experiments3.add_config(**experiment)

    return wrapper


# pylint: disable=invalid-name
@pytest.fixture(name='mock_saturn')
def _mock_saturn(mockserver):
    def _inner(status: str):
        # pylint: disable=invalid-name
        @mockserver.json_handler('/saturn/api/v1/eda/search')
        def saturn_handler(request):
            return {
                'reqid': 'fff-785647',
                'puid': 76874335,
                'score': 100,
                'score_percentile': 90,
                'formula_id': '785833',
                'formula_description': 'bnpl_market',
                'data_source': 'puid/2021-06-21',
                'status': status,
            }

        return saturn_handler

    return _inner


@pytest.fixture(name='mock_api_proxy_4_list_payment_methods')
def mock_api_proxy_4_list_payment_methods_fixture(
        mockserver,
):  # pylint: disable=invalid-name
    def _mock_api_proxy_list_payment_methods(
            payment_methods=None,
            merchant_ids=None,
            merchant_id=None,
            service_token=None,
            country=False,
    ):
        @mockserver.json_handler(
            '/api-proxy-superapp-critical'
            '/4.0/payments/v1/list-payment-methods',
        )
        def _api_proxy_handler(request):
            response = {
                **LIST_PAYMENT_METHODS_RESPONSE_BASE,
                'payment_methods': (
                    [] if payment_methods is None else payment_methods
                ),
                'merchant_id_list': (
                    ['merchant.ru.yandex.ytaxi.trust']
                    if merchant_ids is None
                    else merchant_ids
                ),
            }
            if merchant_id is not None:
                response['merchant_id'] = merchant_id

            if service_token is not None:
                response['service_token'] = service_token

            if country is not None:
                response['region_id'] = country

            return response

        return _api_proxy_handler

    return _mock_api_proxy_list_payment_methods


@pytest.fixture(name='mock_corp_int_api_payment_methods_eats')
def mock_corp_int_api_payment_methods_eats_fixture(
        mockserver,
):  # pylint: disable=invalid-name
    def _mock_corp_int_api_payment_methods_eats(
            payment_methods, order_sum=None, snd_point=None, dst_point=None,
    ):
        @mockserver.json_handler(
            '/taxi-corp-integration/v1/payment-methods/eats',
        )
        def _corp_int_api_handler(request):
            if order_sum is not None:
                assert request.json == {
                    'order_sum': order_sum,
                    'currency': 'RUB',
                    'place_of_service_location': {'position': snd_point},
                    'place_of_user_location': {'position': dst_point},
                }
            return mockserver.make_response(
                status=200,
                json={'payment_methods': payment_methods},
                headers={'X-YaRequestId': 'conflict'},
            )

        return _corp_int_api_handler

    return _mock_corp_int_api_payment_methods_eats


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]


@pytest.fixture(name='mock_trust_payments_get')
def _mock_trust_payments_get(mockserver):
    def _inner(purchase_token):
        @mockserver.json_handler(
            '/trust-eda/trust-payments/v2/payments/' + purchase_token,
        )
        def transactions_create_invoice_handler(request):
            return mockserver.make_response(
                status=200,
                json={
                    '3ds_transaction_info': {
                        'redirect_url': (
                            'https://trust.yandex.ru/web/redirect_3ds?'
                            'purchase_token=c964a582b3b4b3dcd514ab1914a7d2a8'
                        ),
                        'process_url': (
                            'https://trust.yandex.ru/web/process_3ds?'
                            'purchase_token=c964a582b3b4b3dcd514ab1914a7d2a8'
                        ),
                        'status': 'wait_for_result',
                    },
                    'purchase_token': purchase_token,
                    'amount': '0.00',
                    'currency': 'RUB',
                    'payment_status': 'started',
                    'orders': [],
                },
            )

        return transactions_create_invoice_handler

    return _inner


def _make_response_40_lpm(
        payment_methods: typing.List[dict],
        merchant_ids=None,
        country_expected=False,
) -> dict:
    if merchant_ids is None:
        merchant_ids = ['merchant.ru.yandex.ytaxi.trust']

    response = {
        **LIST_PAYMENT_METHODS_RESPONSE_BASE,
        'payment_methods': payment_methods,
        'merchant_id_list': merchant_ids,
    }

    default_country_id = 225

    if country_expected:
        response['region_id'] = default_country_id

    return response


@pytest.fixture(name='mock_api_proxy_list_payment_methods')
def mock_api_proxy_list_payment_methods_fixture(
        mockserver,
):  # pylint: disable=invalid-name
    def _mock_api_proxy_list_payment_methods(payment_methods, error=None):
        @mockserver.json_handler(
            '/api-proxy-superapp-critical'
            '/4.0/payments/v1/list-payment-methods',
        )
        def _api_proxy_handler(request):
            if error is not None:
                return mockserver.make_response(
                    **{
                        'status': error,
                        'json': {
                            'code': 'internal-server-error',
                            'body': 'exception',
                        },
                    },
                )
            assert request.query == {
                'source': 'eats_payments',
                'service': 'eats',
            }

            expected_request = {}
            if 'sender_point' in request.json:
                expected_request = {
                    **expected_request,
                    'sender_point': request.json['sender_point'],
                }
            if 'destination_point' in request.json:
                expected_request = {
                    **expected_request,
                    'destination_point': request.json['destination_point'],
                }
            if 'location' in request.json:
                expected_request = {
                    **expected_request,
                    'location': request.json['location'],
                }

            assert request.json == expected_request
            return _make_response_40_lpm(
                payment_methods, country_expected=('location' in request.json),
            )

        return _api_proxy_handler

    return _mock_api_proxy_list_payment_methods


@pytest.fixture(name='mock_eats_payments_active_orders')
def mock_eats_payments_active_orders(
        mockserver,
):  # pylint: disable=invalid-name
    def _mock_eats_payments_active_orders(active_orders, error=None):
        @mockserver.json_handler('/eats-payments/v1/orders/active')
        def _active_orders_response(request):
            if error is not None:
                return mockserver.make_response(
                    **{
                        'status': error,
                        'json': {
                            'code': 'internal-server-error',
                            'body': 'exception',
                        },
                    },
                )
            return mockserver.make_response(
                **{'status': '200', 'json': active_orders},
            )

        return _active_orders_response

    return _mock_eats_payments_active_orders


@pytest.fixture(name='mock_cashback_calculator_calculate')
def mock_cashback_calculator_calculate(
        mockserver,
):  # pylint: disable=invalid-name
    def _mock_cashback_calculator_calculate():
        @mockserver.json_handler(
            '/bank-cashback-calculator/cashback-calculator/v1/calculate',
        )
        def _create_response():
            response = {
                'max_amount': '100',
                'percent': {'amount': '10'},
                'rule_ids': [],
            }
            return mockserver.make_response(
                **{'status': '200', 'json': response},
            )

        return _create_response

    return _mock_cashback_calculator_calculate
