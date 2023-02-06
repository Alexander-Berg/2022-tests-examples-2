from typing import Optional

import pytest

from . import conftest


@pytest.mark.config(CARGO_TYPE_LIMITS=conftest.get_default_cargo_type_limits())
@pytest.mark.parametrize(
    'client_requirements, finish_estimate_request, has_params',
    [
        # no client requirements
        (None, conftest.get_finish_estimate_request(), True),
        # same, just check no affect
        (
            {'cargo_type': 'lcv_m', 'cargo_loaders': 0, 'taxi_class': 'cargo'},
            conftest.get_finish_estimate_request(),
            True,
        ),
        # check loaders
        (
            {'cargo_type': 'lcv_m', 'cargo_loaders': 1, 'taxi_class': 'cargo'},
            {
                'zone_id': 'moscow',
                'is_delayed': False,
                'cars': [
                    {
                        'taxi_class': 'cargo',
                        'taxi_requirements': {
                            'cargo_type': 'lcv_m',
                            'cargo_loaders': 1,
                        },
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
            },
            True,
        ),
        # client requirements different cargo_type warning
        (
            {'taxi_class': 'cargo', 'cargo_type': 'van'},
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
                'warnings': [
                    {
                        'source': 'client_requirements',
                        'code': 'not_fit_in_car',
                        'details_code': 'estimating.warning.too_large_item',
                        'details_args': {'item_title': 'Холодильник'},
                    },
                ],
            },
            True,
        ),
        (
            {'taxi_class': 'express'},
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
                'warnings': [
                    {
                        'source': 'client_requirements',
                        'code': 'not_fit_in_car',
                        'details_code': 'estimating.warning.too_large_item',
                        'details_args': {'item_title': 'Холодильник'},
                    },
                ],
            },
            True,
        ),
        (
            None,
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
            False,
        ),
        (
            {'taxi_class': 'express'},
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
            False,
        ),
    ],
)
async def test_client_requirements(
        stq_runner,
        mock_claims_full,
        mock_int_api_profile,
        mock_int_api_estimate,
        mock_finish_estimate,
        client_requirements: Optional[dict],
        finish_estimate_request: dict,
        has_params,
):
    mock_claims_full.response['items'] = [
        conftest.get_cargo_item(has_params=has_params),
    ]
    if client_requirements:
        mock_claims_full.response['client_requirements'] = client_requirements
    mock_finish_estimate['expected-request'] = finish_estimate_request
    if client_requirements and client_requirements.get('taxi_class'):
        mock_int_api_estimate['response'] = (
            conftest.get_default_estimate_response(
                client_requirements['taxi_class'],
            )
        )
    if not client_requirements and not has_params:
        mock_int_api_estimate[
            'response'
        ] = conftest.get_default_estimate_response('express')

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert mock_finish_estimate['handler'].times_called == 1


