import copy
import datetime

import pytest

from . import test_common


def set_details_screen_config(experiments3, value):
    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_order_context_subvention_details_screen',
        consumers=[
            '/internal/subvention-order-context/v1/subvention-details-screen',
        ],
        default_value={},
        clauses=[
            {
                'title': 'allways match',
                'predicate': {'type': 'true'},
                'value': value,
            },
        ],
    )


def gen_single_ontop_matched_rule(amount, rule_id=None):
    return {
        'amount': str(amount),
        'type': 'single_ontop',
        'rule': {
            'start': '2022-01-01T00:00:00+00:00',
            'tariff_class': 'econom',
            'zone': 'moscow',
            'id': (rule_id if rule_id is not None else 'mock_single_ontop_id'),
            'end': '2022-02-01T00:00:00+00:00',
            'budget_id': 'mock_budget_id',
        },
    }


def gen_single_ride_matched_rule(amount, rule_id=None):
    return {
        'amount': str(amount),
        'type': 'single_ride',
        'rule': {
            'id': (rule_id if rule_id is not None else 'mock_single_ride_id'),
            'budget_id': 'mock_budget_id',
            'draft_id': '100000',
            'tariff_class': 'econom',
            'zone': 'moscow',
            'rule_type': 'single_ride',
            'start': '2022-01-01T00:00:00+00:00',
            'end': '2022-02-01T00:00:00+00:00',
            'updated_at': '2022-01-01T00:00:00+00:00',
            'rates': [
                {'week_day': 'mon', 'start': '00:00', 'bonus_amount': '100'},
            ],
            'schedule_ref': 'mock_schedule_ref',
        },
    }


