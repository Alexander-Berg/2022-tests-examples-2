# pylint: disable=too-many-lines
import json
from typing import Optional

import pytest

from . import conftest


@pytest.mark.parametrize('total_fixed_price', [True, False])
@pytest.mark.parametrize(
    'claim_items, save_cars_request',
    [
        (
            [
                {
                    'id': 123,
                    'extra_id': '123',
                    'pickup_point': 1,
                    'droppof_point': 2,
                    'title': 'Холодильник карманный',
                    'size': {'length': 0.1, 'width': 0.2, 'height': 0.3},
                    'weight': 5,
                    'quantity': 1,
                    'cost_value': '10.20',
                    'cost_currency': 'RUR',
                },
            ],
            {
                'cars': [
                    {
                        'taxi_class': 'express',
                        'items': [{'id': 123, 'quantity': 1}],
                        'taxi_requirements': {'door_to_door': True},
                    },
                ],
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price': '999.001',
                    'price_raw': 999,
                },
                'zone_id': 'moscow',
                'is_delayed': False,
                'eta': 30,
                'currency': 'RUB',
                'currency_rules': conftest.get_currency_rules(),
            },
        ),
    ],
)
async def test_stq_run(
        mockserver,
        stq_runner,
        claim_items,
        save_cars_request,
        mock_claims_full,
        total_fixed_price,
        mock_int_api_profile,
):
    mock_claims_full.response['items'] = claim_items

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        body = json.loads(request.get_data())
        assert body == save_cars_request

        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json == {
            'sourceid': 'cargo',
            'selected_class': 'express',
            'user': {
                'personal_phone_id': 'personal_phone_id_123',
                'user_id': 'taxi_user_id_1',
            },
            'payment': {
                'payment_method_id': 'corp-corp_client_id_12312312312312312',
                'type': 'corp',
            },
            'requirements': {'door_to_door': True},
            'route': [[37.1, 55.1], [37.2, 55.3]],
        }
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': total_fixed_price,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [
                {
                    'time_raw': 30,
                    'class': 'express',
                    'price_raw': 999.001,
                    'is_fixed_price': True,
                },
            ],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')

    assert mock_claims_full.mock.times_called == 1
    assert dummy_save_result.times_called == 1


async def test_stq_new_pricing(
        mockserver,
        stq_runner,
        mock_claims_full,
        default_pricing_response,
        exp3_pricing_enabled,
        exp3_offer_ttl_enabled,
        mock_int_api_profile,
):
    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc')
    def _cargo_pricing(request):
        assert (
            request.json['idempotency_token']
            == 'claim_id_1_2020-03-31T18:35:00+0000'
        )
        return default_pricing_response

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        assert request.json['offer_ttl'] == 5
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert dummy_save_result.times_called == 1


@pytest.mark.config(CARGO_MATCHER_ENABLE_PRICING_PHOENIX=True)
@pytest.mark.parametrize(
    'pricing_payment_method, ' 'expected_method_id, expected_pricing_methods',
    [
        pytest.param(
            'card',
            'card-xxx',
            {
                'card': {
                    'cardstorage_id': 'card-xxx',
                    'owner_yandex_uid': 'yandex_uid-yyy',
                },
            },
            id='card',
        ),
        pytest.param(
            'corp',
            'corp-corp_client_id_12312312312312312',
            None,
            id='contract',
        ),
    ],
)
async def test_estimate_with_phoenix(
        mockserver,
        stq_runner,
        mock_claims_full,
        default_pricing_response,
        exp3_pricing_enabled,
        exp3_offer_ttl_enabled,
        mocker_tariff_current,
        mock_int_api_profile,
        load_json,
        pricing_payment_method,
        expected_method_id,
        expected_pricing_methods,
):
    mocker_tariff_current()

    expected_payment_info = {
        'type': pricing_payment_method,
        'method_id': expected_method_id,
    }

    finance_payment_methods = load_json(
        'finance_payments_response_{}.json'.format(pricing_payment_method),
    )

    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc')
    def _cargo_pricing(request):
        assert request.json['payment_info'] == expected_payment_info
        return default_pricing_response

    mock_claims_full.response['features'] = [
        {'id': 'phoenix_claim'},
        {'id': 'phoenix_corp'},
        {'id': 'agent_scheme'},
    ]

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        if expected_pricing_methods:
            assert (
                request.json['pricing_payment_methods']
                == expected_pricing_methods
            )
        else:
            assert 'pricing_payment_methods' not in request.json
        assert 'failure_reason' not in request.json
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/payment-methods/v1',
    )
    def dummy_get_payment_methods(request):
        assert request.json == {'yandex_uid': '123'}
        return finance_payment_methods

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert dummy_save_result.times_called == 1