@pytest.mark.config(CARGO_TYPE_LIMITS=conftest.get_default_cargo_type_limits())
@pytest.mark.parametrize(
    'expected_offer_id, cargo_type_workmode',
    [
        pytest.param(
            'taxi_offer_id_2',
            'oldway',
            marks=pytest.mark.experiments3(
                is_config=True,
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='cargo_type_requirement_work_mode',
                consumers=['cargo-matcher/estimate'],
                clauses=[],
                default_value={'work_mode': 'oldway'},
            ),
        ),
        pytest.param(
            'taxi_offer_id_3',
            'tryout',
            marks=pytest.mark.experiments3(
                is_config=True,
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='cargo_type_requirement_work_mode',
                consumers=['cargo-matcher/estimate'],
                clauses=[],
                default_value={'work_mode': 'tryout'},
            ),
        ),
        pytest.param(
            'taxi_offer_id_3',
            'newway',
            marks=pytest.mark.experiments3(
                is_config=True,
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='cargo_type_requirement_work_mode',
                consumers=['cargo-matcher/estimate'],
                clauses=[],
                default_value={'work_mode': 'newway'},
            ),
        ),
        pytest.param(
            'taxi_offer_id_3',
            'newway',
            marks=pytest.mark.experiments3(
                is_config=True,
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='cargo_type_requirement_work_mode',
                consumers=['cargo-matcher/estimate'],
                clauses=[
                    {
                        'title': '1',
                        'value': {'work_mode': 'newway'},
                        'predicate': {
                            'init': {
                                'predicates': [
                                    {
                                        'init': {
                                            'set': ['moscow'],
                                            'arg_name': 'zone',
                                            'set_elem_type': 'string',
                                        },
                                        'type': 'in_set',
                                    },
                                    {
                                        'init': {
                                            'value': 'cargo',
                                            'arg_name': 'tariff',
                                            'arg_type': 'string',
                                        },
                                        'type': 'eq',
                                    },
                                ],
                            },
                            'type': 'all_of',
                        },
                    },
                ],
                default_value={},
            ),
        ),
    ],
)
async def test_cargo_type_workmode(
        mockserver,
        stq_runner,
        mock_claims_full,
        mock_int_api_profile,
        mock_finish_estimate,
        taxi_config,
        cargo_type_workmode,
        expected_offer_id,
):
    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def mock_estimate(request):
        resp = conftest.get_default_estimate_response()
        if 'cargo_type' in request.json['requirements']:
            resp['offer'] = 'taxi_offer_id_2'
        elif 'cargo_type_int' in request.json['requirements']:
            resp['offer'] = 'taxi_offer_id_3'
        return resp

    mock_claims_full.response['client_requirements'] = {
        'cargo_type': 'lcv_m',
        'taxi_class': 'cargo',
    }
    result_requirements = dict()
    if cargo_type_workmode == 'oldway':
        result_requirements = {'cargo_type': 'lcv_m'}
    else:
        result_requirements = {'cargo_type_int': 2}
    mock_finish_estimate['expected-request'] = {
        'cars': [
            {
                'taxi_class': 'cargo',
                'taxi_requirements': result_requirements,
                'items': [{'id': 123, 'quantity': 1}],
            },
        ],
        'currency': 'RUB',
        'currency_rules': {
            'code': 'RUB',
            'text': 'руб.',
            'template': '$VALUE$\u2006$SIGN$$CURRENCY$',
            'sign': '₽',
        },
        'offer': {
            'offer_id': expected_offer_id,
            'price': '999.001',
            'price_raw': 999,
        },
        'zone_id': 'moscow',
        'is_delayed': False,
    }
    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')

    if cargo_type_workmode == 'tryout':
        assert mock_estimate.times_called == 2
    else:
        assert mock_estimate.times_called == 1


def _set_expected_finish_estimate_request(
        mock_finish_estimate, taxi_class, taxi_requirements, warnings=None,
):
    mock_finish_estimate['expected-request'] = {
        'cars': [
            {
                'items': [{'id': 123, 'quantity': 1}],
                'taxi_class': taxi_class,
                'taxi_requirements': taxi_requirements,
            },
        ],
        'currency': 'RUB',
        'currency_rules': {
            'code': 'RUB',
            'sign': 'RUB',
            'template': 'RUB',
            'text': 'RUB',
        },
        'eta': 0.2,
        'is_delayed': False,
        'offer': {
            'offer_id': 'cargo-pricing/v1/123456',
            'price': '123.45',
            'price_raw': 123,
        },
        'zone_id': 'moscow',
        'total_distance_meters': 1000.0,
    }

    if warnings is not None:
        mock_finish_estimate['expected-request']['warnings'] = warnings


