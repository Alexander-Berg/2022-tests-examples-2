import pandas as pd
import pytest

from grocery_tasks.autoorder.calc import orders_calculator


@pytest.mark.parametrize(
    'stock_prediction, min_stock, max_stock, fixed_order, expected_order',
    [
        (200, 300, 400, 300, 300),
        (200, 300, 400, 200, 200),
        (200, 300, 400, 100, 100),
        (200, 300, 0, 300, 300),
        (200, 300, 0, 100, 100),
        (200, 200, 0, 200, 0),
        (200, 100, 0, 100, 0),
        (200, 200, 400, 1000, 0),
        (200, 100, 400, 1000, 0),
        (200, 300, 200, 0, None),
        (200, 300, 300, 0, 100),
        (200, 300, 400, 0, 200),
        (200, 200, 300, 0, 0),
        (200, 100, 300, 0, 0),
        (200, 0, 300, 0, 100),
        (200, 0, 200, 0, 0),
        (200, 0, 100, 0, 0),
        (200, 0, 300, 100, 100),
        (200, 0, 200, 200, 0),
        (200, 0, 100, 300, 0),
        (200, 0, 0, 0, None),
        (200, 100, 0, 0, None),
        (200, 200, 0, 0, None),
        (200, 300, 0, 0, None),
        (200, 0, 0, 100, None),
        (200, 0, 0, 200, None),
        (200, 0, 0, 300, None),
        (-100, 200, 300, 0, 300),
        (-0.9, 200, 300, 0, 300),
        (-0.5, 200, 300, 0, 300),
        (-0.3, 200, 300, 0, 300),
        (0.0, 200, 300, 0, 300),
        (0.1, 200, 300, 0, 299),
        (0.5, 200, 300, 0, 299),
        (0.9, 200, 300, 0, 299),
        (257.9, 200, 300, 0, 0),
        (-100, 0, 300, 0, 300),
        (-0.9, 0, 300, 0, 300),
        (-0.5, 0, 300, 0, 300),
        (-0.3, 0, 300, 0, 300),
        (0.0, 0, 300, 0, 300),
        (0.1, 0, 300, 0, 299),
        (0.5, 0, 300, 0, 299),
        (0.9, 0, 300, 0, 299),
        (299.1, 0, 300, 0, 0),
    ],
)
def test_fix_order(
        stock_prediction, min_stock, max_stock, fixed_order, expected_order,
):
    fixed_order_row = pd.Series(
        {'min_stock': min_stock, 'max_stock': max_stock, 'order': fixed_order},
    )

    order = orders_calculator.get_fixed_order(
        stock_prediction, fixed_order_row,
    )

    assert order == expected_order
