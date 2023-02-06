import json

import pytest

from . import conftest

DEFAULT_CARGO_TYPE_LIMITS = {
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
}


def get_corp_paymentmethods(user_tariffs=None):
    tariffs = user_tariffs or []
    return {
        'methods': [
            {
                'type': 'corp',
                'id': 'corp-corp_client_id_12312312312312312',
                'label': 'Yandex team',
                'description': 'Осталось 4000 из 5000 руб.',
                'cost_center': 'cost center',
                'cost_centers': {
                    'required': False,
                    'format': 'mixed',
                    'values': [],
                },
                'can_order': True,
                'zone_available': True,
                'hide_user_cost': False,
                'user_id': 'user_id_1',
                'client_comment': 'comment',
                'currency': 'RUB',
                'classes_available': tariffs,
            },
        ],
    }


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
    'claim_items, save_cars_request, ' 'estimate_request, estimate_response',
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
                        'taxi_class': 'cargo',
                        'taxi_requirements': {'cargo_type': 'van'},
                        'items': [{'id': 123, 'quantity': 1}],
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
            {},
            {},
        ),
    ],
)
async def test_cargo_tariff_available(
        mockserver,
        stq_runner,
        load_json,
        claim_items,
        save_cars_request,
        estimate_request,
        estimate_response,
        mock_claims_full,
        mock_int_api_profile,
):
    mock_claims_full.response['items'] = claim_items

    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _dummy_get_tariff(request):
        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': load_json('cargo_category.json'),
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
        assert request.json == estimate_request
        return estimate_response

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


@pytest.mark.parametrize(
    'cargo_matcher_cars, cargo_type_limits',
    [
        (
            [
                {
                    'enabled': True,
                    'max_loaders': 0,
                    'height_cm': 200,
                    'taxi_class': 'express',
                },
            ],
            {},
        ),
        (
            [
                {
                    'enabled': True,
                    'max_loaders': 0,
                    'cargo_type_limits_key': 'van',
                    'taxi_class': 'express',
                },
            ],
            {},
        ),
    ],
)
async def test_wrong_configs(
        mockserver,
        stq_runner,
        taxi_config,
        cargo_matcher_cars,
        cargo_type_limits,
        mock_claims_full,
        mock_int_api_profile,
):
    taxi_config.set_values(
        dict(
            CARGO_MATCHER_CARS=cargo_matcher_cars,
            CARGO_TYPE_LIMITS=cargo_type_limits,
        ),
    )

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        body = json.loads(request.get_data())
        assert body == {
            'cars': [],
            'failure_reason': 'estimating.too_large_item',
            'items_comments': [
                {'id': 123, 'comment': 'estimating.too_large_item'},
            ],
        }

        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')


