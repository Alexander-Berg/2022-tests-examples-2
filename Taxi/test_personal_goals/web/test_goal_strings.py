import pytest

from personal_goals import models as goals
from personal_goals.api.modules.goals_list.serialization import builders
from . import common


async def _get_personal_goal(pg_goals, goal_id: str, event_count=0):
    goal_d = dict((await pg_goals.goals.by_ids([goal_id]))[0])
    goal_d['goal_id'] = 'goal_id'
    goal_d['status'] = 'active'
    goal_d['yandex_uid'] = 'yandex_uid'
    if event_count:
        goal_d['event_count'] = event_count
    return goals.parse.parse_personal_goal(goal_d)


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.translations(
    tariff=common.TARIFF, client_messages=common.CLIENT_MESSAGES,
)
@pytest.mark.parametrize(
    'goal_id,result',
    [
        ('goal_id_1', '<b>Bonus:</b> 10% for ride in «Economy».'),
        ('goal_id_2', '<b>Bonus:</b> 400\u2006$SIGN$$CURRENCY$ for ride.'),
        (
            'goal_id_3',
            '<b>Bonus:</b> 400 $SIGN$$CURRENCY$ for ride in «Economy».',
        ),
        (
            'goal_id_4',
            '<b>Bonus:</b> 400 $SIGN$$CURRENCY$ for ride.'
            ' <red>Tariff is not supported in you zone.</red>',
        ),
        ('goal_id_5', '<b>Cashback:</b> 100 points.'),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['for_strings.sql'])
async def test_summary_bonus(
        web_context, goal_id, result, pg_goals, default_tariff_settings,
):
    locale = 'ru'
    goal = await _get_personal_goal(pg_goals, goal_id, web_context)

    context = builders.common.BuilderContext(
        locale,
        web_context.translations,
        web_context.config,
        default_tariff_settings,
    )
    builder = builders.common.GoalSummaryBuilder(goal, context)

    assert builder.build_bonus() == result


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.translations(
    tariff=common.TARIFF, client_messages=common.CLIENT_MESSAGES,
)
@pytest.mark.parametrize(
    'goal_id,result',
    [
        ('goal_id_1', '<b>How:</b> make 2 unt. 30 августа'),
        ('goal_id_2', '<b>How:</b> make 3 unt. 30 августа'),
        ('goal_id_4', '<b>How:</b> make 4 in «Economy» unt. 30 августа'),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['for_strings.sql'])
async def test_summary_condition(
        web_context, goal_id, result, pg_goals, default_tariff_settings,
):
    locale = 'ru'
    goal = await _get_personal_goal(pg_goals, goal_id, web_context)

    context = builders.common.BuilderContext(
        locale,
        web_context.translations,
        web_context.config,
        default_tariff_settings,
    )
    builder = builders.common.GoalSummaryBuilder(goal, context)

    assert builder.build_condition() == result


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.translations(
    tariff=common.TARIFF, client_messages=common.CLIENT_MESSAGES,
)
@pytest.mark.parametrize(
    'goal_id,result',
    [('goal_id_1', '<b>Details:</b> Pay by card.'), ('goal_id_2', None)],
)
@pytest.mark.pgsql('personal_goals', files=['for_strings.sql'])
async def test_summary_details(
        web_context, goal_id, result, pg_goals, default_tariff_settings,
):
    locale = 'ru'
    goal = await _get_personal_goal(pg_goals, goal_id, web_context)

    context = builders.common.BuilderContext(
        locale,
        web_context.translations,
        web_context.config,
        default_tariff_settings,
    )
    builder = builders.common.GoalSummaryBuilder(goal, context)

    assert builder.build_details() == result


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.translations(
    tariff=common.TARIFF, client_messages=common.CLIENT_MESSAGES,
)
@pytest.mark.parametrize(
    'goal_id,result',
    [
        ('goal_id_1', 'Glad to see'),
        ('goal_id_2', 'Glad to see'),
        ('goal_id_4', 'Glad to see'),
        ('goal_id_5', 'Glad to see'),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['for_strings.sql'])
async def test_notification_finish_description(
        web_context, goal_id, result, pg_goals, default_tariff_settings,
):
    locale = 'ru'
    goal = await _get_personal_goal(pg_goals, goal_id, web_context)
    notification = goals.models.PersonalGoalNotification(
        goal=goal, event='goal_finish', notification_id='some_id',
    )

    context = builders.notifications.NotificationBuilderContext(
        locale,
        web_context.translations,
        web_context.config,
        default_tariff_settings,
    )
    builder = builders.notifications.NotificationFinishBuilder(
        notification, context,
    )

    assert builder.build_description() == result


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.translations(
    tariff=common.TARIFF, client_messages=common.CLIENT_MESSAGES,
)
@pytest.mark.parametrize(
    'goal_id,result',
    [
        ('goal_id_1', 'You complete 2 rides'),
        ('goal_id_2', '1 ride unt. 30 августа - get 400 $SIGN$$CURRENCY$'),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['for_strings.sql'])
async def test_notification_progress_title(
        web_context, goal_id, result, pg_goals, default_tariff_settings,
):
    locale = 'ru'
    goal = await _get_personal_goal(pg_goals, goal_id, 2)
    notification = goals.models.PersonalGoalNotification(
        goal=goal, event='goal_progress', notification_id='some_id',
    )

    context = builders.notifications.NotificationBuilderContext(
        locale,
        web_context.translations,
        web_context.config,
        default_tariff_settings,
    )
    builder = builders.notifications.NotificationProgressBuilder(
        notification, context,
    )

    assert builder.build_title() == result


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.translations(
    tariff=common.TARIFF, client_messages=common.CLIENT_MESSAGES,
)
@pytest.mark.parametrize(
    'goal_id,title,detail,events',
    [
        ('goal_id_1', '1 rides until bonus', 'You have 1 from 2 orders', 1),
        ('goal_id_3', '4 rides until bonus', None, 0),
        ('goal_id_5', '2 rides until cashback', None, 0),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['for_strings.sql'])
async def test_goal_strings_progress(
        web_context,
        goal_id,
        title,
        detail,
        events,
        pg_goals,
        default_tariff_settings,
):
    locale = 'ru'

    goal = await _get_personal_goal(pg_goals, goal_id, event_count=events)
    context = builders.goals.GoalBuilderContext(
        locale=locale,
        translations=web_context.translations,
        config=web_context.config,
        tariff_settings=default_tariff_settings,
    )
    builder = builders.goals.GoalBuilder(goal, context)
    result = builder.build_progress()

    assert result.title == title
    assert result.detail == detail


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.translations(
    tariff=common.TARIFF, client_messages=common.CLIENT_MESSAGES,
)
@pytest.mark.parametrize(
    'goal_id,description',
    [
        ('goal_id_1', 'Discount limit is 10%'),
        ('goal_id_3', 'Discount limit is 400\u2006$SIGN$$CURRENCY$'),
        ('goal_id_5', 'Cashback bonus is 100 points'),
    ],
)
@pytest.mark.pgsql('personal_goals', files=['for_strings.sql'])
async def test_goal_strings_description(
        web_context, goal_id, description, pg_goals, default_tariff_settings,
):
    locale = 'ru'

    goal = await _get_personal_goal(pg_goals, goal_id)
    context = builders.goals.GoalBuilderContext(
        locale=locale,
        translations=web_context.translations,
        config=web_context.config,
        tariff_settings=default_tariff_settings,
    )
    builder = builders.goals.GoalBuilder(goal, context)
    result = builder.build_description()

    assert result == description


@pytest.mark.now('2019-07-26T00:00:00+0')
@pytest.mark.translations(
    tariff=common.TARIFF, client_messages=common.CLIENT_MESSAGES,
)
@pytest.mark.parametrize(
    'event_count, title',
    [(1, 'Discount 10% in 1 rides'), (2, 'You complete 2 rides')],
)
@pytest.mark.pgsql('personal_goals', files=['for_strings.sql'])
async def test_goal_string_title(
        web_context, pg_goals, default_tariff_settings, title, event_count,
):
    locale = 'ru'

    goal = await _get_personal_goal(
        pg_goals, 'goal_id_1', event_count=event_count,
    )
    context = builders.goals.GoalBuilderContext(
        locale=locale,
        translations=web_context.translations,
        config=web_context.config,
        tariff_settings=default_tariff_settings,
    )
    builder = builders.goals.GoalBuilder(goal, context)
    result = builder.build_title()

    assert result == title
