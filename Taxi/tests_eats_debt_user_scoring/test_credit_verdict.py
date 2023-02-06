import pytest

from tests_eats_debt_user_scoring import helpers


@pytest.mark.parametrize(
    ('request_json', 'expected_response'),
    [
        (
            {
                'yandex_uid': '3456723',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '100.5',
                'service': 'eats',
                'payment_method': 'card',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': True},
        ),
        (
            {
                'yandex_uid': '123456',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '100.5',
                'service': 'eats',
                'payment_method': 'card',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': False},
        ),
        (
            {
                'yandex_uid': '2434523',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '5000',
                'service': 'eats',
                'payment_method': 'card',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': False},
        ),
        (
            {
                'yandex_uid': '2434523',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '1000',
                'service': 'grocery',
                'payment_method': 'googlepay',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': True},
        ),
        (
            {
                'yandex_uid': '2434523',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '2001',
                'service': 'grocery',
                'payment_method': 'googlepay',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': False},
        ),
    ],
)
@pytest.mark.experiments3(
    filename='eats_debt_user_scoring_credit_verdict.json',
)
async def test_credit_verdict(
        taxi_eats_debt_user_scoring, request_json, expected_response,
):
    response = await taxi_eats_debt_user_scoring.post(
        '/internal/eats-debt-user-scoring/v1/eats-credit/score',
        json=request_json,
    )

    assert response.status_code == 200
    response = response.json()
    assert response == expected_response


@pytest.mark.parametrize(
    ('request_json', 'expected_response', 'counters'),
    [
        # For payment method
        (
            {
                'yandex_uid': '3456723',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '3000',
                'service': 'eats',
                'payment_method': 'googlepay',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': True},
            helpers.make_counters(
                [
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'restaurant',
                        'payment_method': 'googlepay',
                        'orders_count': 1,
                    },
                ],
            ),
        ),
        (
            {
                'yandex_uid': '3456723',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '3001',
                'service': 'eats',
                'payment_method': 'googlepay',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': False},
            helpers.make_counters(
                [
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'restaurant',
                        'payment_method': 'googlepay',
                        'orders_count': 1,
                    },
                ],
            ),
        ),
        (
            {
                'yandex_uid': '3456723',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '3001',
                'service': 'eats',
                'payment_method': 'googlepay',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': False},
            helpers.make_counters(
                [
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'restaurant',
                        'payment_method': 'applepay',
                        'orders_count': 1,
                    },
                ],
            ),
        ),
        # For orders count
        (
            {
                'yandex_uid': '3456723',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '1000',
                'service': 'eats',
                'payment_method': 'card',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': True},
            helpers.make_counters(
                [
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'restaurant',
                        'payment_method': 'googlepay',
                        'orders_count': 4,
                    },
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'grocery',
                        'payment_method': 'applepay',
                        'orders_count': 6,
                    },
                ],
            ),
        ),
        (
            {
                'yandex_uid': '3456723',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '1001',
                'service': 'eats',
                'payment_method': 'card',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': True},
            helpers.make_counters(
                [
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'restaurant',
                        'payment_method': 'googlepay',
                        'orders_count': 4,
                    },
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'grocery',
                        'payment_method': 'applepay',
                        'orders_count': 6,
                    },
                ],
            ),
        ),
        (
            {
                'yandex_uid': '3456723',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '1000',
                'service': 'eats',
                'payment_method': 'card',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': True},
            helpers.make_counters(
                [
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'restaurant',
                        'payment_method': 'googlepay',
                        'orders_count': 4,
                    },
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'grocery',
                        'payment_method': 'applepay',
                        'orders_count': 5,
                    },
                ],
            ),
        ),
        # For service
        (
            {
                'yandex_uid': '3456723',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '2000',
                'service': 'eats',
                'payment_method': 'card',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': True},
            helpers.make_counters(
                [
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'restaurant',
                        'payment_method': 'googlepay',
                        'orders_count': 5,
                    },
                ],
            ),
        ),
        (
            {
                'yandex_uid': '3456723',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '2001',
                'service': 'eats',
                'payment_method': 'card',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': False},
            helpers.make_counters(
                [
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'restaurant',
                        'payment_method': 'googlepay',
                        'orders_count': 5,
                    },
                ],
            ),
        ),
        (
            {
                'yandex_uid': '3456723',
                'order_nr': 'order_1',
                'currency': 'RUB',
                'amount': '1000',
                'service': 'eats',
                'payment_method': 'card',
                'business': 'restaurant',
                'phone_id': 'phone_id',
                'is_disaster': True,
            },
            {'allow_credit': True},
            helpers.make_counters(
                [
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'restaurant',
                        'payment_method': 'googlepay',
                        'orders_count': 4,
                    },
                    {
                        'place_id': '1234',
                        'brand_id': '2112',
                        'business_type': 'grocery',
                        'payment_method': 'applepay',
                        'orders_count': 5,
                    },
                ],
            ),
        ),
    ],
)
@pytest.mark.experiments3(
    filename='eats_debt_user_scoring_credit_verdict_with_orders_stats.json',
)
@pytest.mark.config(
    EATS_DEBT_USER_SCORING_CHECK_ORDER_STATS={
        'check_order_stats': True,
        'mappings': {},
    },
)
async def test_credit_verdict_with_order_stats(
        taxi_eats_debt_user_scoring,
        request_json,
        expected_response,
        counters,
        eats_core_eater,
        eats_order_stats,
):
    eats_order_stats(counters=counters)
    response = await taxi_eats_debt_user_scoring.post(
        '/internal/eats-debt-user-scoring/v1/eats-credit/score',
        json=request_json,
    )

    assert response.status_code == 200
    response = response.json()
    assert response == expected_response