@pytest.mark.config(CARGO_MATCHER_ENABLE_PRICING_PHOENIX=True)
@pytest.mark.parametrize(
    'cargo_finance_response, expected_finish_estimate_request',
    [
        pytest.param(
            {
                'methods': [
                    {
                        'id': (
                            'cargocorp:corp_client_id_12312312312312312:'
                            'card:456:789'
                        ),
                        'display': {
                            'type': 'cargocorp',
                            'image_tag': 'corpcard',
                            'title': 'Corp',
                            'disable_reason': {
                                'code': 'outstanding_debt',
                                'message': 'Debt',
                                'details': {},
                            },
                        },
                        'details': {
                            'type': 'corpcard',
                            'cardstorage_id': 'card-xxx',
                            'owner_yandex_uid': 'yandex_uid-yyy',
                            'is_disabled': True,
                        },
                    },
                ],
            },
            {
                'cars': [],
                'failure_reason': 'estimating.cargocorp_payment_failure',
                'failure_message': 'Debt',
            },
            id='phoenix has debts',
        ),
        pytest.param(
            {'methods': []},
            {
                'cars': [],
                'failure_reason': 'estimating.cargocorp_payment_failure',
                'failure_message': 'Отсутствует способ оплаты',
            },
            id='phoenix has no payment methods',
        ),
    ],
)
async def test_estimate_with_phoenix_fails(
        mockserver,
        stq_runner,
        mock_claims_full,
        default_pricing_response,
        exp3_pricing_enabled,
        exp3_offer_ttl_enabled,
        mocker_tariff_current,
        cargo_finance_response,
        mock_int_api_profile,
        expected_finish_estimate_request,
):
    mocker_tariff_current()

    mock_claims_full.response['features'] = [
        {'id': 'phoenix_claim'},
        {'id': 'phoenix_corp'},
        {'id': 'agent_scheme'},
    ]

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        assert request.json == expected_finish_estimate_request
        return {
            'id': 'claim_id_1',
            'status': 'estimating_failed',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler(
        '/cargo-finance/internal/cargo-finance/payment-methods/v1',
    )
    def dummy_get_payment_methods(request):
        assert request.json == {'yandex_uid': '123'}
        return mockserver.make_response(
            json=cargo_finance_response,
            status=cargo_finance_response.get('code', 200),
        )

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert dummy_save_result.times_called == 1


@pytest.mark.config(
    CARGO_TYPE_LIMITS={
        'van': {
            'carrying_capacity_max_kg': 2001,
            'carrying_capacity_min_kg': 300,
            'height_max_cm': 201,
            'height_min_cm': 90,
            'length_max_cm': 290,
            'length_min_cm': 170,
            'width_max_cm': 201,
            'width_min_cm': 96,
        },
        'lcv_m': {
            'carrying_capacity_max_kg': 6000,
            'carrying_capacity_min_kg': 700,
            'height_max_cm': 230,
            'height_min_cm': 150,
            'length_max_cm': 520,
            'length_min_cm': 260,
            'width_max_cm': 230,
            'width_min_cm': 130,
        },
    },
)
@pytest.mark.parametrize(
    'baggage_use_percentage, save_cars_request, '
    'estimate_request, estimate_response',
    [
        (
            0.75,
            {
                'cars': [
                    {
                        'taxi_class': 'express',
                        'items': [{'id': 123, 'quantity': 1}],
                        'taxi_requirements': {'door_to_door': True},
                    },
                ],
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price': '999.001',
                    'price_raw': 999,
                },
                'zone_id': 'moscow',
                'is_delayed': False,
                'currency': 'RUB',
                'currency_rules': conftest.get_currency_rules(),
            },
            {
                'sourceid': 'cargo',
                'selected_class': 'express',
                'user': {
                    'personal_phone_id': 'personal_phone_id_123',
                    'user_id': 'taxi_user_id_1',
                },
                'payment': {
                    'payment_method_id': (
                        'corp-corp_client_id_12312312312312312'
                    ),
                    'type': 'corp',
                },
                'requirements': {'door_to_door': True},
                'route': [[37.1, 55.1], [37.2, 55.3]],
            },
            {
                'offer': 'taxi_offer_id_1',
                'is_fixed_price': True,
                'currency_rules': conftest.get_currency_rules(),
                'service_levels': [{'class': 'express', 'price_raw': 999.001}],
            },
        ),
        (
            0.1,
            {
                'cars': [
                    {
                        'taxi_class': 'cargo',
                        'taxi_requirements': {'cargo_type': 'van'},
                        'items': [{'id': 123, 'quantity': 1}],
                    },
                ],
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price': '999.001',
                    'price_raw': 999,
                },
                'zone_id': 'moscow',
                'is_delayed': False,
                'currency': 'RUB',
                'currency_rules': conftest.get_currency_rules(),
            },
            {
                'sourceid': 'cargo',
                'selected_class': 'cargo',
                'user': {
                    'personal_phone_id': 'personal_phone_id_123',
                    'user_id': 'taxi_user_id_1',
                },
                'payment': {
                    'payment_method_id': (
                        'corp-corp_client_id_12312312312312312'
                    ),
                    'type': 'corp',
                },
                'requirements': {'cargo_type': 'van'},
                'route': [[37.1, 55.1], [37.2, 55.3]],
            },
            {
                'offer': 'taxi_offer_id_1',
                'is_fixed_price': True,
                'currency_rules': conftest.get_currency_rules(),
                'service_levels': [{'class': 'cargo', 'price_raw': 999.001}],
            },
        ),
        (
            0.03,
            conftest.get_finish_estimate_request(),
            {
                'sourceid': 'cargo',
                'selected_class': 'cargo',
                'user': {
                    'personal_phone_id': 'personal_phone_id_123',
                    'user_id': 'taxi_user_id_1',
                },
                'payment': {
                    'payment_method_id': (
                        'corp-corp_client_id_12312312312312312'
                    ),
                    'type': 'corp',
                },
                'requirements': {'cargo_type': 'lcv_m'},
                'route': [[37.1, 55.1], [37.2, 55.3]],
            },
            {
                'offer': 'taxi_offer_id_1',
                'is_fixed_price': True,
                'currency_rules': conftest.get_currency_rules(),
                'service_levels': [{'class': 'cargo', 'price_raw': 999.001}],
            },
        ),
    ],
)
async def test_baggage_percentage(
        mockserver,
        stq_runner,
        taxi_config,
        baggage_use_percentage,
        save_cars_request,
        estimate_request,
        estimate_response,
        mock_claims_full,
        mock_int_api_profile,
):
    taxi_config.set_values(
        dict(
            CARGO_MATCHER_PERCENTAGE_OF_BAGGAGE_VOLUME=baggage_use_percentage,
        ),
    )

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):
        body = json.loads(request.get_data())
        assert body == save_cars_request

        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json == estimate_request
        return estimate_response

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


