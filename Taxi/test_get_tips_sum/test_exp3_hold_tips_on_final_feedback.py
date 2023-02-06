import pytest


HANDLE_URL = '/internal/tips/v1/get-tips-sum'


@pytest.mark.pgsql('tips', files=['tips.sql'])
@pytest.mark.now('2020-10-30T12:00:00Z')
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='hold_tips_on_final_feedback',
    consumers=['tips'],
    default_value={'time_before_take_tips': 3600},
)
@pytest.mark.parametrize(
    ['order_id', 'expected_has_tips_sum'],
    [
        ('order_1_above_exp_time_final', True),
        ('order_2_above_exp_time_not_final', True),
        ('order_3_below_exp_time_final', True),
        ('order_4_below_exp_time_not_final', False),
    ],
)
async def test_hold_tips_on_final_feedback_experiment(
        taxi_tips, order_id: str, expected_has_tips_sum: bool,
):
    response = await taxi_tips.post(HANDLE_URL, params={'order_id': order_id})
    assert response.status_code == 200
    has_tips_sum = response.json().get('new_tips_sum') is not None
    assert has_tips_sum == expected_has_tips_sum