@pytest.mark.parametrize(
    'params, matched_rules, details_screen_config, expected_response',
    [
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [],
            # details_screen_config
            {'details_screen': {'type': 'detailed', 'is_collapsed': False}},
            # expected_response
            'expected_response_no_bonuses.json',
            id='no bonuses',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [gen_single_ride_matched_rule(180)],
            # details_screen_config
            {'details_screen': {'type': 'detailed', 'is_collapsed': False}},
            # expected_response
            'expected_response_single_ride_below_price_detailed.json',
            id='single_ride below price detailed',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [gen_single_ride_matched_rule(180)],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': True,
                    'yango_terms': True,
                },
            },
            # expected_response
            'expected_response_no_bonuses.json',
            id='single_ride below price simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [gen_single_ride_matched_rule(201.19)],
            # details_screen_config
            {'details_screen': {'type': 'detailed', 'is_collapsed': False}},
            # expected_response
            'expected_resposne_single_ride_detailed.json',
            id='single_ride detailed',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [gen_single_ride_matched_rule(201.19)],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': True,
                    'yango_terms': True,
                },
            },
            # expected_response
            'expected_resposne_single_ride_simple.json',
            id='single_ride simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [
                gen_single_ride_matched_rule(250),
                gen_single_ontop_matched_rule(15),
            ],
            # details_screen_config
            {'details_screen': {'type': 'detailed', 'is_collapsed': False}},
            # expected_response
            'expected_response_single_ride_and_single_ontop_detailed.json',
            id='single_ride & single_ontop detailed',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [
                gen_single_ride_matched_rule(250),
                gen_single_ontop_matched_rule(15),
            ],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': True,
                    'yango_terms': True,
                },
            },
            # expected_response
            'expected_response_single_ride_and_single_ontop_simple.json',
            id='single_ride & single_ontop simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [
                gen_single_ride_matched_rule(250),
                gen_single_ontop_matched_rule(10),
                gen_single_ontop_matched_rule(5),
            ],
            # details_screen_config
            {'details_screen': {'type': 'detailed', 'is_collapsed': False}},
            # expected_response
            'expected_response_single_ride_and_2_single_ontop_detailed.json',
            id='single_ride & 2 single_ontop detailed',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [
                gen_single_ride_matched_rule(180),
                gen_single_ontop_matched_rule(10),
                gen_single_ontop_matched_rule(5),
            ],
            # details_screen_config
            {'details_screen': {'type': 'detailed', 'is_collapsed': False}},
            # expected_response
            'expected_response_unappl_single_ride_plus_ontop_detailed.json',
            id='unapplied single_ride & single_ontops detailed',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [
                gen_single_ride_matched_rule(180),
                gen_single_ontop_matched_rule(10),
                gen_single_ontop_matched_rule(5),
            ],
            # details_screen_config
            {'details_screen': {'type': 'simple', 'is_collapsed': False}},
            # expected_response
            'expected_response_unappl_single_ride_plus_ontop_simple.json',
            id='unapplied single_ride & single_ontops simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': True,
            },
            # matched_rules
            [],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': False,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            'expected_response_compensation_simple.json',
            id='compensation simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': True,
            },
            # matched_rules
            [],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'detailed',
                    'is_collapsed': False,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            'expected_response_compensation_detailed.json',
            id='compensation detailed',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': False,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            'expected_response_no_bonuses.json',
            id='no compensation when payment_type=card',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 210,
                'payment_type_is_cash': True,
            },
            # matched_rules
            [],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'detailed',
                    'is_collapsed': False,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            'expected_response_no_bonuses.json',
            id='compensation is negative',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': True,
            },
            # matched_rules
            [gen_single_ride_matched_rule(100)],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'detailed',
                    'is_collapsed': False,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            (
                'expected_response_compensation_'
                'and_single_ride_below_price_detailed.json'
            ),
            id='compensation and single ride below price detailed',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': True,
            },
            # matched_rules
            [gen_single_ride_matched_rule(250)],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'detailed',
                    'is_collapsed': False,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            'expected_response_compensation_and_single_ride_detailed.json',
            id='compensation and single ride detailed',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 150,
                'payment_type_is_cash': True,
            },
            # matched_rules
            [
                gen_single_ride_matched_rule(180),
                gen_single_ontop_matched_rule(10),
                gen_single_ontop_matched_rule(25),
            ],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'detailed',
                    'is_collapsed': False,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            (
                'expected_response_compensation_'
                'single_ride_below_price_2_single_ontop_detailed.json'
            ),
            id=(
                'compensation & unapplied single_ride &'
                '2 single_ontop detailed'
            ),
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
                'ya_plus_amount': 30,
            },
            # matched_rules
            [],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': False,
                    'use_price_for_mone_instad_of_ride': True,
                },
            },
            # expected_response
            'expected_response_yandex_plus_simple.json',
            id='yandex.plus simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 200,
                'payment_type_is_cash': False,
                'ya_plus_amount': 30,
            },
            # matched_rules
            [],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'detailed',
                    'is_collapsed': False,
                    'use_price_for_mone_instad_of_ride': True,
                },
            },
            # expected_response
            'expected_response_yandex_plus_detailed.json',
            id='yandex.plus detailed',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': False,
            },
            # matched_rules
            [],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': False,
                    'use_price_for_mone_instad_of_ride': True,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            'expected_response_mone_simple.json',
            id='mone simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': True,
                'ya_plus_amount': 30,
            },
            # matched_rules
            [],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': False,
                    'use_price_for_mone_instad_of_ride': True,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            'expected_response_yandex_plus_compensation_simple.json',
            id='yandex.plus & compensation cash simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': False,
                'ya_plus_amount': 30,
            },
            # matched_rules
            [],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': False,
                    'use_price_for_mone_instad_of_ride': True,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            'expected_response_yandex_plus_compensation_simple.json',
            id='yandex.plus & compensation card simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': True,
                'ya_plus_amount': 30,
            },
            # matched_rules
            [gen_single_ride_matched_rule(220)],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': False,
                    'use_price_for_mone_instad_of_ride': True,
                    'yango_terms': True,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            'expected_response_yandex_plus_compensation_bonuses_simple.json',
            id='yandex.plus & compensation & bonuses simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': True,
                'ya_plus_amount': 190,
            },
            # matched_rules
            [gen_single_ride_matched_rule(220)],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'simple',
                    'is_collapsed': False,
                    'use_price_for_mone_instad_of_ride': True,
                    'yango_terms': True,
                    'show_user_price_compensation': True,
                },
            },
            # expected_response
            (
                'expected_response_yandex_plus_for_whole_cost_'
                'complicated_simple.json'
            ),
            id='yandex.plus for whole cost compilcated simple',
        ),
        pytest.param(
            # params
            {
                'driver_price': 200,
                'user_price': 190,
                'payment_type_is_cash': True,
            },
            # matched_rules
            [
                gen_single_ride_matched_rule(180),
                gen_single_ontop_matched_rule(25),
            ],
            # details_screen_config
            {
                'details_screen': {
                    'type': 'detailed',
                    'is_collapsed': False,
                    'display_subventions': False,
                },
            },
            # expected_response
            'expected_response_no_bonuses.json',
            id='screen with no subventions',
        ),
    ],
)
async def test_subvention_details_screen(
        taxi_subvention_order_context,
        mongodb,
        experiments3,
        bsx,
        load_json,
        params,
        matched_rules,
        details_screen_config,
        expected_response,
):
    set_details_screen_config(experiments3, details_screen_config)

    mongodb.subvention_order_context.insert_one(
        copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA),
    )

    for rule in matched_rules:
        bsx.add_match_rule(rule)

    response = await taxi_subvention_order_context.get(
        'internal/subvention-order-context/v1/subvention-details-screen',
        params=dict(
            order_id='order_id',
            driver_profile_id='uuid',
            park_id='dbid',
            locale='ru',
            application='Taximeter 12.00 (9999)',
            **params,
        ),
    )

    assert response.status_code == 200
    assert response.json() == load_json(expected_response)


