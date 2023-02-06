import pytest


TIPS_FEEDBACK_THRESHOLD_MARK = pytest.mark.experiments3(
    name='tips_feedback_threshold',
    consumers=['tips'],
    match={'enabled': True, 'predicate': {'type': 'true'}},
    default_value={'threshold': 4},
)
EXP_MARKS = [TIPS_FEEDBACK_THRESHOLD_MARK]

HANDLE_URL = '/internal/tips/v1/need-hold-tips'


@pytest.mark.pgsql('tips', files=['tips.sql'])
@pytest.mark.parametrize(
    ['order_id', 'expected_need_hold_tips'],
    [
        pytest.param('order_1_card', True),
        pytest.param('order_2_empty_feedback', True),
        pytest.param('order_3_rating_3', False),
        pytest.param('order_4_rating_4', False),
        pytest.param('order_5_rating_5', True),
        pytest.param('order_1_card', True, marks=EXP_MARKS),
        pytest.param('order_2_empty_feedback', True, marks=EXP_MARKS),
        pytest.param('order_3_rating_3', False, marks=EXP_MARKS),
        pytest.param('order_4_rating_4', True, marks=EXP_MARKS),
        pytest.param('order_5_rating_5', True, marks=EXP_MARKS),
    ],
)
async def test_feedback_local(
        taxi_tips, order_id: str, expected_need_hold_tips: bool,
):
    response = await taxi_tips.post(HANDLE_URL, params={'order_id': order_id})
    assert response.status_code == 200
    need_hold_tips = response.json()['need_hold_tips']
    assert need_hold_tips == expected_need_hold_tips