@pytest.mark.parametrize(
    'client_requirements',
    [None, {'taxi_class': 'cargo', 'cargo_type': 'lcv_m'}],
)
async def test_required_tariffs_are_not_available(
        mockserver,
        stq_runner,
        mock_claims_full,
        client_requirements: Optional[dict],
):
    if client_requirements:
        mock_claims_full.response['client_requirements'] = client_requirements

    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _dummy_get_tariff(request):
        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': [],
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):
        body = json.loads(request.get_data())
        assert body == {
            'cars': [],
            'failure_reason': 'estimating.tariff.no_categories',
        }

        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


@pytest.mark.config(
    CARGO_TYPE_LIMITS={
        'lcv_m': {
            'carrying_capacity_max_kg': 6000,
            'carrying_capacity_min_kg': 700,
            'height_max_cm': 230,
            'height_min_cm': 150,
            'length_max_cm': 520,
            'length_min_cm': 260,
            'width_max_cm': 230,
            'width_min_cm': 130,
        },
    },
)
@pytest.mark.parametrize(
    'claim_items, save_cars_request',
    [
        (
            [
                {
                    'id': 123,
                    'extra_id': '123',
                    'pickup_point': 1,
                    'droppof_point': 2,
                    'title': 'Холодильник карманный',
                    'size': {'length': 0.1, 'width': 0.2, 'height': 0.3},
                    'weight': 5,
                    'quantity': 1,
                    'cost_value': '10.20',
                    'cost_currency': 'RUR',
                },
            ],
            {
                'cars': [
                    {
                        'taxi_class': 'express',
                        'items': [{'id': 123, 'quantity': 1}],
                        'taxi_requirements': {'door_to_door': True},
                    },
                ],
                'zone_id': 'moscow',
                'is_delayed': False,
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price': '999.001',
                    'price_raw': 999,
                },
                'currency': 'RUB',
                'currency_rules': conftest.get_currency_rules(),
            },
        ),
        (
            [
                {
                    'id': 123,
                    'extra_id': '123',
                    'pickup_point': 1,
                    'droppof_point': 2,
                    'title': 'Холодильник карманный',
                    'size': {'length': 1, 'width': 1, 'height': 1},
                    'weight': 5,
                    'quantity': 1,
                    'cost_value': '10.20',
                    'cost_currency': 'RUR',
                },
            ],
            {
                'cars': [],
                'failure_reason': 'estimating.permitted_tariffs_not_enough',
                'items_comments': [
                    {'id': 123, 'comment': 'estimating.too_large_item'},
                ],
            },
        ),
        (
            [
                {
                    'id': 123,
                    'extra_id': '123',
                    'pickup_point': 1,
                    'droppof_point': 2,
                    'title': 'Холодильник карманный',
                    'size': {'length': 100, 'width': 100, 'height': 100},
                    'weight': 5,
                    'quantity': 1,
                    'cost_value': '10.20',
                    'cost_currency': 'RUR',
                },
            ],
            {
                'cars': [],
                'failure_reason': 'estimating.too_large_item',
                'items_comments': [
                    {'id': 123, 'comment': 'estimating.too_large_item'},
                ],
            },
        ),
    ],
)
async def test_express_tariff_available(
        mockserver,
        stq_runner,
        load_json,
        claim_items,
        mock_claims_full,
        save_cars_request,
        mock_int_api_profile,
):
    mock_claims_full.response['items'] = claim_items

    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _dummy_get_tariff(request):
        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': load_json('express_category.json'),
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):
        body = json.loads(request.get_data())
        assert body == save_cars_request

        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json == {
            'sourceid': 'cargo',
            'selected_class': 'express',
            'user': {
                'personal_phone_id': 'personal_phone_id_123',
                'user_id': 'taxi_user_id_1',
            },
            'payment': {
                'payment_method_id': 'corp-corp_client_id_12312312312312312',
                'type': 'corp',
            },
            'requirements': {'door_to_door': True},
            'route': [[37.1, 55.1], [37.2, 55.3]],
        }
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [{'class': 'express', 'price_raw': 999.001}],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