@pytest.mark.parametrize(
    'context_data',
    [
        None,
        {
            'order_id': 'order_id',
            'dbid_uuid': 'dbid_uuid',
            'updated': datetime.datetime(2020, 1, 1, 12, 0),
            'value': {
                # imcomplete
            },
        },
    ],
)
async def test_no_context_404(
        taxi_subvention_order_context,
        mongodb,
        experiments3,
        bsx,
        context_data,
):
    set_details_screen_config(
        experiments3,
        {
            'details_screen': {'type': 'detailed', 'is_collapsed': True},
            'story_deeplink': 'mock_story_deeplink',
        },
    )

    if context_data:
        mongodb.subvention_order_context.insert_one(context_data)

    response = await taxi_subvention_order_context.get(
        'internal/subvention-order-context/v1/subvention-details-screen',
        params={
            'order_id': 'order_id',
            'driver_profile_id': 'uuid',
            'park_id': 'dbid',
            'driver_price': 100,
            'user_price': 100,
            'payment_type_is_cash': False,
            'locale': 'ru',
            'application': 'Taximeter 12.00 (9999)',
        },
    )

    assert response.status_code == 404


async def test_429(
        taxi_subvention_order_context, mongodb, experiments3, mockserver,
):
    set_details_screen_config(
        experiments3,
        {
            'details_screen': {'type': 'detailed', 'is_collapsed': True},
            'story_deeplink': 'mock_story_deeplink',
        },
    )

    mongodb.subvention_order_context.insert_one(
        copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA),
    )

    @mockserver.json_handler('/billing-subventions-x/v2/rules/match')
    def _mock_v2_rules_match(request):
        return mockserver.make_response(
            json={'message': 'Too many requests', 'code': 429}, status=429,
        )

    response = await taxi_subvention_order_context.get(
        'internal/subvention-order-context/v1/subvention-details-screen',
        params={
            'order_id': 'order_id',
            'driver_profile_id': 'uuid',
            'park_id': 'dbid',
            'driver_price': 100,
            'user_price': 100,
            'payment_type_is_cash': False,
            'locale': 'ru',
            'application': 'Taximeter 12.00 (9999)',
        },
    )

    assert response.status_code == 429


