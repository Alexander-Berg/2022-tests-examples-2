import pytest

from billing_models.generated.models import goal_shift

from billing_functions.functions import calculate_goal_payoff


@pytest.mark.parametrize(
    'num_orders,expected_nrides,expected_amount',
    (
        (9, 0, '0'),
        (10, 10, '100'),
        (11, 10, '100'),
        (49, 10, '100'),
        (50, 50, '500'),
        (51, 50, '500'),
        (0, 0, '0'),
    ),
)
def test_calculate_bonus(
        make_query, num_orders, expected_nrides, expected_amount,
):
    query = make_query(num_orders)
    payment = calculate_goal_payoff.execute(query)
    expected = goal_shift.GoalSubvention(
        amount=expected_amount,
        amount_per_contract='0',
        step_nrides=expected_nrides,
    )
    assert payment.serialize() == expected.serialize()


@pytest.mark.parametrize(
    'nrides, nrides_per_contract, ' 'expected_amount_per_contract',
    (
        (10, 10, '100'),
        (10, 0, '0'),
        (0, 0, '0'),
        (20, 10, '50'),
        (51, 50, '490.1961'),
    ),
)
def test_calculate_bonus_shares(
        make_query, nrides, nrides_per_contract, expected_amount_per_contract,
):
    query = make_query(
        num_orders=nrides, num_orders_per_contract=nrides_per_contract,
    )
    payment = calculate_goal_payoff.execute(query)
    assert payment.amount_per_contract == expected_amount_per_contract


@pytest.fixture(name='make_query')
def _make_make_query():
    def _make_query(num_orders, num_orders_per_contract=0):
        return calculate_goal_payoff.GoalBonusQuery(
            steps=[
                goal_shift.GoalStepsItem(nrides=10, amount='100'),
                goal_shift.GoalStepsItem(nrides=50, amount='500'),
            ],
            nrides=num_orders,
            nrides_per_contract=num_orders_per_contract,
        )

    return _make_query
