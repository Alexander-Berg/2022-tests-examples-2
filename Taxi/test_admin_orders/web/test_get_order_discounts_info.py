import pytest

from admin_orders.internal.order_sections import discounts
from test_admin_orders.web import helpers


case_discount = helpers.case_getter(  # pylint: disable=C0103
    'calc_method,cost,yaplus_multiplier,discount_value,discount_price,'
    'max_discount,expected_result',
    calc_method='fixed',
    yaplus_multiplier=None,
)


@pytest.mark.nofilldb()
@pytest.mark.parametrize(
    case_discount.params,
    [
        # -----------------------------------
        # cases with BASE_PRICE = FIXED PRICE
        # -----------------------------------
        # fixed price, discount, no Plus
        case_discount(
            cost=70,
            discount_value=0.3,
            discount_price=100,
            expected_result={
                'price': 100,
                'value': 0.3,
                'discount_price': 70,
                'base_price': 100,
            },
        ),
        # fixed price, discount and Plus, base_price = fixed price
        case_discount(
            cost=126,
            discount_value=0.3,
            discount_price=200,
            yaplus_multiplier=0.9,
            expected_result={
                'price': 180,
                'value': 0.3,
                'discount_price': 126,
                'base_price': 200,
            },
        ),
        # --------------------------------------
        # cases with BASE_PRICE = PRICE RESTORED
        # --------------------------------------
        # taximeter price, discount, no Plus
        case_discount(
            calc_method='taximeter',
            cost=95,
            discount_value=0.3,
            discount_price=100,
            expected_result={
                'price': 135.71,
                'value': 0.3,
                'discount_price': 95,
                'base_price': 135.71,
            },
        ),
        # taximeter price, discount and Plus
        case_discount(
            calc_method='taximeter',
            cost=95,
            discount_value=0.3,
            discount_price=100,
            yaplus_multiplier=0.9,
            expected_result={
                'price': 135.71,
                'value': 0.3,
                'discount_price': 95,
                'base_price': 150.79,
            },
        ),
        # taximeter price, discount with working limit, no Plus
        case_discount(
            calc_method='taximeter',
            cost=95,
            discount_value=0.3,
            discount_price=100,
            max_discount=20,
            expected_result={
                'price': 115,
                'value': 0.3,
                'discount_price': 95,
                'base_price': 115,
                'discount_limit': 20,
            },
        ),
        # taximeter price, discount with working limit, and Plus
        case_discount(
            calc_method='taximeter',
            cost=95,
            discount_value=0.3,
            discount_price=100,
            max_discount=20,
            yaplus_multiplier=0.9,
            expected_result={
                'price': 115,
                'value': 0.3,
                'discount_price': 95,
                'base_price': 127.78,
                'discount_limit': 20,
            },
        ),
        # taximeter price, discount with large limit, no Plus
        case_discount(
            calc_method='taximeter',
            cost=95,
            discount_value=0.3,
            discount_price=100,
            max_discount=50,
            expected_result={
                'price': 135.71,
                'value': 0.3,
                'discount_price': 95,
                'base_price': 135.71,
            },
        ),
        # taximeter price, discount with large limit, and Plus
        case_discount(
            calc_method='taximeter',
            cost=95,
            discount_value=0.3,
            discount_price=100,
            max_discount=50,
            yaplus_multiplier=0.9,
            expected_result={
                'price': 135.71,
                'value': 0.3,
                'discount_price': 95,
                'base_price': 150.79,
            },
        ),
    ],
)
def test_extract_discount_data(
        calc_method,
        cost,
        yaplus_multiplier,
        discount_value,
        discount_price,
        max_discount,
        expected_result,
):
    struct_data = dict(
        calc_method=calc_method,
        cost=cost,
        discount_value=discount_value,
        discount_price=discount_price,
        discount_max_absolute_value=max_discount,
    )
    result = discounts.extract_discount_data(struct_data, yaplus_multiplier)
    assert result == expected_result
