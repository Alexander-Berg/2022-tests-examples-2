# pylint: disable=too-many-lines

import math

import pytest

from tests_eats_plus import configs
from tests_eats_plus import conftest

EXPAECTED_CASHBACK_INCOME = {
    'eda_part': 61,
    'decimal_eda_part': '61',
    'full': 182,
    'decimal_full': '182',
    'place_part': 121,
    'decimal_place_part': '121',
}


def get_hide_cashback_income_exp(result: str, doesnt_have_plus_test=False):
    if doesnt_have_plus_test:
        return pytest.mark.experiments3(
            name='eats_plus_hide_cashback_income',
            consumers=['eats-plus/hide_cashback_income'],
            is_config=True,
            clauses=[
                {
                    'title': 'Always match',
                    'value': {'hide_income': result},
                    'predicate': {
                        'init': {
                            'predicate': {
                                'init': {'arg_name': 'has_plus'},
                                'type': 'bool',
                            },
                        },
                        'type': 'not',
                    },
                },
            ],
            default_value={'hide_income': 'never'},
        )

    return pytest.mark.experiments3(
        name='eats_plus_hide_cashback_income',
        consumers=['eats-plus/hide_cashback_income'],
        is_config=True,
        default_value={'hide_income': result},
    )


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_cashback_checkout_happy_path(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 120})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'public_id': 'coke',
                },
            ],
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback_income': {
            'eda_part': 16,
            'decimal_eda_part': '16',
            'full': 47,
            'decimal_full': '47',
            'place_part': 31,
            'decimal_place_part': '31',
        },
        'cashback_outcome': 120,
        'decimal_cashback_outcome': '120',
        'hide_cashback_income': False,
        'cashback_outcome_details': [
            {'cashback_outcome': '120', 'service_type': 'product'},
        ],
        'has_plus': True,
    }