@pytest.mark.config(CARGO_TYPE_LIMITS=DEFAULT_CARGO_TYPE_LIMITS)
@pytest.mark.parametrize(
    'user_tariffs, save_cars_request',
    [
        (
            [],
            {
                'cars': [],
                'failure_reason': (
                    'estimating.required_tariffs_disabled_for_user'
                ),
            },
        ),
        (
            ['express'],
            {
                'cars': [],
                'failure_reason': 'estimating.permitted_tariffs_not_enough',
                'items_comments': [
                    {'comment': 'estimating.too_large_item', 'id': 123},
                ],
            },
        ),
        (
            ['cargo', 'express'],
            {
                'cars': [
                    {
                        'taxi_class': 'cargo',
                        'taxi_requirements': {'cargo_type': 'van'},
                        'items': [{'id': 123, 'quantity': 1}],
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
    ],
)
async def test_user_tariffs(
        mockserver,
        stq_runner,
        user_tariffs,
        save_cars_request,
        mock_claims_full,
        mock_int_api_profile,
):
    mock_claims_full.response['items'] = [
        {
            'id': 123,
            'extra_id': '123',
            'pickup_point': 1,
            'droppof_point': 2,
            'title': 'Холодильник карманный',
            'size': {'length': 1, 'width': 0.8, 'height': 0.8},
            'weight': 5,
            'quantity': 1,
            'cost_value': '10.20',
            'cost_currency': 'RUR',
        },
    ]

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

    @mockserver.json_handler('/taxi-corp-integration/v1/corp_paymentmethods')
    def dummy_paymentmethods(request):
        return {
            'methods': [
                {
                    'type': 'corp',
                    'id': 'corp-corp_client_id_12312312312312312',
                    'label': 'Yandex team',
                    'description': 'Осталось 4000 из 5000 руб.',
                    'cost_center': 'cost center',
                    'cost_centers': {
                        'required': False,
                        'format': 'mixed',
                        'values': [],
                    },
                    'can_order': True,
                    'zone_available': True,
                    'hide_user_cost': False,
                    'user_id': 'user_id_1',
                    'client_comment': 'comment',
                    'currency': 'RUB',
                    'classes_available': user_tariffs,
                },
            ],
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json == {
            'sourceid': 'cargo',
            'selected_class': 'cargo',
            'user': {
                'personal_phone_id': 'personal_phone_id_123',
                'user_id': 'taxi_user_id_1',
            },
            'payment': {
                'payment_method_id': 'corp-corp_client_id_12312312312312312',
                'type': 'corp',
            },
            'requirements': {'cargo_type': 'van'},
            'route': [[37.1, 55.1], [37.2, 55.3]],
        }
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [{'class': 'cargo', 'price_raw': 999.001}],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')

    assert mock_claims_full.mock.times_called == 1
    assert dummy_save_result.times_called == 1
    assert dummy_paymentmethods.times_called == 1


@pytest.mark.config(CARGO_TYPE_LIMITS=DEFAULT_CARGO_TYPE_LIMITS)
@pytest.mark.parametrize(
    'item_dimension, taxi_class, requirements',
    [
        (0.1, 'express', {'door_to_door': True}),
        (0.5, 'cargo', {'cargo_type': 'van'}),
    ],
)
async def test_payment_on_delivery(
        mockserver,
        stq_runner,
        item_dimension,
        taxi_class,
        requirements,
        mock_claims_full,
        mock_int_api_profile,
):
    mock_claims_full.response['items'] = [
        {
            'id': 123,
            'extra_id': '123',
            'pickup_point': 1,
            'droppof_point': 2,
            'title': 'Холодильник карманный',
            'size': {
                'length': item_dimension,
                'width': item_dimension,
                'height': item_dimension,
            },
            'weight': 5,
            'quantity': 1,
            'cost_value': '10.20',
            'cost_currency': 'RUR',
        },
    ]
    mock_claims_full.response['route_points'][1]['payment_on_delivery'] = {
        'client_order_id': '123',
        'is_paid': False,
        'cost': '100',
    }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        body = json.loads(request.get_data())
        assert body == {
            'cars': [
                {
                    'items': [{'id': 123, 'quantity': 1}],
                    'taxi_class': taxi_class,
                    'taxi_requirements': requirements,
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
        }
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/taxi-corp-integration/v1/corp_paymentmethods')
    def dummy_paymentmethods(request):
        return get_corp_paymentmethods([taxi_class])

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json == {
            'sourceid': 'cargo',
            'selected_class': taxi_class,
            'user': {
                'personal_phone_id': 'personal_phone_id_123',
                'user_id': 'taxi_user_id_1',
            },
            'payment': {
                'payment_method_id': 'corp-corp_client_id_12312312312312312',
                'type': 'corp',
            },
            'requirements': requirements,
            'route': [[37.1, 55.1], [37.2, 55.3]],
        }
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [{'class': taxi_class, 'price_raw': 999.001}],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')

    assert mock_claims_full.mock.times_called == 1
    assert dummy_save_result.times_called == 1
    assert dummy_paymentmethods.times_called == 1


@pytest.mark.config(CARGO_TYPE_LIMITS=DEFAULT_CARGO_TYPE_LIMITS)
@pytest.mark.usefixtures(
    'mock_corp_tariffs',
    'mock_claims_full',
    'mock_int_api_profile',
    'mock_finish_estimate',
    'mock_int_api_estimate',
)
@pytest.mark.parametrize(
    'save_cars_request, estimate_response',
    [
        (
            {'cars': [], 'failure_reason': 'estimating.cant_construct_route'},
            {
                'alert': {'code': 'CANT_CONSTRUCT_ROUTE'},
                'offer': 'taxi_offer_id_1',
                'is_fixed_price': False,
                'currency_rules': conftest.get_currency_rules(),
                'service_levels': [
                    {
                        'class': 'cargo',
                        'price': '855 руб. за первые 5 мин и 0 км',
                    },
                ],
            },
        ),
    ],
)
async def test_no_route(
        stq_runner,
        save_cars_request,
        estimate_response,
        mock_finish_estimate,
        mock_int_api_estimate,
):
    mock_finish_estimate['expected-request'] = save_cars_request
    mock_int_api_estimate['response'] = estimate_response

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert mock_finish_estimate['handler'].times_called == 1


@pytest.mark.parametrize(
    'payment_on_delivery, skip_door_to_door, excepted_requirements',
    [
        (False, False, {'door_to_door': True}),
        (False, True, {'door_to_door': False}),
        (True, False, {'door_to_door': True}),
        (True, True, {'door_to_door': True}),
    ],
)
async def test_door_to_door(
        mockserver,
        stq_runner,
        taxi_config,
        payment_on_delivery,
        skip_door_to_door,
        excepted_requirements,
        mock_claims_full,
        mock_int_api_profile,
):
    mock_claims_full.response['client_requirements'] = {
        'taxi_class': 'express',
    }
    mock_claims_full.response['skip_door_to_door'] = skip_door_to_door
    if payment_on_delivery:
        mock_claims_full.response['route_points'][1]['payment_on_delivery'] = {
            'client_order_id': '123',
            'is_paid': False,
            'cost': '100',
        }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        body = json.loads(request.get_data())
        if excepted_requirements is not None:
            assert (
                body['cars'][0]['taxi_requirements'] == excepted_requirements
            )
        else:
            assert 'taxi_requirements' not in body['cars'][0]
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/taxi-corp-integration/v1/corp_paymentmethods')
    def dummy_paymentmethods(request):
        return get_corp_paymentmethods(['cargo', 'express'])

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [{'class': 'express', 'price_raw': 700}],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')

    assert mock_claims_full.mock.times_called == 1
    assert dummy_save_result.times_called == 1
    assert dummy_paymentmethods.times_called == 1


@pytest.mark.usefixtures(
    'mock_int_api_estimate',
    'mock_int_api_profile',
    'mock_claims_full',
    'mock_finish_estimate',
    'mock_paymentmethods',
)
@pytest.mark.parametrize(
    'save_result_request',
    [{'cars': [], 'failure_reason': 'estimating.payment_method_cant_order'}],
)
async def test_cant_order(
        stq_runner,
        save_result_request,
        mock_finish_estimate,
        mock_paymentmethods,
):
    mock_paymentmethods['response']['methods'][0]['can_order'] = False
    mock_finish_estimate['expected-request'] = save_result_request

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert mock_finish_estimate['handler'].times_called == 1


@pytest.mark.config(CARGO_TYPE_LIMITS=DEFAULT_CARGO_TYPE_LIMITS)
@pytest.mark.usefixtures(
    'mock_claims_full', 'mock_int_api_profile', 'mock_finish_estimate',
)
@pytest.mark.parametrize(
    'finish_estimate_request, profile_response, profile_status',
    [
        (
            {'cars': [], 'failure_reason': 'estimating.sender_blocked'},
            {'blocked': '2024-04-03T06:52:15+0000', 'type': ''},
            403,
        ),
    ],
)
async def test_sender_blocked(
        mockserver,
        stq_runner,
        finish_estimate_request,
        profile_response,
        profile_status,
        mock_finish_estimate,
        mock_int_api_profile,
):
    mock_int_api_profile.response = mockserver.make_response(
        json=profile_response, status=profile_status,
    )
    mock_finish_estimate['expected-request'] = finish_estimate_request

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert mock_int_api_profile.mock.times_called == 1
    assert mock_finish_estimate['handler'].times_called == 1


@pytest.mark.config(
    CARGO_MATCHER_CARS=[
        {
            'taxi_class': 'courier',
            'length_cm': 30,
            'width_cm': 30,
            'height_cm': 30,
            'carrying_capacity_kg': 10,
            'max_loaders': 0,
            'enabled': True,
        },
        {
            'taxi_class': 'express',
            'length_cm': 100,
            'width_cm': 50,
            'height_cm': 40,
            'carrying_capacity_kg': 20,
            'max_loaders': 0,
            'enabled': True,
        },
    ],
)
@pytest.mark.parametrize(
    ('door_to_door_enabled', 'expected_taxi_class'),
    (
        pytest.param(
            True,
            'courier',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='cargo_replace_express_to_courier',
                    consumers=['cargo-matcher/estimate'],
                    clauses=[],
                    default_value={'enabled': True},
                ),
            ],
        ),
        pytest.param(
            False,
            'express',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='cargo_replace_express_to_courier',
                    consumers=['cargo-matcher/estimate'],
                    clauses=[],
                    default_value={'enabled': False},
                ),
            ],
        ),
        pytest.param(
            False,
            'express',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': False},
                    name='cargo_replace_express_to_courier',
                    consumers=['cargo-matcher/estimate'],
                    clauses=[],
                    default_value={'enabled': True},
                ),
            ],
        ),
    ),
)
async def test_courier_experiment(
        mockserver,
        stq_runner,
        load_json,
        door_to_door_enabled: bool,
        expected_taxi_class: str,
        mock_claims_full,
        mock_int_api_profile,
):
    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _tariffs(request):
        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': load_json('categories_with_courier.json'),
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        }

    mock_claims_full.response['client_requirements'] = {
        'taxi_class': 'express',
    }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/taxi-corp-integration/v1/corp_paymentmethods')
    def dummy_paymentmethods(request):
        return get_corp_paymentmethods(['cargo', 'express', 'courier'])

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json['requirements'] == {'door_to_door': True}

        assert request.json['selected_class'] == expected_taxi_class
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [
                {'class': expected_taxi_class, 'price_raw': 700},
            ],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')

    assert mock_claims_full.mock.times_called == 1
    assert dummy_save_result.times_called == 1
    assert dummy_paymentmethods.times_called == 1