async def test_long_route(
        mockserver,
        stq_runner,
        mock_claims_full,
        load_json,
        mock_int_api_profile,
):
    mock_claims_full.response['route_points'] = [
        {
            'id': 100,
            'address': {'fullname': '', 'coordinates': [1, 1]},
            'contact': {
                'personal_phone_id': 'personal_phone_id_123',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Petya',
            },
            'type': 'source',
            'visit_order': 1,
            'visit_status': 'pending',
            'visited_at': {},
        },
        {
            'id': 10,
            'address': {'fullname': '', 'coordinates': [3, 3]},
            'contact': {
                'personal_phone_id': 'personal_phone_id_456',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Vasya',
            },
            'type': 'destination',
            'visit_order': 3,
            'visit_status': 'pending',
            'visited_at': {},
        },
        {
            'id': 4,
            'address': {'fullname': '', 'coordinates': [4, 4]},
            'contact': {
                'personal_phone_id': 'personal_phone_id_456',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Vasya',
            },
            'type': 'source',
            'visit_order': 4,
            'visit_status': 'pending',
            'visited_at': {},
        },
        {
            'id': 2,
            'address': {'fullname': '', 'coordinates': [2, 2]},
            'contact': {
                'personal_phone_id': 'personal_phone_id_456',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Vasya',
            },
            'type': 'source',
            'visit_order': 2,
            'visit_status': 'pending',
            'visited_at': {},
        },
        {
            'id': 5,
            'address': {'fullname': '', 'coordinates': [5, 5]},
            'contact': {
                'personal_phone_id': 'personal_phone_id_456',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Vasya',
            },
            'type': 'destination',
            'visit_order': 5,
            'visit_status': 'pending',
            'visited_at': {},
        },
        {
            'id': 6,
            'address': {'fullname': '', 'coordinates': [100, 100]},
            'contact': {
                'personal_phone_id': 'personal_phone_id_456',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Vasya',
            },
            'type': 'return',
            'visit_order': 6,
            'visit_status': 'pending',
            'visited_at': {},
        },
    ]

    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _dummy_get_tariff(request):
        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': load_json('express_category.json'),
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json['route'] == [
            [1, 1],
            [2, 2],
            [3, 3],
            [4, 4],
            [5, 5],
        ]
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'service_levels': [{'class': 'express', 'price_raw': 999}],
            'currency_rules': conftest.get_currency_rules(),
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


def _finish_estimate_too_heavy():
    return {
        'cars': [],
        'failure_reason': 'estimating.too_heavy_item',
        'items_comments': [
            {'comment': 'estimating.too_heavy_item', 'id': 124},
        ],
    }


def _lcv_l_limits():
    # TODO change ge_default_cargo_type_limits for lcv_l
    limits = conftest.get_default_cargo_type_limits()
    limits['lcv_l'] = limits.pop('lcv_m')
    return limits


