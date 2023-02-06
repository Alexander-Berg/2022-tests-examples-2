import pytest

from taxi import billing

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'bonus_calculator_json, num_orders, expected_bonus_json',
    [
        ('single_step_bonus.json', 0, '0_rub.json'),
        ('single_step_bonus.json', 9, '0_rub.json'),
        ('single_step_bonus.json', 10, '30_rub.json'),
        ('three_steps_bonus.json', 9, '0_rub.json'),
        ('three_steps_bonus.json', 10, '30_rub.json'),
        ('three_steps_bonus.json', 11, '30_rub.json'),
        ('three_steps_bonus.json', 19, '30_rub.json'),
        ('three_steps_bonus.json', 20, '40_rub.json'),
        ('three_steps_bonus.json', 21, '40_rub.json'),
        ('three_steps_bonus.json', 29, '40_rub.json'),
        ('three_steps_bonus.json', 30, '50_rub.json'),
        ('three_steps_bonus.json', 31, '50_rub.json'),
        ('three_steps_bonus.json', 99, '50_rub.json'),
    ],
)
@pytest.mark.nofilldb()
def test_calculate_bonus(
        bonus_calculator_json,
        num_orders,
        expected_bonus_json,
        load_py_json_dir,
):
    bonus_calculator: models.StepsBonusCalculator
    expected_bonus: billing.Money
    bonus_calculator, expected_bonus = load_py_json_dir(
        'test_calculate_bonus', bonus_calculator_json, expected_bonus_json,
    )
    zero_rubles = billing.Money.zero('RUB')
    actual_bonus = bonus_calculator.calculate_bonus(zero_rubles, num_orders)
    assert actual_bonus == expected_bonus
