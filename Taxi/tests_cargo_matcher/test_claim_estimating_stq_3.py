import copy
import json

import pytest

from . import conftest


ESTIMATE_REQUEST = {
    'sourceid': 'cargo',
    'selected_class': '<replace_me>',
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

ESTIMATE_RESPONSE = {
    'offer': 'taxi_offer_id_1',
    'is_fixed_price': True,
    'currency_rules': conftest.get_currency_rules(),
    'service_levels': [
        {'class': 'econom', 'price_raw': 987.654},
        {'class': '<replace_me>', 'price_raw': 999.001},
    ],
}

FINISH_ESTIMATE_REQUEST = {
    'zone_id': 'moscow',
    'is_delayed': False,
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
    'currency': 'RUB',
    'currency_rules': conftest.get_currency_rules(),
}

FINISH_ESTIMATE_REQUEST_WITH_EXPERIMENT_AND_SUBSTITUTION = {
    'zone_id': 'moscow',
    'is_delayed': False,
    'cars': [
        {
            'taxi_class': 'cargocorp',
            'client_taxi_class': 'cargo',
            'taxi_requirements': {'cargo_type': 'van'},
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
    'taxi_classes_substitution': ['express', 'cargocorp'],
}

FINISH_ESTIMATE_REQUEST_WITH_EXPERIMENT = {
    'zone_id': 'moscow',
    'is_delayed': False,
    'cars': [
        {
            'taxi_class': 'cargocorp',
            'client_taxi_class': 'cargo',
            'taxi_requirements': {'cargo_type': 'van'},
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
}


@pytest.fixture(name='matcher_exp_extended_tariffs')
def _matcher_exp_extended_tariffs(taxi_cargo_matcher, exp_extended_tariffs):
    async def _wrapper(**kwargs):
        await exp_extended_tariffs(
            taxi_cargo_matcher,
            consumers=['cargo-matcher/tariff-substitution'],
            **kwargs,
        )

    return _wrapper


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
@pytest.mark.config(CARGO_MATCHER_PERCENTAGE_OF_BAGGAGE_VOLUME=0.1)
@pytest.mark.parametrize(
    [
        'corp_categories',
        'expected_taxi_class',
        'finish_estimate_request',
        'expected_all_classes',
        'cargocorp_autoreplacement_enabled',
    ],
    [
        pytest.param(
            'categories.json',
            'cargocorp',
            FINISH_ESTIMATE_REQUEST_WITH_EXPERIMENT_AND_SUBSTITUTION,
            True,
            None,
            id='cargocorp_from_experiment',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='cargo_replace_cargo_to_cargocorp',
                    consumers=['cargo-matcher/estimate'],
                    clauses=[],
                    default_value={'enabled': True},
                ),
            ],
        ),
        pytest.param(
            'categories_with_cargocorp.json',
            'cargocorp',
            FINISH_ESTIMATE_REQUEST_WITH_EXPERIMENT,
            False,
            True,
            id='cargocorp_category_enabled',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='cargo_replace_cargo_to_cargocorp',
                    consumers=['cargo-matcher/estimate'],
                    clauses=[],
                    default_value={'enabled': False},
                ),
            ],
        ),
        pytest.param(
            'categories_with_cargocorp.json',
            'cargo',
            FINISH_ESTIMATE_REQUEST,
            False,
            False,
            id='cargocorp_category_auto_replacement_disabled',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='cargo_replace_cargo_to_cargocorp',
                    consumers=['cargo-matcher/estimate'],
                    clauses=[],
                    default_value={'enabled': False},
                ),
            ],
        ),
        pytest.param(
            'categories.json',
            'cargo',
            FINISH_ESTIMATE_REQUEST,
            False,
            None,
            id='cargo_value_disabled',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': True},
                    name='cargo_replace_cargo_to_cargocorp',
                    consumers=['cargo-matcher/estimate'],
                    clauses=[],
                    default_value={'enabled': False},
                ),
            ],
        ),
        pytest.param(
            'categories.json',
            'cargo',
            FINISH_ESTIMATE_REQUEST,
            False,
            None,
            id='cargo_experiment_disabled',
            marks=[
                pytest.mark.experiments3(
                    match={'predicate': {'type': 'true'}, 'enabled': False},
                    name='cargo_replace_cargo_to_cargocorp',
                    consumers=['cargo-matcher/estimate'],
                    clauses=[],
                    default_value={'enabled': True},
                ),
            ],
        ),
    ],
)
async def test_replace_cargo_by_cargocorp(
        mockserver,
        stq_runner,
        mock_claims_full,
        load_json,
        matcher_exp_extended_tariffs,
        corp_categories,
        expected_taxi_class,
        finish_estimate_request,
        expected_all_classes,
        cargocorp_autoreplacement_enabled,
        mock_int_api_profile,
        conf_exp3_cargocorp_autoreplacement,
):
    if cargocorp_autoreplacement_enabled is not None:
        await conf_exp3_cargocorp_autoreplacement(
            is_enabled=cargocorp_autoreplacement_enabled,
        )
    if expected_all_classes:
        await matcher_exp_extended_tariffs(
            extra_classes=['courier', 'express'],
        )

    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _corp_tariffs(request):
        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': load_json(corp_categories),
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
        assert body == finish_estimate_request
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        expected_request = copy.deepcopy(ESTIMATE_REQUEST)
        expected_request['selected_class'] = expected_taxi_class
        if expected_all_classes:
            expected_request['all_classes'] = True
        assert request.json == expected_request
        corrected_response = copy.deepcopy(ESTIMATE_RESPONSE)
        corrected_response['service_levels'][1]['class'] = expected_taxi_class
        return corrected_response

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert _dummy_save_result.has_calls