@pytest.mark.config(CARGO_TYPE_LIMITS=conftest.get_default_cargo_type_limits())
async def test_cargo_type_with_cargo_pricing(
        stq_runner,
        mock_claims_full,
        mock_int_api_profile,
        mock_finish_estimate,
        exp3_pricing_enabled,
        exp3_work_mode_new_way,
        mock_cargo_pricing,
):
    _set_expected_finish_estimate_request(
        mock_finish_estimate,
        taxi_class='cargo',
        taxi_requirements={'cargo_type_int': 2},
    )
    mock_claims_full.response['client_requirements'] = {
        'cargo_type': 'lcv_m',
        'taxi_class': 'cargo',
    }

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')

    assert mock_cargo_pricing.mock.times_called == 1
    assert mock_cargo_pricing.request['taxi_requirements'] == {
        'cargo_type_int': 2,
    }
    assert mock_cargo_pricing.request['waypoints'] == [
        {'id': '1', 'position': [37.1, 55.1], 'type': 'pickup'},
        {'id': '2', 'position': [37.2, 55.3], 'type': 'dropoff'},
    ]
    assert mock_cargo_pricing.request['cargo_items'] == [
        {
            'dropoff_point_id': '2',
            'pickup_point_id': '1',
            'quantity': 1,
            'size': {'height': 0.3, 'length': 0.8, 'width': 0.4},
            'weight': 5.0,
        },
    ]


@pytest.fixture(name='check_estimate_stq_client_requirements')
def _check_estimate_stq_client_requirements(
        stq_runner,
        mock_claims_full,
        mock_finish_estimate,
        mock_int_api_estimate,
        mock_int_api_profile,
        mock_cargo_pricing,
        exp3_pricing_enabled,
        exp3_work_mode_new_way,
):
    async def estimate(
            claim_client_requirements,
            finish_estimate_taxi_requirements,
            cargo_pricing_taxi_requirements,
            finish_estimate_warnings=None,
    ):
        mock_claims_full.response[
            'client_requirements'
        ] = claim_client_requirements
        mock_claims_full.response['client_requirements'][
            'taxi_class'
        ] = 'express'
        _set_expected_finish_estimate_request(
            mock_finish_estimate,
            taxi_class='express',
            taxi_requirements=finish_estimate_taxi_requirements,
            warnings=finish_estimate_warnings,
        )
        mock_int_api_estimate[
            'response'
        ] = conftest.get_default_estimate_response('express')
        await stq_runner.cargo_matcher_claim_estimating.call(
            task_id='claim_id_1',
        )
        assert mock_finish_estimate['handler'].times_called == 1
        assert mock_cargo_pricing.mock.times_called == 1
        assert (
            mock_cargo_pricing.request['taxi_requirements']
            == cargo_pricing_taxi_requirements
        )

    return estimate


async def test_client_requirement_pro_courier(
        check_estimate_stq_client_requirements,
):
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'pro_courier': True},
        finish_estimate_taxi_requirements={
            'door_to_door': True,
            'pro_courier': True,
        },
        cargo_pricing_taxi_requirements={
            'pro_courier': 1,
            'door_to_door': True,
        },
    )


async def test_client_requirement_dynamic_requirements(
        check_estimate_stq_client_requirements, config_dynamic_requirements,
):
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'dynamic_requirement': 12},
        finish_estimate_taxi_requirements={
            'door_to_door': True,
            'dynamic_requirement': 12,
        },
        cargo_pricing_taxi_requirements={
            'dynamic_requirement': 12,
            'door_to_door': True,
        },
    )


async def test_client_requirement_dynamic_requirements_disabled(
        check_estimate_stq_client_requirements,
        set_dynamic_requirements_config,
):
    await set_dynamic_requirements_config(dynamic_requirements=[])
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'dynamic_requirement': 12},
        finish_estimate_taxi_requirements={'door_to_door': True},
        cargo_pricing_taxi_requirements={'door_to_door': True},
    )


