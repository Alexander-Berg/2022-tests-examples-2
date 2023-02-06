import pytest

from personal_goals.modules import missing_kit


@pytest.mark.parametrize(
    'notifications_ids, remaining_notifications',
    [
        ([], 4),
        (
            [
                'b7fc20328ae043fb830d4c3453331906',
                '8072aa213e914b00b066b5f9f83f663d',
            ],
            2,
        ),
    ],
)
@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_missed_notifications(
        web_context, notifications_ids, remaining_notifications, pg_goals,
):
    # pylint: disable=W0212
    await missing_kit.notifications._handle_missed_notifications(
        web_context, notifications_ids,
    )

    notifications = await pg_goals.notifications.all()
    assert len(notifications) == remaining_notifications


@pytest.mark.parametrize(
    'goal_id, expected_status',
    [
        ('user_goal_id_1', 'missed'),
        ('9921d89db101479ab1e476d8910d72fb', 'missed'),
        ('c69e65c601c04ffdaa6277c80cafe7f8', 'done'),
    ],
)
@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.pgsql('personal_goals', files=['basic_personal_goals.sql'])
async def test_missed_goals(web_context, goal_id, expected_status, pg_goals):
    # pylint: disable=W0212
    await missing_kit.goals._handle_missed_goals(web_context, [goal_id])

    user_goal = (await pg_goals.user_goals.by_ids([goal_id]))[0]
    assert user_goal['status'] == expected_status
    events = await pg_goals.goal_events.by_user_goal(goal_id)
    assert not events