@pytest.mark.config(CARGO_TYPE_LIMITS=_lcv_l_limits())
@pytest.mark.parametrize(
    'items, finish_estimate_request',
    [
        # one item ok requirements
        (
            [conftest.get_cargo_item(weight=51)],
            conftest.get_finish_estimate_request(cargo_type='lcv_l'),
        ),
        # two is too_heavy
        (
            [
                conftest.get_cargo_item(item_id=123, weight=51),
                conftest.get_cargo_item(item_id=124, weight=51),
            ],
            _finish_estimate_too_heavy(),
        ),
        # one too_heavy item
        (
            [conftest.get_cargo_item(item_id=124, weight=101)],
            _finish_estimate_too_heavy(),
        ),
        # item quantity > 1 ok
        (
            [conftest.get_cargo_item(quantity=2, weight=24)],
            conftest.get_finish_estimate_request(
                cargo_type='lcv_l', quantity=2,
            ),
        ),
        # item quntity > 1 too_heavy
        (
            [conftest.get_cargo_item(item_id=124, quantity=2, weight=51)],
            _finish_estimate_too_heavy(),
        ),
    ],
)
async def test_too_heavy(
        stq_runner,
        mock_claims_full,
        mock_int_api_profile,
        mock_int_api_estimate,
        mock_finish_estimate,
        items: list,
        finish_estimate_request: dict,
):
    mock_claims_full.response['items'] = items
    mock_finish_estimate['expected-request'] = finish_estimate_request

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


def _finish_estimate_too_large_volume():
    return {
        'cars': [],
        'failure_reason': 'estimating.too_large_item',
        'items_comments': [
            {'comment': 'estimating.too_large_item', 'id': 124},
        ],
    }


def _finish_estimate_too_large_linear():
    return {
        'cars': [],
        'failure_reason': 'estimating.too_large_linear_size',
        'items_comments': [
            {'comment': 'estimating.too_large_linear_size', 'id': 124},
        ],
    }


@pytest.mark.config(CARGO_TYPE_LIMITS=_lcv_l_limits())
@pytest.mark.parametrize(
    'items, finish_estimate_request',
    [
        # one item ok requirements
        (
            [conftest.get_cargo_item(has_params=True)],
            conftest.get_finish_estimate_request(cargo_type='lcv_l'),
        ),
        # two is too_large_volume
        (
            [
                conftest.get_cargo_item(
                    item_id=123,
                    weight=1,
                    has_params=True,
                    length=0.1,
                    height=0.1,
                    width=0.1,
                ),
                conftest.get_cargo_item(
                    item_id=124,
                    weight=1,
                    has_params=True,
                    length=1.9,
                    height=1.9,
                    width=1.9,
                ),
            ],
            _finish_estimate_too_large_volume(),
        ),
        # one too_large_linear item
        (
            [
                conftest.get_cargo_item(
                    item_id=124, weight=1, has_params=True, length=3,
                ),
            ],
            _finish_estimate_too_large_linear(),
        ),
        # item quantity > 1 ok
        (
            [
                conftest.get_cargo_item(
                    item_id=123,
                    quantity=2,
                    weight=1,
                    has_params=True,
                    length=0.9,
                    height=0.9,
                    width=0.9,
                ),
            ],
            conftest.get_finish_estimate_request(
                cargo_type='lcv_l', quantity=2,
            ),
        ),
        # item quntity > 1 too_large_volume
        (
            [
                conftest.get_cargo_item(
                    item_id=124,
                    quantity=2,
                    weight=1,
                    has_params=True,
                    length=1.9,
                    height=1.9,
                    width=1.9,
                ),
            ],
            _finish_estimate_too_large_volume(),
        ),
    ],
)
async def test_too_large(
        stq_runner,
        mock_claims_full,
        mock_int_api_profile,
        mock_int_api_estimate,
        mock_finish_estimate,
        items: list,
        finish_estimate_request: dict,
):
    mock_claims_full.response['items'] = items
    mock_finish_estimate['expected-request'] = finish_estimate_request

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