async def test_client_requirement_unavailable_dynamic_requirements(
        check_estimate_stq_client_requirements,
        set_dynamic_requirements_config,
):
    await set_dynamic_requirements_config(
        dynamic_requirements=['unavailable_requirements'],
    )
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'unavailable_requirements': 12},
        finish_estimate_taxi_requirements={'door_to_door': True},
        finish_estimate_warnings=[
            {
                'code': 'requirement_unavailable',
                'details_code': 'estimating.warning.requirement_unavailable',
                'source': 'taxi_requirements',
                'details_args': {'item_title': 'unavailable_requirements'},
            },
        ],
        cargo_pricing_taxi_requirements={'door_to_door': True},
    )


async def test_client_requirement_from_option(
        check_estimate_stq_client_requirements,
        conf_exp3_requirements_from_options,
        config_dynamic_requirements,
):
    await conf_exp3_requirements_from_options(
        requirement='dynamic_requirement',
    )
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'cargo_options': ['auto_courier']},
        finish_estimate_taxi_requirements={
            'door_to_door': True,
            'dynamic_requirement': True,
        },
        cargo_pricing_taxi_requirements={
            'dynamic_requirement': True,
            'door_to_door': True,
        },
    )


async def test_client_requirement_from_option_kwargs(
        check_estimate_stq_client_requirements,
        conf_exp3_requirements_from_options,
        config_dynamic_requirements,
        experiments3,
):
    await conf_exp3_requirements_from_options(
        requirement='dynamic_requirement',
    )
    exp3_recorder = experiments3.record_match_tries(
        'cargo_matcher_options_to_requirements_map',
    )
    await check_estimate_stq_client_requirements(
        claim_client_requirements={
            'cargo_options': ['auto_courier', 'another_option'],
        },
        finish_estimate_taxi_requirements={
            'door_to_door': True,
            'dynamic_requirement': True,
        },
        cargo_pricing_taxi_requirements={
            'dynamic_requirement': True,
            'door_to_door': True,
        },
    )

    tries = await exp3_recorder.get_match_tries(ensure_ntries=2)
    for try_ in tries:
        assert try_.kwargs['zone'] == 'moscow'
        assert (
            try_.kwargs['corp_client_id'] == 'corp_client_id_12312312312312312'
        )
        assert try_.kwargs['tariff'] == 'express'
        assert try_.kwargs['tariff_plan_series_id'] == 'tariff_plan_id_123'
    assert tries[0].kwargs['option'] == 'auto_courier'
    assert tries[1].kwargs['option'] == 'another_option'


async def test_estimate_switchable_requirements_bool_switched_on(
        check_estimate_stq_client_requirements,
        config_dynamic_requirements,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['api', 'corp_cabinet'])
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'dynamic_requirement': True},
        finish_estimate_taxi_requirements={
            'door_to_door': True,
            'dynamic_requirement': True,
        },
        cargo_pricing_taxi_requirements={
            'dynamic_requirement': True,
            'door_to_door': True,
        },
    )


async def test_estimate_switchable_requirements_bool_switched_off(
        check_estimate_stq_client_requirements,
        config_dynamic_requirements,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=[])
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'dynamic_requirement': True},
        finish_estimate_taxi_requirements={'door_to_door': True},
        finish_estimate_warnings=[
            {
                'code': 'requirement_unavailable',
                'details_args': {'item_title': 'dynamic_requirement'},
                'details_code': 'estimating.warning.requirement_unavailable',
                'source': 'taxi_requirements',
            },
        ],
        cargo_pricing_taxi_requirements={'door_to_door': True},
    )


async def test_estimate_switchable_requirements_bool_false_switched_off(
        check_estimate_stq_client_requirements,
        config_dynamic_requirements,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=[])
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'dynamic_requirement': False},
        finish_estimate_taxi_requirements={'door_to_door': True},
        finish_estimate_warnings=[
            {
                'code': 'requirement_unavailable',
                'details_args': {'item_title': 'dynamic_requirement'},
                'details_code': 'estimating.warning.requirement_unavailable',
                'source': 'taxi_requirements',
            },
        ],
        cargo_pricing_taxi_requirements={'door_to_door': True},
    )