async def test_match_request(
        taxi_subvention_order_context, mongodb, experiments3, bsx, load_json,
):
    set_details_screen_config(
        experiments3,
        {
            'details_screen': {'type': 'detailed', 'is_collapsed': True},
            'story_deeplink': 'mock_story_deeplink',
        },
    )

    mongodb.subvention_order_context.insert_one(
        copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA),
    )

    response = await taxi_subvention_order_context.get(
        'internal/subvention-order-context/v1/subvention-details-screen',
        params={
            'order_id': 'order_id',
            'driver_profile_id': 'uuid',
            'park_id': 'dbid',
            'driver_price': 100,
            'user_price': 100,
            'payment_type_is_cash': False,
            'locale': 'ru',
            'application': 'Taximeter 12.00 (9999)',
        },
    )

    assert response.status_code == 200

    assert bsx.mock_v2_rules_match.times_called == 1
    assert bsx.mock_v2_rules_match.next_call()['request'].json == {
        'activity_points': 91,
        'geoareas': ['geoarea1'],
        'geonode': 'br_root/br_russia/br_moscow/moscow',
        'has_lightbox': False,
        'has_sticker': False,
        'reference_time': '2020-01-01T12:00:00+00:00',
        'rule_types': ['single_ride', 'single_ontop'],
        'tags': ['tag1', 'tag2', 'virtual_tag1'],
        'tariff_class': 'econom',
        'timezone': 'Europe/Moscow',
        'unique_driver_id': 'unique_driver_id',
        'zone': 'moscow',
    }


@pytest.mark.parametrize(
    'user_agent,expected_response',
    [
        ('Taximeter 10.23 (14433)', 'expected_response_kotlin.json'),
        ('Taximeter 12.0 (9999)', 'expected_response_flutter.json'),
        ('Taximeter 11.8 (3013817) ios', 'expected_response_flutter.json'),
    ],
)
async def test_flutter_constructor_api(
        taxi_subvention_order_context,
        mongodb,
        experiments3,
        bsx,
        load_json,
        expected_response,
        user_agent,
):
    set_details_screen_config(
        experiments3,
        {
            'details_screen': {
                'type': 'detailed',
                'is_collapsed': False,
                'show_user_price_compensation': True,
            },
        },
    )

    experiments3.add_config(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='subvention_order_context_constructor_api',
        consumers=[
            (
                '/internal/subvention-order-context/v1/'
                'subvention-details-screen:application'
            ),
        ],
        default_value={'api': 'kotlin'},
        clauses=[
            {
                'title': 'android >= 12.0',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'predicates': [
                                        {
                                            'init': {
                                                'value': 'android',
                                                'arg_name': (
                                                    'application_platform'
                                                ),
                                                'arg_type': 'string',
                                            },
                                            'type': 'eq',
                                        },
                                        {
                                            'init': {
                                                'value': 12,
                                                'arg_name': (
                                                    'application_version_major'
                                                ),
                                                'arg_type': 'int',
                                            },
                                            'type': 'gte',
                                        },
                                    ],
                                },
                                'type': 'all_of',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {'api': 'flutter'},
            },
            {
                'title': 'ios',
                'predicate': {
                    'init': {
                        'predicates': [
                            {
                                'init': {
                                    'value': 'ios',
                                    'arg_name': 'application_platform',
                                    'arg_type': 'string',
                                },
                                'type': 'eq',
                            },
                        ],
                    },
                    'type': 'all_of',
                },
                'value': {'api': 'flutter'},
            },
        ],
    )

    mongodb.subvention_order_context.insert_one(
        copy.deepcopy(test_common.DEFAULT_CONTEXT_DATA),
    )

    bsx.add_match_rule(gen_single_ride_matched_rule(180))

    response = await taxi_subvention_order_context.get(
        'internal/subvention-order-context/v1/subvention-details-screen',
        params={
            'order_id': 'order_id',
            'driver_profile_id': 'uuid',
            'park_id': 'dbid',
            'driver_price': 100,
            'user_price': 90,
            'payment_type_is_cash': True,
            'locale': 'ru',
            'application': user_agent,
        },
    )

    assert response.status_code == 200
    assert response.json() == load_json(expected_response)
