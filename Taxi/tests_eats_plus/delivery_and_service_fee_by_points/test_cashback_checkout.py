import pytest

from tests_eats_plus import conftest


CASHBACK_INCOME_DEFAULT = {
    'eda_part': 0,
    'full': 10,
    'place_part': 10,
    'decimal_eda_part': '0',
    'decimal_full': '10',
    'decimal_place_part': '10',
}

ZERO_CASHBACK_INCOME = {
    'eda_part': 0,
    'full': 0,
    'place_part': 0,
    'decimal_eda_part': '0',
    'decimal_full': '0',
    'decimal_place_part': '0',
}

SERVICES = [
    {'service_type': 'delivery', 'quantity': '1', 'cost': '100'},
    {'service_type': 'product', 'quantity': '1', 'cost': '100'},
    {'service_type': 'product', 'quantity': '1', 'cost': '100'},
    {'service_type': 'service_fee', 'quantity': '1', 'cost': '100'},
]

MATCH_DISCOUNTS_RESULT = [
    {
        'subquery_id': 'offer_0',
        'place_cashback': {
            'menu_value': {
                'value_type': 'fraction',
                'value': '5.0',
                'maximum_discount': '99999',
            },
        },
    },
]


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.parametrize(
    ['yandex_uid', 'discount_info', 'balance', 'outcome', 'expected_code'],
    [
        ('3456725', {'is_old': True, 'has_plus': True}, 1000, 297, 200),
        ('34567252', {'is_old': True, 'has_plus': True}, 250, 250, 200),
        ('3456725', {'is_old': True, 'has_plus': False}, 1000, 0, 200),
        ('3456725', {'is_old': True, 'has_plus': True}, 200, 200, 200),
        ('3456726', {'is_old': True, 'has_plus': True}, 1000, 198, 200),
        ('3456726', {'is_old': True, 'has_plus': False}, 1100, 0, 200),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(MATCH_DISCOUNTS_RESULT)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_delivery_and_service_fee_by_points.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
async def test_cashback_checkout_delivery_by_points(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        discount_info,
        expected_code,
        balance,
        outcome,
):
    passport_blackbox(has_plus=discount_info['has_plus'], has_cashback=True)
    plus_wallet({'RUB': balance})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'is_first_order': not discount_info['is_old'],
            'yandex_uid': yandex_uid,
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': SERVICES,
        },
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        expected_response = {
            'cashback_income': CASHBACK_INCOME_DEFAULT,
            'cashback_outcome': outcome if discount_info['has_plus'] else 0,
            'decimal_cashback_outcome': (
                str(outcome) if discount_info['has_plus'] else '0'
            ),
            'has_plus': discount_info['has_plus'],
            'hide_cashback_income': False,
        }
        if discount_info['has_plus']:
            cashback_outcome_details = [
                {
                    'cashback_outcome': str(min(balance, 198)),
                    'service_type': 'product',
                },
            ]
            if outcome != min(balance, 198):
                delivery = {
                    'cashback_outcome': str(outcome - min(balance, 198)),
                    'service_type': 'delivery',
                }
                cashback_outcome_details.append(delivery)

            if cashback_outcome_details:
                expected_response[
                    'cashback_outcome_details'
                ] = cashback_outcome_details

        assert response.json() == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.parametrize(
    ['yandex_uid', 'discount_info', 'balance', 'outcome', 'expected_code'],
    [
        ('34567251', {'is_old': True, 'has_plus': True}, 1000, 297, 200),
        ('34567251', {'is_old': True, 'has_plus': True}, 250, 250, 200),
        ('34567251', {'is_old': True, 'has_plus': False}, 1000, 0, 200),
        ('34567251', {'is_old': True, 'has_plus': True}, 200, 200, 200),
        ('34567261', {'is_old': True, 'has_plus': True}, 1000, 198, 200),
        ('34567261', {'is_old': True, 'has_plus': False}, 1100, 0, 200),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(MATCH_DISCOUNTS_RESULT)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_delivery_and_service_fee_by_points.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
async def test_cashback_checkout_service_fee_by_points(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        discount_info,
        expected_code,
        balance,
        outcome,
):
    passport_blackbox(has_plus=discount_info['has_plus'], has_cashback=True)
    plus_wallet({'RUB': balance})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'is_first_order': not discount_info['is_old'],
            'yandex_uid': yandex_uid,
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': SERVICES,
        },
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        expected_response = {
            'cashback_income': CASHBACK_INCOME_DEFAULT,
            'cashback_outcome': outcome if discount_info['has_plus'] else 0,
            'decimal_cashback_outcome': (
                str(outcome) if discount_info['has_plus'] else '0'
            ),
            'has_plus': discount_info['has_plus'],
            'hide_cashback_income': False,
        }
        if discount_info['has_plus']:
            cashback_outcome_details = [
                {
                    'cashback_outcome': str(min(balance, 198)),
                    'service_type': 'product',
                },
            ]
            if outcome != min(balance, 198):
                service_fee = {
                    'cashback_outcome': str(outcome - min(balance, 198)),
                    'service_type': 'service_fee',
                }
                cashback_outcome_details.append(service_fee)

            if cashback_outcome_details:
                expected_response[
                    'cashback_outcome_details'
                ] = cashback_outcome_details

        assert response.json() == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.parametrize(
    ['yandex_uid', 'discount_info', 'balance', 'outcome', 'expected_code'],
    [
        ('34567252', {'is_old': True, 'has_plus': True}, 1000, 396, 200),
        ('34567252', {'is_old': True, 'has_plus': True}, 350, 350, 200),
        ('34567252', {'is_old': True, 'has_plus': False}, 1000, 0, 200),
        ('34567252', {'is_old': True, 'has_plus': True}, 200, 200, 200),
        ('34567262', {'is_old': True, 'has_plus': True}, 1000, 198, 200),
        ('34567262', {'is_old': True, 'has_plus': False}, 1100, 0, 200),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match(MATCH_DISCOUNTS_RESULT)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_delivery_and_service_fee_by_points.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
async def test_cashback_checkout_delivery_and_service_fee_by_points(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        discount_info,
        expected_code,
        balance,
        outcome,
):
    passport_blackbox(has_plus=discount_info['has_plus'], has_cashback=True)
    plus_wallet({'RUB': balance})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'is_first_order': not discount_info['is_old'],
            'yandex_uid': yandex_uid,
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': SERVICES,
        },
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        expected_response = {
            'cashback_income': CASHBACK_INCOME_DEFAULT,
            'cashback_outcome': outcome if discount_info['has_plus'] else 0,
            'decimal_cashback_outcome': (
                str(outcome) if discount_info['has_plus'] else '0'
            ),
            'has_plus': discount_info['has_plus'],
            'hide_cashback_income': False,
        }
        if discount_info['has_plus']:
            cashback_outcome_details = [
                {
                    'cashback_outcome': str(min(balance, 198)),
                    'service_type': 'product',
                },
            ]
            if outcome != min(balance, 198):
                delivery_and_service_fee = outcome - min(balance, 198)

                delivery = {
                    'cashback_outcome': str(min(delivery_and_service_fee, 99)),
                    'service_type': 'delivery',
                }
                cashback_outcome_details.append(delivery)

                if delivery_and_service_fee != min(
                        delivery_and_service_fee, 99,
                ):
                    service_fee = {
                        'cashback_outcome': str(
                            min(delivery_and_service_fee - 99, 99),
                        ),
                        'service_type': 'service_fee',
                    }
                    cashback_outcome_details.append(service_fee)

            if cashback_outcome_details:
                expected_response[
                    'cashback_outcome_details'
                ] = cashback_outcome_details

        assert response.json() == expected_response


@pytest.mark.now('2020-11-26T00:00:00.000000Z')
@pytest.mark.parametrize(
    [
        'yandex_uid',
        'discount_info',
        'services_types',
        'outcome',
        'expected_code',
    ],
    [
        pytest.param(
            '3456725',
            {'is_old': True, 'has_plus': True},
            ['delivery'],
            99,
            200,
            id='plus user; delivery only',
        ),
        pytest.param(
            '34567251',
            {'is_old': True, 'has_plus': True},
            ['service_fee'],
            99,
            200,
            id='plus user; service fee only',
        ),
        pytest.param(
            '34567252',
            {'is_old': True, 'has_plus': True},
            ['delivery', 'service_fee'],
            99,
            200,
            id='plus user; delivery and service fee',
        ),
        pytest.param(
            '3456725',
            {'is_old': True, 'has_plus': False},
            None,
            None,
            404,
            id='non plus user',
        ),
        pytest.param(
            '34567253',
            {'is_old': True, 'has_plus': True},
            None,
            None,
            404,
            id='plus user; disabled',
        ),
    ],
)
@pytest.mark.eats_catalog_storage_cache(
    conftest.EATS_CATALOG_STORAGE_CACHE_DEFAULT_CONTENT,
)
@pytest.mark.eats_discounts_match([])
@pytest.mark.experiments3(
    filename='exp3_eats_plus_delivery_and_service_fee_by_points.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_cashback_discounts_source.json',
)
@pytest.mark.experiments3(
    filename='exp3_eats_plus_spend_in_non_plus_places.json',
)
async def test_cashback_checkout_fees_by_points_in_non_plus_places(
        taxi_eats_plus,
        passport_blackbox,
        plus_wallet,
        eats_order_stats,
        yandex_uid,
        discount_info,
        expected_code,
        services_types,
        outcome,
):
    passport_blackbox(has_plus=discount_info['has_plus'], has_cashback=True)
    plus_wallet({'RUB': 1000})
    eats_order_stats()

    response = await taxi_eats_plus.post(
        'internal/eats-plus/v1/checkout/cashback',
        json={
            'is_first_order': not discount_info['is_old'],
            'yandex_uid': yandex_uid,
            'order_id': 'order_1',
            'currency': 'RUB',
            'place_id': {'place_id': '1', 'provider': 'eats'},
            'services': SERVICES,
        },
    )

    assert response.status_code == expected_code
    if expected_code == 200:
        expected_response = {
            'cashback_income': ZERO_CASHBACK_INCOME,
            'cashback_outcome': outcome * len(services_types),
            'decimal_cashback_outcome': (str(outcome * len(services_types))),
            'has_plus': discount_info['has_plus'],
            'hide_cashback_income': False,
            'cashback_outcome_details': [
                {
                    'cashback_outcome': str(outcome),
                    'service_type': service_type,
                }
                for service_type in services_types
            ],
        }
        assert response.json() == expected_response