async def test_estimate_switchable_requirements_wrong_experiment(
        check_estimate_stq_client_requirements,
        config_dynamic_requirements,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['wrong'])
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'dynamic_requirement': True},
        finish_estimate_taxi_requirements={'door_to_door': True},
        finish_estimate_warnings=[
            {
                'code': 'requirement_unavailable',
                'details_args': {'item_title': 'dynamic_requirement'},
                'details_code': 'estimating.warning.requirement_unavailable',
                'source': 'taxi_requirements',
            },
        ],
        cargo_pricing_taxi_requirements={'door_to_door': True},
    )


async def test_estimate_switchable_requirements_kwargs(
        check_estimate_stq_client_requirements,
        config_dynamic_requirements,
        config_bool_switchable_requirement,
        conf_exp3_switchable_requirement,
        experiments3,
):
    await conf_exp3_switchable_requirement(visible_in=['api'])
    exp3_recorder = experiments3.record_match_tries(
        'cargo_matcher_switchable_requirement_enabled',
    )
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'dynamic_requirement': True},
        finish_estimate_taxi_requirements={
            'door_to_door': True,
            'dynamic_requirement': True,
        },
        cargo_pricing_taxi_requirements={
            'dynamic_requirement': True,
            'door_to_door': True,
        },
    )

    tries = await exp3_recorder.get_match_tries(ensure_ntries=1)
    kwargs = tries[0].kwargs
    assert kwargs['corp_client_id'] == 'corp_client_id_12312312312312312'
    assert kwargs['zone'] == 'moscow'
    assert kwargs['tariff'] == 'express'
    assert not kwargs['is_c2c']


async def test_estimate_switchable_requirements_select(
        check_estimate_stq_client_requirements,
        config_dynamic_requirements,
        config_select_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['corp_cabinet'])
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'dynamic_requirement': 1},
        finish_estimate_taxi_requirements={
            'door_to_door': True,
            'dynamic_requirement': 1,
        },
        cargo_pricing_taxi_requirements={
            'dynamic_requirement': 1,
            'door_to_door': True,
        },
    )


async def test_estimate_switchable_requirements_multiselect(
        check_estimate_stq_client_requirements,
        config_dynamic_requirements,
        config_multiselect_switchable_requirement,
        conf_exp3_switchable_requirement,
):
    await conf_exp3_switchable_requirement(visible_in=['api'])
    await check_estimate_stq_client_requirements(
        claim_client_requirements={'dynamic_requirement': [1, 2]},
        finish_estimate_taxi_requirements={
            'door_to_door': True,
            'dynamic_requirement': [1, 2],
        },
        cargo_pricing_taxi_requirements={
            'dynamic_requirement': [1, 2],
            'door_to_door': True,
        },
    )