@pytest.mark.config(
    CARGO_TYPE_LIMITS={
        'van': {
            'carrying_capacity_max_kg': 2001,
            'carrying_capacity_min_kg': 300,
            'height_max_cm': 201,
            'height_min_cm': 90,
            'length_max_cm': 290,
            'length_min_cm': 170,
            'width_max_cm': 201,
            'width_min_cm': 96,
        },
    },
)
@pytest.mark.parametrize(
    'client_requirements, save_cars_request',
    [
        (
            None,
            {
                'zone_id': 'moscow',
                'is_delayed': False,
                'cars': [
                    {
                        'taxi_class': 'express',
                        'items': [{'id': 123, 'quantity': 1}],
                    },
                ],
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price': '999.001',
                    'price_raw': 999,
                },
                'currency': 'RUB',
                'currency_rules': conftest.get_currency_rules(),
                'warnings': [
                    {
                        'code': 'requirement_unavailable',
                        'details_code': (
                            'estimating.warning.'
                            'requirement_unavailable.'
                            'door_to_door'
                        ),
                        'source': 'taxi_requirements',
                    },
                ],
            },
        ),
        (
            {
                'taxi_class': 'express',
                'door_to_door': True,
                'taxi_classes': ['test_class_1', 'test_class_2'],
            },
            {
                'zone_id': 'moscow',
                'is_delayed': False,
                'cars': [
                    {
                        'taxi_class': 'express',
                        'items': [{'id': 123, 'quantity': 1}],
                    },
                ],
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price': '999.001',
                    'price_raw': 999,
                },
                'currency': 'RUB',
                'currency_rules': conftest.get_currency_rules(),
                'warnings': [
                    {
                        'code': 'requirement_unavailable',
                        'details_code': (
                            'estimating.warning.'
                            'requirement_unavailable.'
                            'door_to_door'
                        ),
                        'source': 'taxi_requirements',
                    },
                ],
            },
        ),
        (
            {'taxi_class': 'cargo', 'cargo_type': 'van'},
            {
                'zone_id': 'moscow',
                'is_delayed': False,
                'cars': [
                    {
                        'taxi_class': 'cargo',
                        'items': [{'id': 123, 'quantity': 1}],
                    },
                ],
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price': '999.001',
                    'price_raw': 999,
                },
                'currency': 'RUB',
                'currency_rules': conftest.get_currency_rules(),
                'warnings': [
                    {
                        'code': 'requirement_unavailable',
                        'details_code': (
                            'estimating.warning.'
                            'requirement_unavailable.'
                            'cargo_type'
                        ),
                        'source': 'taxi_requirements',
                    },
                ],
            },
        ),
        (
            {'taxi_class': 'cargo', 'cargo_type': 'van', 'cargo_loaders': 2},
            {
                'zone_id': 'moscow',
                'is_delayed': False,
                'cars': [
                    {
                        'taxi_class': 'cargo',
                        'items': [{'id': 123, 'quantity': 1}],
                    },
                ],
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price': '999.001',
                    'price_raw': 999,
                },
                'currency': 'RUB',
                'currency_rules': conftest.get_currency_rules(),
                'warnings': [
                    {
                        'code': 'requirement_unavailable',
                        'details_code': (
                            'estimating.warning.'
                            'requirement_unavailable.'
                            'cargo_loaders'
                        ),
                        'source': 'taxi_requirements',
                    },
                    {
                        'code': 'requirement_unavailable',
                        'details_code': (
                            'estimating.warning.'
                            'requirement_unavailable.'
                            'cargo_type'
                        ),
                        'source': 'taxi_requirements',
                    },
                ],
            },
        ),
    ],
)
async def test_requirement_unavailable(
        mockserver,
        stq_runner,
        load_json,
        client_requirements,
        save_cars_request,
        mock_claims_full,
        mock_int_api_profile,
):
    mock_claims_full.response['client_requirements'] = client_requirements

    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _dummy_get_tariff(request):
        categories = load_json('categories.json')
        for category in categories:
            category['summable_requirements'] = []

        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': categories,
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):
        assert request.json == save_cars_request

        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json == {
            'sourceid': 'cargo',
            'selected_class': save_cars_request['cars'][0]['taxi_class'],
            'user': {
                'personal_phone_id': 'personal_phone_id_123',
                'user_id': 'taxi_user_id_1',
            },
            'payment': {
                'payment_method_id': 'corp-corp_client_id_12312312312312312',
                'type': 'corp',
            },
            'requirements': {},
            'route': [[37.1, 55.1], [37.2, 55.3]],
        }
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [
                {
                    'class': save_cars_request['cars'][0]['taxi_class'],
                    'price_raw': 999.001,
                },
            ],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


@pytest.mark.parametrize(
    'is_delayed',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                is_config=True,
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='cargo_control_delayed_orders',
                consumers=['cargo-matcher/delayed-orders'],
                clauses=[
                    {
                        'title': '1',
                        'predicate': {
                            'type': 'gt',
                            'init': {
                                'value': 300,
                                'arg_name': 'order_delay_seconds',
                                'arg_type': 'int',
                            },
                        },
                        'value': {'is_delayed': True},
                    },
                ],
                default_value={},
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.experiments3(
                is_config=True,
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='cargo_control_delayed_orders',
                consumers=['cargo-matcher/delayed-orders'],
                clauses=[],
                default_value={'is_delayed': False},
            ),
        ),
    ],
)
@pytest.mark.now('2020-04-09T17:41:23.825194+00:00')
async def test_is_delayed(
        is_delayed,
        mockserver,
        mock_claims_full,
        stq_runner,
        mock_int_api_profile,
):
    mock_claims_full.response['due'] = '2020-04-09T17:47:23.825194+00:00'

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):
        assert request.json.get('is_delayed') == is_delayed

        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [{'class': 'express', 'price_raw': 999.001}],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert mock_claims_full.mock.times_called == 1
    assert _dummy_save_result.times_called == 1
    assert _orders_estimate.times_called == 1