@pytest.mark.parametrize('currency', ['RUB'])
@pytest.mark.parametrize(
    'precision,income_round_policy,' 'cost,quantity,standard_response',
    [
        pytest.param(
            0,
            'half_up_round_policy',
            100.4,
            1,
            {
                'cashback_income': {
                    'eda_part': 5,
                    'decimal_eda_part': '5',
                    'full': 15,
                    'decimal_full': '15',
                    'place_part': 10,
                    'decimal_place_part': '10',
                },
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '99', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='rounds outcome down from 99.4 to 99',
        ),
        pytest.param(
            0,
            'half_up_round_policy',
            100.5,
            1,
            {
                'cashback_income': {
                    'eda_part': 5,
                    'decimal_eda_part': '5',
                    'full': 15,
                    'decimal_full': '15',
                    'place_part': 10,
                    'decimal_place_part': '10',
                },
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '99', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='rounds outcome down from 99.5 to 99',
        ),
        pytest.param(
            0,
            'ceiling_round_policy',
            100.1,
            1,
            {
                'cashback_income': {
                    'eda_part': 6,
                    'decimal_eda_part': '6',
                    'full': 17,
                    'decimal_full': '17',
                    'place_part': 11,
                    'decimal_place_part': '11',
                },
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '99', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='rounds income up, and outcome down',
        ),
        pytest.param(
            1,
            'half_up_round_policy',
            100.5,
            1,
            {
                'cashback_income': {
                    'eda_part': 5,
                    # 100.5 * 0.05 = 5.025 ~ 5
                    'decimal_eda_part': '5',
                    'full': 15,
                    'decimal_full': '15.1',
                    'place_part': 10,
                    # 100.5 * 0.10 = 10.05 ~ 10.1 (see round policy)
                    'decimal_place_part': '10.1',
                },
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99.5',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '99.5', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='keeps intact outcome 99.5 because precision is 1',
        ),
        pytest.param(
            1,
            'null_round_policy',
            100.5,
            1,
            {
                'cashback_income': {
                    'eda_part': 5,
                    # 100.5 * 0.05 = 5.025 ~ 5
                    'decimal_eda_part': '5',
                    'full': 15,
                    'decimal_full': '15',
                    'place_part': 10,
                    # 100.5 * 0.10 = 10.05 ~ 10.0 (see round policy)
                    'decimal_place_part': '10',
                },
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99.5',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '99.5', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='keeps outcome 99.5 intact despite null r.p. bc prec=1',
        ),
        pytest.param(
            1,
            'half_up_round_policy',
            101.5,
            5,
            {
                'cashback_income': {
                    'eda_part': 5,
                    'decimal_eda_part': '5.1',
                    'full': 15,
                    'decimal_full': '15.3',
                    'place_part': 10,
                    'decimal_place_part': '10.2',
                },
                'cashback_outcome': 96,
                'decimal_cashback_outcome': '96.5',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '96.5', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='handles quantity: 101.5 becomes 96.5',
        ),
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@configs.EATS_PLUS_ENABLED_CURRENCIES
@configs.EATS_PLUS_CURRENCY_FOR_PLUS
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_checkout_rounding_and_precision(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        taxi_config,
        currency,
        precision,
        income_round_policy,
        cost,
        quantity,
        standard_response,
        eats_order_stats,
):
    taxi_config.set_values(
        {
            'EATS_PLUS_ROUNDING_AND_PRECISION_BY_CURRENCY_V2': {
                currency: {
                    'display_precision': precision,
                    'income_round_policy': income_round_policy,
                    'income_precision': precision,
                    'outcome_precision': precision,
                },
            },
        },
    )

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({currency: 10000})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': currency,
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {
                    'service_type': 'product',
                    'quantity': str(quantity),
                    'cost': str(cost),
                    'public_id': 'coke',
                },
            ],
            'total_cost': str(cost),
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == standard_response


@pytest.mark.parametrize('currency', ['RUB', 'BYN', 'KZT'])
@pytest.mark.parametrize(
    'quantity,cost,minimum,standard_response',
    [
        pytest.param(
            1,
            100,
            1,
            {
                'cashback_income': {
                    'eda_part': 5,
                    'decimal_eda_part': '5',
                    'full': 15,
                    'decimal_full': '15',
                    'place_part': 10,
                    'decimal_place_part': '10',
                },
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '99', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='outcome = 100 - 1 = 99',
        ),
        pytest.param(
            1,
            100,
            3,
            {
                'cashback_income': {
                    'eda_part': 5,
                    'decimal_eda_part': '5',
                    'full': 15,
                    'decimal_full': '15',
                    'place_part': 10,
                    'decimal_place_part': '10',
                },
                'cashback_outcome': 97,
                'decimal_cashback_outcome': '97',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '97', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='outcome = 100 - 3 = 97',
        ),
        pytest.param(
            3,
            100,
            4,
            {
                'cashback_income': {
                    'eda_part': 5,
                    'decimal_eda_part': '5',
                    'full': 15,
                    'decimal_full': '15',
                    'place_part': 10,
                    'decimal_place_part': '10',
                },
                'cashback_outcome': 88,
                'decimal_cashback_outcome': '88',
                'hide_cashback_income': False,
                'cashback_outcome_details': [
                    {'cashback_outcome': '88', 'service_type': 'product'},
                ],
                'has_plus': True,
            },
            id='outcome = 100 - (3 * 4) = 88',
        ),
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@configs.EATS_PLUS_ENABLED_CURRENCIES
@configs.EATS_PLUS_CURRENCY_FOR_PLUS
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_checkout_minimum_cannot_be_paid_by_cashback(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        taxi_config,
        quantity,
        cost,
        currency,
        minimum,
        standard_response,
        eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({currency: 10000})
    eats_order_stats()

    taxi_config.set_values(
        {'EATS_PLUS_MINIMUM_CANNOT_BE_PAID_BY_CASHBACK': {currency: minimum}},
    )
    taxi_config.set_values(
        {
            'EATS_PLUS_ROUNDING_AND_PRECISION_BY_CURRENCY_V2': {
                currency: {
                    'display_precision': 0,  # doesn't matter
                    'income_round_policy': 'half_up_round_policy',
                    'income_precision': 1,
                    'outcome_precision': 1,
                },
            },
        },
    )

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': currency,
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {
                    'service_type': 'product',
                    'quantity': str(quantity),
                    'cost': str(cost),
                    'public_id': 'coke',
                },
            ],
            'total_cost': str(cost),
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == standard_response


MULTI_SERVICES_JSON = {
    'yandex_uid': '3456723',
    'order_id': 'order_1',
    'currency': 'RUB',
    'place_id': {'place_id': '1', 'provider': 'eats'},
    'services': [
        {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
        {
            'service_type': 'product',
            'quantity': '3',
            'cost': '312.0',
            'public_id': 'coke',
        },
        {'service_type': 'product', 'quantity': '1', 'cost': '400.0'},
        {'service_type': 'product', 'quantity': '2', 'cost': '500.0'},
    ],
}


@pytest.mark.parametrize(
    'balance, income, outcome, total_cost',
    [
        pytest.param(
            800,
            {
                'eda_part': 45,
                'decimal_eda_part': '45',
                'full': 135,
                'decimal_full': '135',
                'place_part': 90,
                'decimal_place_part': '90',
            },
            800,
            1000.4,
            id='balance_less_than_total',
        ),
        # overriding actual cashback source sum by total_cost in test body,
        # total_cost is 1000.4, have delivery which does not count,
        # and quantity of product as minimum which cannot be paid by cashback,
        # so total of 1000.4 (total cost) - (sum of quantities) - 100.5
        # accounts here, which is 893.9,
        # and integer, 'old', cashback must round it down to 893,
        # while decimal one, according to the currency-dependent precision,
        # may return 893.9 'as is',
        # or round using null_round_policy, and return 893
        pytest.param(
            100000,
            {
                'eda_part': 45,
                'decimal_eda_part': '45',
                'full': 135,
                'decimal_full': '135',
                'place_part': 90,
                'decimal_place_part': '90',
            },
            1000.4 - (3 + 2 + 1) - 100.5,
            1000.4,
            id='balance_greater_than_total',
        ),
        pytest.param(
            100000,
            {
                'eda_part': 0,
                'decimal_eda_part': '0',
                'full': 0,
                'decimal_full': '0',
                'place_part': 0,
                'decimal_place_part': '0',
            },
            0,
            0,
            id='zero total cost',
        ),
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_checkout_total_services_cost(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        balance,
        income,
        outcome,
        total_cost,
        eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': balance})
    eats_order_stats()

    request_json = MULTI_SERVICES_JSON.copy()
    request_json['total_cost'] = str(total_cost)

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback', json=request_json,
    )

    assert response.status_code == 200
    response = response.json()
    expected_response = {
        'cashback_income': income,
        'cashback_outcome': math.floor(outcome),
        'decimal_cashback_outcome': str(math.floor(outcome)),
        'hide_cashback_income': False,
        'has_plus': True,
    }
    if math.floor(outcome):
        expected_response['cashback_outcome_details'] = [
            {
                'cashback_outcome': str(math.floor(outcome)),
                'service_type': 'product',
            },
        ]
    assert response == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_checkout_multiple_services(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 120})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback', json=MULTI_SERVICES_JSON,
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback_income': EXPAECTED_CASHBACK_INCOME,
        'cashback_outcome': 120,
        'decimal_cashback_outcome': '120',
        'hide_cashback_income': False,
        'cashback_outcome_details': [
            {'cashback_outcome': '120', 'service_type': 'product'},
        ],
        'has_plus': True,
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_checkout_plus_million(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'public_id': 'coke',
                },
                {'service_type': 'product', 'quantity': '1', 'cost': '400.0'},
                {'service_type': 'product', 'quantity': '2', 'cost': '500.0'},
            ],
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback_income': {
            'eda_part': 61,
            'full': 182,
            'place_part': 121,
            'decimal_eda_part': '61',
            'decimal_full': '182',
            'decimal_place_part': '121',
        },
        'cashback_outcome': 1206,
        'decimal_cashback_outcome': '1206',
        'hide_cashback_income': False,
        'cashback_outcome_details': [
            {'cashback_outcome': '1206', 'service_type': 'product'},
        ],
        'has_plus': True,
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_checkout_doesnt_have_plus(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=False, has_cashback=False)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'public_id': 'coke',
                },
                {'service_type': 'product', 'quantity': '1', 'cost': '400.0'},
                {'service_type': 'product', 'quantity': '2', 'cost': '500.0'},
            ],
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback_income': EXPAECTED_CASHBACK_INCOME,
        'cashback_outcome': 0,
        'decimal_cashback_outcome': '0',
        'hide_cashback_income': False,
        'has_plus': False,
    }


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.parametrize(
    'hide_cashback_income, has_plus',
    [
        pytest.param(
            False,
            True,
            marks=[
                get_hide_cashback_income_exp('never'),
                pytest.mark.eats_discounts_match(
                    conftest.EATS_DISCOUNTS_MATCH,
                ),
            ],
            id='never_hide',
        ),
        pytest.param(
            True,
            True,
            marks=[
                get_hide_cashback_income_exp('always'),
                pytest.mark.eats_discounts_match(
                    conftest.EATS_DISCOUNTS_MATCH,
                ),
            ],
            id='always_hide',
        ),
        pytest.param(
            False,
            True,
            marks=[
                get_hide_cashback_income_exp('zero_cashback'),
                pytest.mark.eats_discounts_match(
                    conftest.EATS_DISCOUNTS_MATCH,
                ),
            ],
            id='hide_when_zero(has_cashback)',
        ),
        pytest.param(
            True,
            True,
            marks=[
                get_hide_cashback_income_exp('zero_cashback'),
                pytest.mark.eats_discounts_match(
                    [
                        {
                            'subquery_id': 'offer_0',
                            'place_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '0.0',
                                },
                            },
                            'yandex_cashback': {
                                'menu_value': {
                                    'value_type': 'fraction',
                                    'value': '0.0',
                                },
                            },
                        },
                    ],
                ),
            ],
            id='hide_when_zero(doesnt_have_cashback)',
        ),
        pytest.param(
            True,
            False,
            marks=[
                get_hide_cashback_income_exp('always', True),
                pytest.mark.eats_discounts_match(
                    conftest.EATS_DISCOUNTS_MATCH,
                ),
            ],
            id='always_hide_if_no_plus',
        ),
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
async def test_cashback_checkout_hide_income_flag(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        hide_cashback_income,
        has_plus,
):
    passport_blackbox(has_plus=has_plus, has_cashback=True)
    plus_wallet({'RUB': 120})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'public_id': 'coke',
                },
            ],
        },
    )

    assert response.status_code == 200
    response = response.json()

    assert response['hide_cashback_income'] == hide_cashback_income


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_checkout_without_plus_cashback(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=False)
    plus_wallet({'RUB': 120})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '312.0',
                    'public_id': 'coke',
                },
            ],
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback_income': {
            'eda_part': 16,
            'decimal_eda_part': '16',
            'full': 47,
            'decimal_full': '47',
            'place_part': 31,
            'decimal_place_part': '31',
        },
        'cashback_outcome': 120,
        'decimal_cashback_outcome': '120',
        'hide_cashback_income': False,
        'cashback_outcome_details': [
            {'cashback_outcome': '120', 'service_type': 'product'},
        ],
        'has_plus': True,
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.parametrize(
    ['product', 'cashback_income', 'place_id'],
    [
        (
            {
                'service_type': 'product',
                'quantity': '3',
                'cost': '10000.0',
                'public_id': 'coke',
            },
            {
                'eda_part': 500,
                'decimal_eda_part': '500',
                'full': 1500,
                'decimal_full': '1500',
                'place_part': 1000,
                'decimal_place_part': '1000',
            },
            '1',
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_checkout_discount_without_max(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        product,
        cashback_income,
        place_id,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 120})

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'is_first_order': True,
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': place_id, 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                product,
            ],
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback_income': cashback_income,
        'cashback_outcome': 120,
        'decimal_cashback_outcome': '120',
        'hide_cashback_income': False,
        'cashback_outcome_details': [
            {'cashback_outcome': '120', 'service_type': 'product'},
        ],
        'has_plus': True,
    }
