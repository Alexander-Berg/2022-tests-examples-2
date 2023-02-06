# pylint: disable=protected-access
# pylint: disable=redefined-outer-name
import numpy as np
import pandas as pd
import pytest

from grocery_tasks.autoorder.calc import distribute_order


@pytest.mark.parametrize(
    'orders, target_order, expected_fit_orders',
    [
        ([20, 10, 10, 30, 40, 10], 40, [20, 10, 10, 0, 0, 0]),
        ([20, 10, 10, 30, 40, 10], 117, [20, 10, 10, 30, 40, 7]),
        ([20, 10, 10, 30, 40, 10], 126, [20, 10, 10, 30, 40, 10]),
        ([20, 10, 10, 30, 40, 10], 0, [0, 0, 0, 0, 0, 0]),
        ([20], 19, [19]),
        ([20], 21, [20]),
        ([20], 0, [0]),
    ],
)
def test_fit_to_sum(orders, target_order, expected_fit_orders):
    input_df = pd.Series(orders).to_frame(name='order')
    input_df['order_cumsum'] = input_df['order'].cumsum()
    input_df['target_order'] = target_order

    fit_orders = input_df.apply(distribute_order._fit_to_sum, axis='columns')

    assert fit_orders.equals(pd.Series(expected_fit_orders))


@pytest.fixture(scope='function')
def input_df(request):
    (
        size,
        coeff_num,
        stock_prediction,
        target_order,
        total_demand_prediction,
    ) = request.param
    return pd.DataFrame(
        {
            'supplier_id': [100] * size,
            'store_id': list(range(size)),
            'product_id': [1000] * size,
            'coeff_num': coeff_num,
            'coeff_denom': [100] * size,
            'target_order': [target_order] * size,
            'total_demand_prediction': total_demand_prediction,
            'quant': [10] * size,
            'max_order': np.NaN,
            'stock_prediction': stock_prediction,
        },
    )


@pytest.fixture(scope='function')
def expected_result_df(request):
    size, distributed_order = request.param
    return pd.DataFrame(
        {
            'supplier_id': [100] * size,
            'store_id': list(range(size)),
            'product_id': [1000] * size,
            'distributed_order': distributed_order,
        },
    )


@pytest.mark.parametrize(
    'input_df, expected_result_df',
    [
        (
            (
                5,  # количество лавок
                [20, 20, 20, 20, 20],  # пропорции заказов в процентах
                [5, 4, 3, 2, 1],  # остатки на лавках
                43,  # требуемая сумма всех заказов
                [0] * 5,  # total_demand_prediction
            ),
            (
                5,  # количество лавок
                [3, 10, 10, 10, 10],  # ожидаемое распределение заказов
            ),
        ),
        (
            (5, [20, 20, 20, 20, 20], [0, 0, 0, 0, 0], 43, [3, 2, 5, 6, 3]),
            (5, [10, 3, 10, 10, 10]),
        ),
        (
            (5, [50, 50, 0, 0, 0], [0, 0, 0, 0, 0], 43, [0] * 5),
            (5, [30, 13, 0, 0, 0]),
        ),
        (
            (5, [50, 1, 1, 1, 47], [0, 0, 0, 0, 0], 124, [0] * 5),
            (5, [70, 0, 0, 0, 54]),
        ),
        (
            (5, [50, 1, 1, 1, 47], [0, 0, 0, 0, 0], 1249, [0] * 5),
            (5, [630, 20, 9, 0, 590]),
        ),
        (
            (5, [24, 17, 16, 30, 13], [0, 0, 0, 0, 0], 0, [0] * 5),
            (5, [0, 0, 0, 0, 0]),
        ),
        ((1, [100], [0], 39, [0]), (1, [39])),
        ((1, [100], [0], 0, [0]), (1, [0])),
    ],
    indirect=True,
)
def test_distribute_order(input_df, expected_result_df):
    result_df = distribute_order._distribute_order(
        input_df, ['supplier_id', 'product_id'],
    )
    result_df = result_df[
        ['supplier_id', 'store_id', 'product_id', 'distributed_order']
    ]

    difference_df = pd.concat([result_df, expected_result_df]).drop_duplicates(
        keep=False,
    )

    assert difference_df.empty
