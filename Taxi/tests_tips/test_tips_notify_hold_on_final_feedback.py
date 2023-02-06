import pytest


def _mark_exp3(is_enabled: bool, should_notify: bool):
    return [
        pytest.mark.experiments3(
            match={'predicate': {'type': 'true'}, 'enabled': is_enabled},
            name='hold_tips_on_final_feedback',
            consumers=['tips'],
            default_value={
                'time_before_take_tips': 3600,
                'should_notify_user': should_notify,
            },
        ),
    ]


MARK_EXP_ENABLED = _mark_exp3(is_enabled=True, should_notify=True)
MARK_EXP_DISABLED = _mark_exp3(is_enabled=False, should_notify=True)
MARK_EXP_NOTIFY_DISABLED = _mark_exp3(is_enabled=True, should_notify=False)


@pytest.mark.parametrize(
    ['order_id', 'expected_stq_called'],
    [
        pytest.param('order_1', True, marks=MARK_EXP_ENABLED, id='happy_path'),
        pytest.param(
            'order_2', True, marks=MARK_EXP_ENABLED, id='default_locale',
        ),
        pytest.param(
            'order_3', False, marks=MARK_EXP_ENABLED, id='order_not_found',
        ),
        pytest.param(
            'order_1', False, marks=MARK_EXP_DISABLED, id='disabled_by_exp',
        ),
        pytest.param(
            'order_1',
            False,
            marks=MARK_EXP_NOTIFY_DISABLED,
            id='disabled_by_exp_value',
        ),
        pytest.param('order_1', False, id='no_exp'),
    ],
)
async def test_send_notification(
        stq, stq_runner, order_id: str, expected_stq_called: bool,
):
    await stq_runner.tips_notify_hold_on_final_feedback.call(
        task_id=order_id, args=[order_id],
    )
    stq_queue = stq['order_notify_tips_hold_on_final_feedback']
    if expected_stq_called:
        assert stq_queue.times_called == 1
        call = stq_queue.next_call()
        assert call['kwargs']['order_id'] == order_id
        assert call['kwargs']['user_id'] == 'user_1'
        assert call['kwargs']['locale'] == 'ru'
    else:
        assert stq_queue.times_called == 0
