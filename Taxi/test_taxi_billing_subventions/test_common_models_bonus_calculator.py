import pytest

from taxi import billing

from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'bonus_calculator_json, base_driver_pay_json, expected_bonus_json',
    [
        (
            '220_guarantee_bonus_calculator.json',
            '100_rub.json',
            '120_rub.json',
        ),
        ('220_guarantee_bonus_calculator.json', '0_rub.json', '220_rub.json'),
        ('220_guarantee_bonus_calculator.json', '230_rub.json', '0_rub.json'),
        ('220_extra_bonus_calculator.json', '230_rub.json', '220_rub.json'),
    ],
)
@pytest.mark.nofilldb()
def test_calculate_bonus(
        bonus_calculator_json,
        base_driver_pay_json,
        expected_bonus_json,
        load_py_json_dir,
):
    bonus_calculator: models.BonusCalculator
    base_driver_pay: billing.Money
    expected_bonus: billing.Money

    bonus_calculator, base_driver_pay, expected_bonus = load_py_json_dir(
        'test_calculate_bonus',
        bonus_calculator_json,
        base_driver_pay_json,
        expected_bonus_json,
    )
    actual_bonus = bonus_calculator.calculate_bonus(base_driver_pay, 0)
    assert actual_bonus == expected_bonus
