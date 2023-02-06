import math

import pytest


PARAMETRIZE_PRICE_ROUNDING_BRAND_ID = 1
PARAMETRIZE_PRICE_ROUNDING = pytest.mark.parametrize(
    'should_include_pennies_in_price',
    [
        pytest.param(False, id='PRICE_ROUNDING config disabled'),
        pytest.param(
            True,
            marks=pytest.mark.config(
                EATS_NOMENCLATURE_PRICE_ROUNDING={
                    f'{PARAMETRIZE_PRICE_ROUNDING_BRAND_ID}': {
                        'should_include_pennies_in_price': True,
                    },
                },
            ),
            id='PRICE_ROUNDING config with enabled brand',
        ),
    ],
)


def proper_round(price):
    # because round() does not always work properly with *.5 values
    if price - math.floor(price) < 0.5:
        return math.floor(price)
    return math.ceil(price)


def rounded_price(response, key):
    for product in response[key]:
        product['price'] = proper_round(product['price'])
        if 'old_price' in product:
            product['old_price'] = proper_round(product['old_price'])
    return response
