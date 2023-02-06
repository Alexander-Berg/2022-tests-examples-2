# pylint: disable=too-many-lines
import math

import pytest

from tests_eats_plus import configs
from tests_eats_plus import conftest

SETTINGS_USE_EXP = {
    'handler_enabled': True,
    'use_experiment': False,
    'handler_default': {'title': 'А тут у нас кешбек'},
}

SETTINGS_USE_EXP_WITH_OUTCOME_FIELDS = {
    'handler_enabled': True,
    'use_experiment': False,
    'handler_default': {
        'title': 'А тут у нас кешбек',
        'outcome_title': 'За этот заказ баллов не будет',
        'outcome_description': 'Потому что вы списываете свои',
    },
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


@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
async def test_cashback_cart_happy_path(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
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
        'cashback': 182,
        'decimal_cashback': '182',
        'cashback_outcome': 1206,
        'decimal_cashback_outcome': '1206',
        'hide_cashback_income': False,
        'title': 'А тут у нас кешбек',
    }


@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
# @pytest.mark.parametrize('currency', ['RUB', 'KZT', 'BYN'])
@pytest.mark.parametrize('currency', ['RUB', 'KZT', 'BYN'])
@pytest.mark.parametrize(
    'precision, income_round_policy, cost, quantity, standard_response',
    [
        pytest.param(
            0,
            'half_up_round_policy',
            100,
            1,
            {
                'cashback': 15,
                'decimal_cashback': '15',
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99',
                'hide_cashback_income': False,
                'title': 'А тут у нас кешбек',
            },
            id='standard (without rounding)',
        ),
        pytest.param(
            1,
            'half_up_round_policy',
            100.51,
            1,
            {
                'cashback': 15,
                'decimal_cashback': '15.1',
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99.5',
                'hide_cashback_income': False,
                'title': 'А тут у нас кешбек',
            },
            id='rounds down to precision 1 (99.51 -> 99.5)',
        ),
        pytest.param(
            0,
            'ceiling_round_policy',
            100.1,
            1,
            {
                'cashback': 17,
                'decimal_cashback': '17',
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99',
                'hide_cashback_income': False,
                'title': 'А тут у нас кешбек',
            },
            id='rounds decimal outcome down from 99.1 to 99',
        ),
    ],
)
@configs.EATS_PLUS_ENABLED_CURRENCIES
@configs.EATS_PLUS_CURRENCY_FOR_PLUS
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
async def test_cashback_rounding_and_precision(
        taxi_eats_plus,
        taxi_config,
        passport_blackbox,
        plus_wallet,
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
    plus_wallet({currency: 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
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
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == standard_response


@pytest.mark.parametrize('currency', ['RUB', 'KZT', 'BYN'])
@pytest.mark.parametrize(
    'quantity, cost, minimum, standard_response',
    [
        pytest.param(
            1,
            100,
            2,
            {
                'cashback': 15,
                'decimal_cashback': '15',
                'cashback_outcome': 98,
                'decimal_cashback_outcome': '98',
                'hide_cashback_income': False,
                'title': 'А тут у нас кешбек',
            },
            id='outcome is 98 (100 - 2)',
        ),
        pytest.param(
            1,
            100,
            0.1,
            {
                'cashback': 15,
                'decimal_cashback': '15',
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99.9',
                'hide_cashback_income': False,
                'title': 'А тут у нас кешбек',
            },
            id='outcome is 99.9 (100 - 0.1',
        ),
        pytest.param(
            2,
            100,
            0.1,
            {
                'cashback': 15,
                'decimal_cashback': '15',
                'cashback_outcome': 99,
                'decimal_cashback_outcome': '99.8',
                'hide_cashback_income': False,
                'title': 'А тут у нас кешбек',
            },
            id='outcome is 99.8 (100 - 0.1 * 2)',
        ),
    ],
)
@configs.EATS_PLUS_ENABLED_CURRENCIES
@configs.EATS_PLUS_CURRENCY_FOR_PLUS
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_cart_minimum_cannot_be_paid_by_cashback(
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
    plus_wallet({currency: 1000000})
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
        'internal/eats-plus/v1/cart/cashback',
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
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == standard_response


@pytest.mark.parametrize(
    'balance, income, outcome, total_cost',
    [
        # total - delivery = 893
        pytest.param(800, 135, 800, 1000.4, id='balance_less_than_total'),
        pytest.param(
            894,
            135,
            1000 - (3 + 2 + 1) - 100.5,
            1000.4,
            id='balance_greater_than_total',
        ),
        pytest.param(800, 0, 0, 0, id='total cost is zero'),
    ],
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_cart_total_services_cost(
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
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
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
            'total_cost': str(total_cost),
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback': math.floor(income),
        'decimal_cashback': str(math.floor(income)),
        'cashback_outcome': math.floor(outcome),
        'decimal_cashback_outcome': str(math.floor(outcome)),
        'hide_cashback_income': False,
        'title': 'А тут у нас кешбек',
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(filename='exp3_eats_plus_cart_cashback.json')
@pytest.mark.config(
    EATS_PLUS_CART_PRESENTATION_SETTINGS={
        'handler_enabled': True,
        'use_experiment': True,
        'handler_default': {'title': 'А тут у нас кешбек'},
    },
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_cart_experiment_data(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
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
        'cashback': 182,
        'decimal_cashback': '182',
        'cashback_outcome': 1206,
        'decimal_cashback_outcome': '1206',
        'hide_cashback_income': False,
        'description': 'Описание к кешбеку',
        'deeplink': 'eats://fires-deeplink',
        'title': 'Смотри какой кешбек',
        'outcome_title': 'За этот заказ баллов не будет',
        'outcome_description': 'Потому что вы списываете свои',
    }


@pytest.mark.parametrize(
    'location,expected_response,expected_code',
    [
        (
            {'latitude': 55.750028, 'longitude': 37.534397},
            {
                'cashback': 182,
                'cashback_outcome': 1206,
                'decimal_cashback': '182',
                'decimal_cashback_outcome': '1206',
                'hide_cashback_income': False,
                'title': '',
            },
            200,
        ),
        ({'latitude': 55.798910, 'longitude': 49.105788}, None, 204),
        (
            {'latitude': 12.3456, 'longitude': 12.3456},
            {
                'cashback': 182,
                'cashback_outcome': 1206,
                'decimal_cashback': '182',
                'decimal_cashback_outcome': '1206',
                'hide_cashback_income': False,
                'title': '',
            },
            200,
        ),
        ({'latitude': 2.000, 'longitude': 2.000}, None, 204),
    ],
)
@pytest.mark.eats_plus_regions_cache(
    [
        {
            'id': 333,
            'name': 'Moscow',
            'slug': 'moscow',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [11.1111, 11.1111, 22.2222, 22.2222],
            'center': [12.3456, 12.3456],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [213, 216],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
        {
            'id': 2,
            'name': 'SPB',
            'slug': 'spb',
            'genitive': '',
            'isAvailable': True,
            'isDefault': True,
            'bbox': [1.000, 1.000, 3.000, 3.000],
            'center': [2.000, 2.000],
            'timezone': 'Europe/Moscow',
            'sort': 1,
            'yandexRegionIds': [321, 911],
            'country': {
                'code': 'RU',
                'id': 35,
                'name': 'Российская Федерация',
            },
        },
    ],
)
@pytest.mark.experiments3(filename='exp3_eats_plus_check_geozone.json')
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_cart_check_location(
        taxi_eats_plus,
        location,
        expected_response,
        expected_code,
        passport_blackbox,
        plus_wallet,
        eats_plus_regions_cache,
        eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'location': location,
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

    assert response.status_code == expected_code
    if expected_code == 200:
        response = response.json()
        assert response == expected_response


@pytest.mark.config(
    EATS_PLUS_OPTIN_ENABLED_CITIES={
        'check_location': False,
        'cities': ['ru-mow'],
    },
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_cart_check_location_disabled(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'location': {'latitude': 55.798910, 'longitude': 49.105788},
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
        'cashback': 182,
        'cashback_outcome': 1206,
        'decimal_cashback': '182',
        'decimal_cashback_outcome': '1206',
        'hide_cashback_income': False,
        'title': '',
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(
    EATS_PLUS_CART_PRESENTATION_SETTINGS={
        'handler_enabled': True,
        'use_experiment': True,
        'handler_default': {'title': 'А тут у нас кешбек'},
    },
)
@pytest.mark.parametrize(
    'has_plus,expected_response',
    [
        (
            True,
            {
                'cashback': 182,
                'decimal_cashback': '182',
                'cashback_outcome': 1206,
                'decimal_cashback_outcome': '1206',
                'hide_cashback_income': False,
                'deeplink': 'eats://fires-deeplink',
                'title': 'Вернется баллами на плюс',
            },
        ),
        (
            False,
            {
                'cashback': 182,
                'decimal_cashback': '182',
                'cashback_outcome': 0,
                'decimal_cashback_outcome': '0',
                'hide_cashback_income': False,
                'deeplink': 'eats://fires-deeplink',
                'description': 'С подпиской их можно тратить',
                'title': 'На Плюсе копятся баллы',
            },
        ),
    ],
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cart_cashback_subscription.json',
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_cart_check_sub(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        has_plus,
        expected_response,
        eats_order_stats,
):
    passport_blackbox(has_plus=has_plus, has_cashback=has_plus)
    plus_wallet({'RUB': 2812})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
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
    assert response == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_cart_first_order_excluded_businesses(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '3456725',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {'service_type': 'delivery', 'quantity': '1', 'cost': '100.5'},
                {
                    'service_type': 'product',
                    'quantity': '3',
                    'cost': '15000.0',
                    'public_id': 'coke',
                },
            ],
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response == {
        'cashback': 2250,
        'decimal_cashback': '2250',
        'cashback_outcome': 14997,
        'decimal_cashback_outcome': '14997',
        'hide_cashback_income': False,
        'title': 'А тут у нас кешбек',
    }


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(
    EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP_WITH_OUTCOME_FIELDS,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_cart_returns_outcome_fields(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    """
    Тест проверяет, что в ответе ручки передаются два новых поля
    (outcome_field и outcome_description), которые нужны для
    информирования пользователя, что он не получит баллов за этот заказ, т.к.
    списывает свои.
    Новые поля передаются в дефолтном хендлере конфига, в котором мы их
    берем, т.к. не попали в эксп.
    """

    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
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
        'cashback': 182,
        'decimal_cashback': '182',
        'cashback_outcome': 1206,
        'decimal_cashback_outcome': '1206',
        'title': 'А тут у нас кешбек',
        'hide_cashback_income': False,
        'outcome_title': 'За этот заказ баллов не будет',
        'outcome_description': 'Потому что вы списываете свои',
    }


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.config(EATS_PLUS_CART_PRESENTATION_SETTINGS=SETTINGS_USE_EXP)
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
async def test_cashback_cart_hide_income_flag(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        hide_cashback_income,
        has_plus,
):
    passport_blackbox(has_plus=has_plus, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': [
                {
                    'service_type': 'product',
                    'quantity': '1',
                    'cost': '100',
                    'public_id': 'coke',
                },
            ],
        },
    )

    assert response.status_code == 200
    response = response.json()
    assert response['hide_cashback_income'] == hide_cashback_income


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.experiments3(filename='exp3_eats_plus_cart_cashback.json')
@pytest.mark.config(
    EATS_PLUS_CART_PRESENTATION_SETTINGS={
        'handler_enabled': True,
        'use_experiment': True,
        'handler_default': {
            'title': (
                'Неважно, мы попадаем в эксп, '
                'и не берем отсюда title, конфиг только для флага use_exp'
            ),
        },
    },
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(conftest.EATS_DISCOUNTS_MATCH)
async def test_cashback_cart_experiment_with_outcome_fields(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    """
    Тест проверяет, что в ответе ручки передаются два новых поля
    (outcome_field и outcome_description), которые нужны для
    информирования пользователя, что он не получит баллов за этот заказ, т.к.
    списывает свои.
    Новые поля передаются в эксперименте, в который мы в этом тесте попадаем.
    """
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback',
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
        'cashback': 182,
        'decimal_cashback': '182',
        'cashback_outcome': 1206,
        'decimal_cashback_outcome': '1206',
        'hide_cashback_income': False,
        'description': 'Описание к кешбеку',
        'deeplink': 'eats://fires-deeplink',
        'title': 'Смотри какой кешбек',
        'outcome_title': 'За этот заказ баллов не будет',
        'outcome_description': 'Потому что вы списываете свои',
    }


@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(
    [
        {
            'subquery_id': 'offer_1',
            'place_cashback': {
                'menu_value': {'value_type': 'fraction', 'value': '15.0'},
            },
        },
        {
            'subquery_id': 'offer_2',
            'place_cashback': {
                'menu_value': {'value_type': 'fraction', 'value': '15.0'},
            },
        },
    ],
)
async def test_cashback_cart_bulk(
        taxi_eats_plus, passport_blackbox, plus_wallet, eats_order_stats,
):
    passport_blackbox(has_plus=True, has_cashback=True)
    plus_wallet({'RUB': 1000000})
    eats_order_stats()
    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/cart/cashback-bulk',
        json={
            'yandex_uid': '3456723',
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'shipping_type': 'delivery',
            'services_offers': [
                {
                    'id': 1,
                    'services': [
                        {
                            'service_type': 'delivery',
                            'quantity': '1',
                            'cost': '100.5',
                        },
                        {
                            'service_type': 'product',
                            'quantity': '3',
                            'cost': '312.0',
                            'public_id': 'coke',
                        },
                    ],
                    'total_cost': '1037.5',
                },
                {
                    'id': 2,
                    'services': [
                        {
                            'service_type': 'delivery',
                            'quantity': '1',
                            'cost': '500',
                        },
                        {
                            'service_type': 'product',
                            'quantity': '2',
                            'cost': '300',
                            'public_id': 'coke',
                        },
                        {
                            'service_type': 'product',
                            'quantity': '1',
                            'cost': '400',
                            'public_id': 'meat',
                        },
                    ],
                    'total_cost': '1200',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert (
        sorted(
            response.json()['cashback_offers'], key=lambda offer: offer['id'],
        )
        == [
            {
                'id': 1,
                'cashback_offer': {
                    'cashback': 47,
                    'decimal_cashback': '47',
                    'cashback_outcome': 309,
                    'decimal_cashback_outcome': '309',
                    'title': '',
                },
            },
            {
                'id': 2,
                'cashback_offer': {
                    'cashback': 105,
                    'decimal_cashback': '105',
                    'cashback_outcome': 697,
                    'decimal_cashback_outcome': '697',
                    'title': '',
                },
            },
        ]
    )
