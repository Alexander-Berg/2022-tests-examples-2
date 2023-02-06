import numpy as np

from projects.autoorder.offline_exps.simulate import (
    _custom_accumulate,
    calc_writeoffs_predictions,
    reset_onhand,
    reduce_onhand_before_supply,
    calc_stock_prediction,
    calc_final_order,
    calc_todays_order,
)


def test_custom_accumulate():
    np.testing.assert_array_almost_equal(
        _custom_accumulate(np.array([2, -1, -3, 2, 4, -6, 2, 1, 3])),
        np.array([2.0, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 0.0]),
    )


def test_calc_writeoffs_predictions():
    planned_writeoffs = np.array([0, 0, 4, 0, 0, 5, 0, 0, 3, 0])
    predictions = np.array([1.5, 1.4, 1.2, 1.1, 1.0, 0.9, 0.7, 0.3, 0.3, 0.3])

    np.testing.assert_array_almost_equal(
        calc_writeoffs_predictions(
            planned_writeoffs=planned_writeoffs,
            demand_predictions=predictions,
        ),
        np.array([0.0, 0.0, 0.0, 0.0, 0.0, 1.9, 0.0, 0.0, 1.7, 0]),
    )


def test_reset_onhand():
    onhand_by_supply_date = [1, 0, 3, 0, 2, 0, 5, 0, 2]
    purchases = 8

    np.testing.assert_array_almost_equal(
        reset_onhand(
            onhand_by_supply_date=onhand_by_supply_date, purchases=purchases,
        ),
        np.array([0, 0, 0, 0, 0, 0, 3, 0, 2]),
    )


def test_reduce_onhand_before_supply():
    onhand = np.array([10, 0, 0, 0, 0, 0])
    supply = np.array([0, 3, 0, 4, 0, 5])
    writeoffs_predictions = np.array([0, 0, 8, 0, 0, 4])
    predictions = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0])

    np.testing.assert_almost_equal(
        reduce_onhand_before_supply(
            supply=supply,
            writeoffs_predictions=writeoffs_predictions,
            demand_predictions=predictions,
            onhand=onhand,
        ),
        4,
    )


def test_calc_stock_prediction():
    all_onhand = 10
    supply = np.array([0, 3, 0, 4, 0, 5, 0, 0, 0, 0])
    writeoffs_predictions = np.array([0, 0, 8, 0, 0, 4, 0, 0, 5, 0])
    predictions = np.array([1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0])
    order_lag = 6

    np.testing.assert_almost_equal(
        calc_stock_prediction(
            supply=supply,
            writeoffs_predictions=writeoffs_predictions,
            demand_predictions=predictions,
            order_lag=order_lag,
            all_onhand=all_onhand,
        ),
        -5,
    )


def test_calc_final_order():
    np.testing.assert_almost_equal(
        calc_final_order(quant=6, safety_stock=3, stock_prediction=-5), 12,
    )


def test_calc_todays_order():
    period = 10
    index = 0
    quant = 6
    order_lag = 2
    num_days = 5
    shelf_life = 7
    hand_safety_stock = 0
    all_predictions = np.array([1.9] * period)
    onhand_by_supply_date = np.array([11] + [0] * (period * 2 - 1))
    planned_supply = np.array([0] * period)
    safety_stock = np.array([1] * period)

    output = calc_todays_order(
        index=index,
        quant=quant,
        order_lag=order_lag,
        num_days=num_days,
        shelf_life=shelf_life,
        all_demand_predictions=all_predictions,
        onhand_by_supply_date=onhand_by_supply_date,
        planned_supply=planned_supply,
        safety_stock=safety_stock,
        hand_safety_stock=hand_safety_stock,
    )

    np.testing.assert_almost_equal(output, 0)


if __name__ == '__main__':
    test_custom_accumulate()
    test_calc_writeoffs_predictions()
    test_reset_onhand()
    test_reduce_onhand_before_supply()
    test_calc_stock_prediction()
    test_calc_final_order()
    test_calc_todays_order()
