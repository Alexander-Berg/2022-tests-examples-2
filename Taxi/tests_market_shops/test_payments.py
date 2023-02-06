# flake8: noqa
# pylint: disable=import-error,wildcard-import


def check_response(
        response,
        delivery_card,
        delivery_cash,
        prepayment_card,
        prepayment_other,
        prepayment_b2b,
):
    assert response.status_code == 200
    assert response.json() == {
        'delivery_card': delivery_card,
        'delivery_cash': delivery_cash,
        'prepayment_card': prepayment_card,
        'prepayment_other': prepayment_other,
        'prepayment_b2b': prepayment_b2b,
    }


async def test_payments_no_payments(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 1, 'user_region_id': 225, 'has_delivery': True},
    )
    check_response(response, False, False, False, False, False)


async def test_payments_delivery_cash(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/payments', {'shop_id': 2, 'user_region_id': 225},
    )
    check_response(response, False, False, False, False, False)
    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 2, 'user_region_id': 225, 'has_delivery': True},
    )
    check_response(response, False, True, False, False, False)


async def test_payments_delivery_card(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/payments', {'shop_id': 4, 'user_region_id': 225},
    )
    check_response(response, False, False, False, False, False)
    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 4, 'user_region_id': 225, 'has_delivery': True},
    )
    check_response(response, True, False, False, False, False)


async def test_payments_prepayment_other(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/payments', {'shop_id': 5, 'user_region_id': 225},
    )
    check_response(response, False, False, False, True, False)
    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 5, 'user_region_id': 225, 'has_delivery': True},
    )
    check_response(response, False, False, False, True, False)


async def test_payments_prepayment_card(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/payments', {'shop_id': 6, 'user_region_id': 225},
    )
    check_response(response, False, False, True, False, False)
    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 6, 'user_region_id': 225, 'has_delivery': True},
    )
    check_response(response, False, False, True, False, False)


async def test_payments_all(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/payments', {'shop_id': 7, 'user_region_id': 225},
    )
    check_response(response, False, False, True, True, False)
    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 7, 'user_region_id': 225, 'has_delivery': True},
    )
    check_response(response, True, True, True, True, False)


async def test_payments_prepayment_b2b(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {
            'shop_id': 1,
            'user_region_id': 225,
            'has_delivery': True,
            'is_b2b_marketplace': True,
        },
    )
    check_response(response, False, False, False, False, True)
    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {
            'shop_id': 6,
            'user_region_id': 225,
            'has_delivery': True,
            'is_b2b_marketplace': True,
        },
    )
    check_response(response, False, False, False, False, True)


async def test_payments_allowed_payment_methods(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {
            'shop_id': 7,
            'user_region_id': 225,
            'has_delivery': True,
            'allowed_payment_methods': 0,
        },
    )
    check_response(response, True, True, True, True, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {
            'shop_id': 7,
            'user_region_id': 225,
            'has_delivery': True,
            'allowed_payment_methods': 1,
        },
    )
    check_response(response, False, False, True, True, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {
            'shop_id': 7,
            'user_region_id': 225,
            'has_delivery': True,
            'allowed_payment_methods': 2,
        },
    )
    check_response(response, False, True, False, False, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {
            'shop_id': 7,
            'user_region_id': 225,
            'has_delivery': True,
            'allowed_payment_methods': 4,
        },
    )
    check_response(response, True, False, False, False, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {
            'shop_id': 7,
            'user_region_id': 225,
            'has_delivery': True,
            'allowed_payment_methods': 8,
        },
    )
    check_response(response, False, False, False, True, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {
            'shop_id': 7,
            'user_region_id': 225,
            'has_delivery': True,
            'allowed_payment_methods': 16,
        },
    )
    check_response(response, False, False, True, False, False)


async def test_payments_allowed_regions(taxi_market_shops):
    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 8, 'user_region_id': 225, 'has_delivery': True},
    )
    check_response(response, False, False, False, False, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 8, 'user_region_id': 213, 'has_delivery': True},
    )
    check_response(response, True, True, True, True, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 8, 'user_region_id': 13662, 'has_delivery': True},
    )
    check_response(response, True, True, True, True, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 8, 'user_region_id': 13584, 'has_delivery': True},
    )
    check_response(response, False, False, False, False, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 3, 'user_region_id': 213, 'has_delivery': True},
    )
    check_response(response, True, False, False, False, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 3, 'user_region_id': 13584, 'has_delivery': True},
    )
    check_response(response, True, False, False, False, False)

    response = await taxi_market_shops.post(
        'market-shops/v1/payments',
        {'shop_id': 3, 'user_region_id': 134, 'has_delivery': True},
    )
    check_response(response, False, False, False, True, False)
