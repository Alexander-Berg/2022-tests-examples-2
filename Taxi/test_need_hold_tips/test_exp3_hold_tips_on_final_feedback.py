import pytest


HANDLE_URL = '/internal/tips/v1/need-hold-tips'


@pytest.mark.config(TIME_BEFORE_TAKE_TIPS=3601)  # != value in exp
@pytest.mark.pgsql('tips', files=['tips.sql'])
@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='hold_tips_on_final_feedback',
    consumers=['tips'],
    default_value={'time_before_take_tips': 3600},
)
async def test_hold_tips_on_final_feedback_experiment(taxi_tips):
    order_id = 'order_1_card'
    response = await taxi_tips.post(HANDLE_URL, params={'order_id': order_id})
    assert response.status_code == 200
    resp = response.json()
    assert resp['time_before_take_tips'] == 3600