@pytest.mark.config(
    CARGO_TYPE_LIMITS=conftest.get_default_cargo_type_limits(),
    CARGO_MATCHER_REQUIRE_MIDDLE_POINT=True,
    CARGO_MATCHER_MIDDLE_POINT_FIELDS={
        'requirement_postfix': {
            'cargo_type': {
                'lcv_m': {'value': '_lcv_m', 'tariffs': ['cargocorp']},
                'lcv_l': {'value': '_lcv_l', 'tariffs': ['cargocorp']},
                'van': {'value': '_van', 'tariffs': ['cargocorp']},
            },
        },
        'cargocorp': 'fake_middle_point_cargocorp',
        'courier': 'fake_middle_point_express',
        'express': 'fake_middle_point_express',
    },
)
@pytest.mark.parametrize(
    'client_requirements, finish_estimate_request, has_params',
    [
        pytest.param(
            {'cargo_type': 'lcv_l', 'cargo_loaders': 1, 'taxi_class': 'cargo'},
            {
                'zone_id': 'moscow',
                'is_delayed': False,
                'cars': [
                    {
                        'taxi_class': 'cargocorp',
                        'client_taxi_class': 'cargo',
                        'taxi_requirements': {
                            'cargo_type': 'lcv_l',
                            'cargo_loaders': 1,
                            'cargo_points': [2, 2],
                            'cargo_points_field': (
                                'fake_middle_point_cargocorp_lcv_l'
                            ),
                        },
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
            },
            True,
            marks=pytest.mark.experiments3(
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='cargo_replace_cargo_to_cargocorp',
                consumers=['cargo-matcher/estimate'],
                clauses=[],
                default_value={'enabled': True},
            ),
        ),
        pytest.param(
            {'cargo_type': 'lcv_m', 'cargo_loaders': 1, 'taxi_class': 'cargo'},
            {
                'zone_id': 'moscow',
                'is_delayed': False,
                'cars': [
                    {
                        'taxi_class': 'cargocorp',
                        'client_taxi_class': 'cargo',
                        'taxi_requirements': {
                            'cargo_type': 'lcv_m',
                            'cargo_loaders': 1,
                            'cargo_points': [2, 2],
                            'cargo_points_field': (
                                'fake_middle_point_cargocorp_lcv_m'
                            ),
                        },
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
            },
            True,
            marks=pytest.mark.experiments3(
                match={'predicate': {'type': 'true'}, 'enabled': True},
                name='cargo_replace_cargo_to_cargocorp',
                consumers=['cargo-matcher/estimate'],
                clauses=[],
                default_value={'enabled': True},
            ),
        ),
        (
            {'taxi_class': 'express'},
            {
                'zone_id': 'moscow',
                'is_delayed': False,
                'cars': [
                    {
                        'taxi_class': 'express',
                        'items': [{'id': 123, 'quantity': 1}],
                        'taxi_requirements': {
                            'door_to_door': True,
                            'cargo_points': [1],
                            'cargo_points_field': 'fake_middle_point_express',
                        },
                    },
                ],
                'offer': {
                    'offer_id': 'taxi_offer_id_1',
                    'price': '999.001',
                    'price_raw': 999,
                },
                'currency': 'RUB',
                'currency_rules': conftest.get_currency_rules(),
            },
            False,
        ),
    ],
)
async def test_fake_middle_point(
        mockserver,
        stq_runner,
        mock_claims_full,
        mock_int_api_profile,
        mock_finish_estimate,
        client_requirements: Optional[dict],
        finish_estimate_request: dict,
        has_params,
        exp3_cargo_add_fake_middle_point,
):
    mock_claims_full.response['items'] = [
        conftest.get_cargo_item(has_params=has_params),
    ]
    mock_claims_full.response['client_requirements'] = client_requirements
    mock_claims_full.response['route_points'].append(
        {
            'id': 3,
            'address': {'fullname': '', 'coordinates': [34.2, 41.3]},
            'contact': {
                'personal_phone_id': 'personal_phone_id_456',
                'personal_email_id': 'personal_email_id_123',
                'name': 'Petya',
            },
            'type': 'destination',
            'visit_order': 3,
            'visit_status': 'pending',
            'visited_at': {},
        },
    )
    mock_finish_estimate['expected-request'] = finish_estimate_request

    @mockserver.json_handler('/int-authproxy/v1/orders/estimate')
    def _orders_estimate(request):
        if client_requirements['taxi_class'] == 'cargo':
            field = finish_estimate_request['cars'][0]['taxi_requirements'][
                'cargo_points_field'
            ]
            assert request.json['requirements'][field] == [2, 2]
            assert request.json['selected_class'] == 'cargocorp'
        else:
            assert request.json['requirements'][
                'fake_middle_point_express'
            ] == [1]
        return conftest.get_default_estimate_response(
            request.json['selected_class'],
        )

    await stq_runner.cargo_matcher_claim_estimating.call(task_id='claim_id_1')
    assert mock_finish_estimate['handler'].times_called == 1
    assert _orders_estimate.times_called == 1