@pytest.mark.parametrize(
    ('door_to_door_enabled', 'expected_taxi_class'),
    (
        pytest.param(
            True,
            'express',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='cargo_replace_express_to_courier',
                    consumers=['cargo-matcher/estimate'],
                    clauses=[],
                    default_value={'enabled': True},
                ),
            ],
        ),
        pytest.param(
            True,
            'express',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': False},
                    name='cargo_replace_express_to_courier',
                    consumers=['cargo-matcher/estimate'],
                    clauses=[],
                    default_value={'enabled': True},
                ),
            ],
        ),
    ),
)
async def test_courier_experiment_without_tariff(
        mockserver,
        stq_runner,
        door_to_door_enabled: bool,
        expected_taxi_class: str,
        mock_int_api_profile,
        mock_claims_full,
):
    mock_claims_full.response['client_requirements'] = {
        'taxi_class': 'express',
    }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/taxi-corp-integration/v1/corp_paymentmethods')
    def dummy_paymentmethods(request):
        return get_corp_paymentmethods(['cargo', 'express', 'courier'])

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        assert request.json['requirements'] == {'door_to_door': True}

        assert request.json['selected_class'] == expected_taxi_class
        return {
            'offer': 'taxi_offer_id_1',
            'is_fixed_price': True,
            'currency_rules': conftest.get_currency_rules(),
            'service_levels': [
                {'class': expected_taxi_class, 'price_raw': 700},
            ],
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')

    assert mock_claims_full.mock.times_called == 1
    assert dummy_save_result.times_called == 1
    assert dummy_paymentmethods.times_called == 1
