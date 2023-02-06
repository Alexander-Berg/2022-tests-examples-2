import pytest

from billing_models.generated import models

from billing_functions import consts
from billing_functions.functions.core.commissions import park_calc


@pytest.mark.json_obj_hook(
    BaseParkCommissionRule=models.BaseParkCommissionRule,
    OrderParkCommissionRule=models.OrderParkCommissionRule,
)
def test_get_rule_or_die_rule(load_py_json):
    rules = load_py_json('rules.json')
    order_rule = park_calc.get_order_rule_or_die(rules)
    assert order_rule.kind == consts.ParkCommissionRuleKind.ORDER

    subvention_rule = park_calc.get_subvention_rule_or_die(rules)
    assert subvention_rule.kind == consts.ParkCommissionRuleKind.SUBVENTION


@pytest.mark.json_obj_hook(
    BaseParkCommissionRule=models.BaseParkCommissionRule,
    OrderParkCommissionRule=models.OrderParkCommissionRule,
    ParkCommission=park_calc.OrderCommission,
)
@pytest.mark.parametrize(
    'test_data_json, calc_func',
    [
        ('subvention.json', park_calc.calculate_from_subvention),
        #
        ('order.json', park_calc.calculate_from_order),
        ('order_with_driver_workshift.json', park_calc.calculate_from_order),
        (
            'order_with_zero_commissions_and_cost.json',
            park_calc.calculate_from_order,
        ),
        ('order_with_zero_eventual_cost.json', park_calc.calculate_from_order),
        (
            'order_with_zero_total_commission.json',
            park_calc.calculate_from_order,
        ),
    ],
)
async def test_calc_from_order(test_data_json, calc_func, *, load_py_json):
    test_data = load_py_json(test_data_json)
    results = calc_func(**test_data['kwargs'])
    assert results == test_data['results']
