# pylint: disable=redefined-outer-name
import pytest

from discounts_operation_calculations.algorithms import katusha
from discounts_operation_calculations.algorithms import preprocessing
from discounts_operation_calculations.internals import error as error_lib


def convert_default_dict_to_dict(obj):
    if isinstance(obj, (tuple, list)):
        return type(obj)(convert_default_dict_to_dict(i) for i in obj)
    if isinstance(obj, dict):
        return {k: convert_default_dict_to_dict(v) for k, v in obj.items()}

    return obj


@pytest.fixture(scope='function')
def calculator(load_dataframe_from_csv):
    data = load_dataframe_from_csv('test_data.csv')
    data = data.set_index(['segment', 'price_from', 'discount'])
    yield katusha.SequentialOptimalCurveCalculator(data, 50)


@pytest.fixture(scope='function')
def calculator_budget_stop(load_dataframe_from_csv):
    # replace all not_chosen priorities to avoid break by priority
    # condition, and break only by budget constraints
    data = load_dataframe_from_csv('test_data.csv')
    data = data.set_index(['segment', 'price_from', 'discount'])
    data.loc[
        data.priority == preprocessing.DiscountPriority.not_chosen, 'priority',
    ] = preprocessing.DiscountPriority.calculated
    yield katusha.SequentialOptimalCurveCalculator(data, 50)


async def test_sequential_optimal_curve(calculator):
    budget = 10000
    results = calculator.calc(budget)
    assert convert_default_dict_to_dict(results) == (
        {'control': {75: 0.0}},
        pytest.approx(10.86624),
        0,
        {
            'control': katusha.SegmentMeta(
                budget=pytest.approx(10.86624),
                new_gmv=pytest.approx(2879800.0),
                avg_discount=pytest.approx(3.773262032085561e-06),
                max_price_with_discount=0,
                max_discount_percent=0.0,
            ),
        },
    )
    assert calculator.calc(100000) != results


async def test_sequential_optimal_curve_same_budget(calculator):
    budget = 10000
    results = calculator.calc(budget)

    assert calculator.calc(budget) == results


@pytest.mark.parametrize('calc', ['calculator', 'calculator_budget_stop'])
async def test_sequential_optimal_curve_over_the_top_budget(calc, request):
    calculator = request.getfixturevalue(calc)

    budget = 10e100
    results = calculator.calc(budget)

    for i in range(10):
        assert calculator.calc(budget + i * 100500) == results


async def test_sequential_optimal_curve_decreased_budget(calculator):
    budget = 100000
    calculator.calc(budget)

    with pytest.raises(error_lib.KatushaError):
        calculator.calc(5000)