@pytest.mark.tariff_settings(filename='tariff_settings/no_categories.json')
async def test_filter_individual_tariffs(
        mockserver, stq_runner, mock_claims_full, mock_int_api_profile,
):
    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def save_result(request):
        assert request.json['cars'] == []
        return {
            'id': 'claim_id_1',
            'status': 'estimating_failed',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert save_result.times_called == 1


@pytest.mark.parametrize('use_all_enabled', (True, False))
async def test_force_use_all_classes(
        mockserver,
        stq_runner,
        use_all_enabled,
        mock_claims_full,
        taxi_config,
        mock_int_api_profile,
):
    taxi_config.set(CARGO_MATCHER_FORCE_USE_ALL_CLASSES=use_all_enabled)

    mock_claims_full.response['items'] = []

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        if use_all_enabled:
            assert request.json['all_classes'] == use_all_enabled
        else:
            assert 'all_classes' not in request.json
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [
                {'time_raw': 30, 'class': 'express', 'price_raw': 999.001},
            ],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')

    assert mock_claims_full.mock.times_called == 1
    assert dummy_save_result.times_called == 1


def _finish_estimate_international_orders_prohibition(tanker_key):
    return {'cars': [], 'failure_reason': tanker_key}


def _finish_estimate_ok():
    result = conftest.get_finish_estimate_request(cargo_type='lcv_l')
    result['cars'][-1]['taxi_class'] = 'express'
    result['cars'][-1]['taxi_requirements'] = {'door_to_door': True}
    result['zone_id'] = 'bishkek'
    return result


@pytest.mark.tariff_settings(
    filename='tariff_settings/moscow_and_bishkek.json',
)
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='cargo_matcher_international_orders_prohibition',
    consumers=['cargo-matcher/international-orders-prohibition'],
    clauses=[],
    is_config=True,
    default_value={
        'countries': [
            {
                'country': 'kg',
                'tanker_key_order_to_country': (
                    'estimating.international_orders_prohibition_to_kg'
                ),
                'tanker_key_order_from_country': (
                    'estimating.international_orders_prohibition_from_kg'
                ),
                'tariffs': ['express', 'cargo', 'cargocorp'],
            },
        ],
    },
)
@pytest.mark.config(CARGO_TYPE_LIMITS=_lcv_l_limits())
@pytest.mark.parametrize(
    'index, coordinates, finish_estimate_request',
    [
        (
            [0],
            [[74.61, 42.87], None],
            _finish_estimate_international_orders_prohibition(
                'estimating.international_orders_prohibition_from_kg',
            ),
        ),
        (
            [1],
            [None, [74.61, 42.87]],
            _finish_estimate_international_orders_prohibition(
                'estimating.international_orders_prohibition_to_kg',
            ),
        ),
        # kg inside
        ([0, 1], [[74.61, 42.87], [74.61, 42.865]], _finish_estimate_ok()),
    ],
)
async def test_international_orders_prohibition(
        stq_runner,
        mock_claims_full,
        mock_int_api_profile,
        mock_int_api_estimate,
        mock_finish_estimate,
        index: list,
        coordinates: list,
        finish_estimate_request: dict,
):
    mock_int_api_estimate['response']['service_levels'][-1][
        'class'
    ] = 'express'
    for i in index:
        mock_claims_full.response['route_points'][i]['address'][
            'coordinates'
        ] = coordinates[i]
    if finish_estimate_request:
        mock_finish_estimate['expected-request'] = finish_estimate_request

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


