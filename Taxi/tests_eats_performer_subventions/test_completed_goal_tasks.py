from concurrent.futures.process import _threads_wakeups
import pytest

ADJ_REASON_ID = 198


def get_create_adjustment_response(
        external_payment_id,
        courier_id,
        amount,
        comment,
        date,
        reason_id=ADJ_REASON_ID,
):
    return {
        'isSuccess': True,
        'adjustment': {
            'id': external_payment_id,
            'courierId': courier_id,
            'reasonId': reason_id,
            'amount': amount,
            'comment': comment,
            'date': date,
        },
    }


@pytest.mark.config(EATS_PERFORMER_SUBVENTIONS_GOAL_COMPLETED_ENABLED=True)
@pytest.mark.pgsql(
    'eats_performer_subventions', files=['subvention_goals.sql'],
)
async def test_stq_completed_goal_dxgy(
        stq_runner, db_select_goals, mockserver,
):
    @mockserver.json_handler(
        '/eats-core-courier-salary/server/api/v1/courier-salary/adjustments',
    )
    def _mock_handler(request):
        return get_create_adjustment_response(
            20, 1, 9217, 'Personal goal', '2022-02-05',
        )

    await stq_runner.eats_performer_subventions_goal_completed.call(
        task_id='unique',
        kwargs={
            'unique_driver_id': 'unique-1',
            'goal_interval': {
                'start': '2022-02-01T00:00:00+03:00',
                'end': '2022-02-07T23:59:59+03:00',
            },
            'money_to_pay': {'amount': '9217', 'currency': 'rub'},
            'orders_count': 34,
        },
    )

    goals = db_select_goals()
    assert len(goals) == 2

    goal = goals[0]
    assert goal['unique_driver_id'] == 'unique-1'
    assert goal['total_money_to_pay'] == 9217
    assert goal['is_paid'] == True
    assert goal['status'] == 'finished'


@pytest.mark.config(EATS_PERFORMER_SUBVENTIONS_GOAL_COMPLETED_ENABLED=True)
@pytest.mark.pgsql(
    'eats_performer_subventions', files=['subvention_goals.sql'],
)
async def test_stq_daily_goal_complete(
        stq_runner, db_select_goals, mockserver,
):
    @mockserver.json_handler(
        '/eats-core-courier-salary/server/api/v1/courier-salary/adjustments',
    )
    def _mock_handler(request):
        return get_create_adjustment_response(
            20, 2, 1000, 'Personal goal', '2022-02-07',
        )

    await stq_runner.eats_performer_subventions_goal_completed.call(
        task_id='unique',
        kwargs={
            'unique_driver_id': 'unique-2',
            'goal_interval': {
                'start': '2022-02-02T00:00:00+03:00',
                'end': '2022-02-07T23:59:59+03:00',
            },
            'money_to_pay': {'amount': '1000', 'currency': 'rub'},
            'orders_count': 10,
            'completed_interval': {
                'start': '2022-02-07T00:00:00+03:00',
                'end': '2022-02-07T23:59:59+03:00',
            },
        },
    )

    goals = db_select_goals()
    assert len(goals) == 2

    goal = goals[1]
    assert goal['unique_driver_id'] == 'unique-2'
    assert goal['total_money_to_pay'] == 1000
    assert goal['is_paid'] == True
    assert goal['status'] == 'finished'
    assert len(goal['days_finished']) == 6
    assert goal['days_finished'][5] == True


@pytest.mark.config(EATS_PERFORMER_SUBVENTIONS_GOAL_COMPLETED_ENABLED=True)
@pytest.mark.pgsql(
    'eats_performer_subventions', files=['subvention_goals.sql'],
)
async def test_stq_daily_goal_progress(
        stq_runner, db_select_goals, mockserver,
):
    await stq_runner.eats_performer_subventions_goal_completed.call(
        task_id='unique',
        kwargs={
            'unique_driver_id': 'unique-2',
            'goal_interval': {
                'start': '2022-02-02T00:00:00+03:00',
                'end': '2022-02-07T23:59:59+03:00',
            },
            'money_to_pay': {'amount': '1000', 'currency': 'rub'},
            'orders_count': 10,
            'completed_interval': {
                'start': '2022-02-06T00:00:00+03:00',
                'end': '2022-02-06T23:59:59+03:00',
            },
        },
    )

    goals = db_select_goals()
    assert len(goals) == 2

    goal = goals[1]
    assert goal['unique_driver_id'] == 'unique-2'
    assert goal['total_money_to_pay'] == 1000
    assert goal['is_paid'] == False
    assert goal['status'] == 'in_progress'
    assert len(goal['days_finished']) == 6
    assert goal['days_finished'][4] == True