@pytest.mark.config(
    CARGO_SDD_TAXI_TARIFF_SETTINGS={
        'name': 'night',
        'remove_in_tariffs': True,
        'remove_in_admin_tariffs': True,
    },
)
async def test_check_sdd_tariff_enabled(
        mockserver,
        stq_runner,
        mock_claims_full,
        load_json,
        matcher_exp_extended_tariffs,
        mock_int_api_profile,
):
    @mockserver.json_handler('/corp-tariffs/v1/client_tariff/current')
    def _corp_tariffs(request):
        return {
            'tariff': {
                'id': '5caeed9d1bc8d21af5a07a26-multizonal-tariff_plan_1',
                'home_zone': 'moscow',
                'categories': load_json('categories.json'),
            },
            'disable_paid_supply_price': False,
            'disable_fixed_price': True,
            'client_tariff_plan': {
                'tariff_plan_series_id': 'tariff_plan_id_123',
                'date_from': '2020-01-22T15:30:00+00:00',
                'date_to': '2021-01-22T15:30:00+00:00',
            },
        }

    mock_claims_full.response['same_day_data'] = {
        'delivery_interval': {
            'from': '2020-01-22T15:30:00+00:00',
            'to': '2020-01-22T15:45:00+00:00',
        },
    }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):
        body = json.loads(request.get_data())
        assert body == {
            'cars': [
                {
                    'items': [{'id': 123, 'quantity': 1}],
                    'taxi_class': 'night',
                    'taxi_requirements': {'door_to_door': True},
                },
            ],
            'currency': 'RUB',
            'currency_rules': {
                'code': 'RUB',
                'sign': '₽',
                'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
                'text': 'руб.',
            },
            'is_delayed': False,
            'offer': {
                'offer_id': 'taxi_offer_id_1',
                'price': '999.001',
                'price_raw': 999,
            },
            'zone_id': 'moscow',
        }
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        expected_request = copy.deepcopy(ESTIMATE_REQUEST)
        expected_request['requirements'] = {'door_to_door': True}
        expected_request['selected_class'] = 'night'
        assert request.json == expected_request
        corrected_response = copy.deepcopy(ESTIMATE_RESPONSE)
        corrected_response['service_levels'][1]['class'] = 'night'
        return corrected_response

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert _dummy_save_result.has_calls


@pytest.mark.config(
    CARGO_SDD_TAXI_TARIFF_SETTINGS={
        'name': 'unknown',
        'remove_in_tariffs': True,
        'remove_in_admin_tariffs': True,
    },
)
async def test_check_sdd_tariff_disabled(
        mockserver,
        stq_runner,
        mock_claims_full,
        load_json,
        matcher_exp_extended_tariffs,
        mock_int_api_profile,
):
    mock_claims_full.response['same_day_data'] = {
        'delivery_interval': {
            'from': '2020-01-22T15:30:00+00:00',
            'to': '2020-01-22T15:45:00+00:00',
        },
    }

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def _dummy_save_result(request):
        body = json.loads(request.get_data())
        assert body == {
            'cars': [],
            'failure_reason': 'estimating.tariff.no_sdd_tariff',
        }
        return {
            'id': 'claim_id_1',
            'status': 'estimating_failed',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert _dummy_save_result.has_calls


async def test_stq_add_pricing_processing_events(
        mockserver,
        stq_runner,
        mock_claims_full,
        mock_finish_estimate,
        mock_int_api_estimate,
        mock_int_api_profile,
        mock_pricing_processing,
):
    mock_int_api_estimate['response'] = conftest.get_default_estimate_response(
        taxi_class='express',
    )
    claim_id = 'claim_id_1'
    await stq_runner.cargo_matcher_claim_estimating.call(task_id=claim_id)
    assert mock_pricing_processing.request.json == {
        'entity_id': claim_id,
        'events': [
            {'kind': 'create'},
            {
                'kind': 'calculation',
                'calc_id': 'taxi_offer_id_1',
                'origin_uri': 'cargo_matcher_claim_estimating',
                'price_for': 'client',
                'clients': [
                    {'corp_client_id': 'corp_client_id_12312312312312312'},
                ],
                'calc_kind': 'offer',
            },
        ],
    }


async def test_stq_fixed_price_notation(
        mockserver,
        stq_runner,
        mock_claims_full,
        default_pricing_response,
        exp3_pricing_enabled,
        mock_int_api_profile,
):
    @mockserver.json_handler('/cargo-pricing/v1/taxi/calc')
    def _cargo_pricing(request):
        default_pricing_response['price'] = '3527398.7777'
        return default_pricing_response

    @mockserver.json_handler('/cargo-claims/v1/claims/finish-estimate')
    def dummy_save_result(request):
        # if it is not fixed, it will give 3.5274e+06
        assert request.json['offer']['price'] == '3527398.7777'
        return {
            'id': 'claim_id_1',
            'status': 'ready_for_approval',
            'version': 1,
            'user_request_revision': '123',
            'skip_client_notify': True,
        }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert dummy_save_result.times_called == 1