@pytest.fixture(name='check_taxi_class_correctness')
async def _check_taxi_class_correctness(
        mockserver,
        stq_runner,
        mock_v1_profile,
        mock_corp_tariffs,
        mock_paymentmethods,
        mock_int_api_estimate,
        mock_finish_estimate,
        mock_claims_full,
        load_json,
):
    def _get_expected_finish_estimate_request(result_taxi_class):
        expected_finish_request = conftest.get_finish_estimate_request(
            cargo_type='van',
        )
        if result_taxi_class == 'express':
            expected_finish_request['cars'][0]['taxi_requirements'] = {
                'door_to_door': True,
            }
        elif result_taxi_class != 'cargo':
            expected_finish_request['cars'][0].pop('taxi_requirements')
        expected_finish_request['cars'][0]['items'] = []
        expected_finish_request['cars'][0]['taxi_class'] = result_taxi_class
        return expected_finish_request

    def _set_available_taxi_classes():
        taxi_classes = load_json('categories_with_eda_lavka_courier.json')
        mock_corp_tariffs['response']['tariff']['categories'] = taxi_classes
        mock_paymentmethods['response']['methods'][0]['classes_available'] = [
            c['category_name'] for c in taxi_classes
        ]

    async def check(client_requirements, result_taxi_class):
        mock_claims_full.response['client_requirements'] = client_requirements
        mock_claims_full.response['items'] = []
        mock_int_api_estimate[
            'response'
        ] = conftest.get_default_estimate_response(result_taxi_class)
        _set_available_taxi_classes()
        mock_finish_estimate[
            'expected-request'
        ] = _get_expected_finish_estimate_request(result_taxi_class)
        await stq_runner.cargo_matcher_claim_estimating.call(
            task_id='claim_id_1',
        )

    return check


@pytest.mark.tariff_settings(
    filename='tariff_settings/moscow_and_bishkek.json',
)
async def test_empty_taxi_classes(check_taxi_class_correctness):
    await check_taxi_class_correctness(
        client_requirements={'taxi_class': 'lavka'}, result_taxi_class='lavka',
    )


@pytest.mark.tariff_settings(
    filename='tariff_settings/moscow_and_bishkek.json',
)
async def test_one_taxi_class(check_taxi_class_correctness):
    await check_taxi_class_correctness(
        client_requirements={'taxi_class': 'lavka', 'taxi_classes': ['eda']},
        result_taxi_class='eda',
    )


@pytest.mark.config(CARGO_TYPE_LIMITS=conftest.get_default_cargo_type_limits())
@pytest.mark.tariff_settings(
    filename='tariff_settings/moscow_and_bishkek.json',
)
@pytest.mark.parametrize(
    'taxi_classes, result_taxi_class',
    [
        (['lavka', 'cargo', 'courier'], 'cargo'),
        (['lavka', 'eda'], 'eda'),
        (['eda', 'courier', 'express'], 'express'),
    ],
)
async def test_simple_most_expensive_class(
        check_taxi_class_correctness,
        taxi_classes: dict,
        result_taxi_class: str,
):
    await check_taxi_class_correctness(
        client_requirements={
            'taxi_class': 'lavka',
            'taxi_classes': taxi_classes,
        },
        result_taxi_class=result_taxi_class,
    )


@pytest.mark.parametrize(
    'client_requirements',
    [
        None,
        {'taxi_class': 'cargo'},
        {
            'taxi_class': 'express',
            'taxi_classes': ['test_class_1', 'test_class_2'],
        },
    ],
)
async def test_client_requirements_taxi_classes(
        mockserver,
        stq_runner,
        load_json,
        client_requirements,
        mock_claims_full,
        testpoint,
        mock_int_api_profile,
):
    mock_claims_full.response['client_requirements'] = client_requirements

    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _dummy_get_tariff(request):
        categories = load_json('categories.json')
        for category in categories:
            category['summable_requirements'] = []

        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': categories,
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):

        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [{'class': 'cargo', 'price_raw': 999.001}],
        }

    @testpoint('cargo_extended_lookup__taxi_classes')
    def _point(taxi_classes):
        if client_requirements:
            expected_classes = []
            if 'taxi_classes' in client_requirements:
                expected_classes.extend(client_requirements['taxi_classes'])
            if 'taxi_class' in client_requirements:
                expected_classes.append(client_requirements['taxi_class'])
            assert sorted(taxi_classes) == sorted(expected_classes)

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


async def test_stq_new_pricing_estimated_distance_validation(
        stq_runner,
        mock_claims_full,
        exp3_pricing_enabled,
        mock_int_api_profile,
        mock_cargo_pricing,
        config_estimate_result_validation,
        mock_finish_estimate,
):
    mock_cargo_pricing.response['details']['total_distance'] = '2000'

    mock_finish_estimate['expected-request'] = {
        'cars': [],
        'failure_reason': 'estimating.route_too_long',
    }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert mock_finish_estimate['handler'].times_called == 1


async def test_stq_new_pricing_estimated_time_validation(
        stq_runner,
        mock_claims_full,
        exp3_pricing_enabled,
        mock_int_api_profile,
        mock_cargo_pricing,
        config_estimate_result_validation,
        mock_finish_estimate,
):
    mock_cargo_pricing.response['details']['total_time'] = '920'

    mock_finish_estimate['expected-request'] = {
        'cars': [],
        'failure_reason': 'estimating.route_too_long',
    }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert mock_finish_estimate['handler'].times_called == 1
