import pytest

from infra_events.common import db
# pylint: disable=redefined-outer-name
from infra_events.generated.cron import cron_context as context
from infra_events.generated.cron import run_cron

INFRA_EVENTS_RELEASE_SCHEDULES = {
    'default': {
        'Fri': {'finish': ['20:00'], 'start': ['12:00']},
        'Mon': {'finish': ['20:00'], 'start': ['12:00']},
        'Thu': {'finish': ['20:00'], 'start': ['12:00']},
        'Tue': {'finish': ['20:00'], 'start': ['12:00']},
        'Wed': {'finish': ['20:00'], 'start': ['12:00']},
    },
    'larks': {
        'Fri': {'finish': ['12:00'], 'start': ['04:00']},
        'Mon': {'finish': ['12:00'], 'start': ['04:00']},
        'Thu': {'finish': ['12:00'], 'start': ['04:00']},
        'Tue': {'finish': ['12:00'], 'start': ['04:00']},
        'Wed': {'finish': ['12:00'], 'start': ['04:00']},
    },
    'owls': {
        'Fri': {'finish': ['04:00'], 'start': ['20:00']},
        'Mon': {'finish': ['04:00'], 'start': ['20:00']},
        'Thu': {'finish': ['04:00'], 'start': ['20:00']},
        'Tue': {'finish': ['04:00'], 'start': ['20:00']},
        'Wed': {'finish': ['04:00'], 'start': ['20:00']},
    },
    'no_work_at_monday_lunch': {
        'Fri': {'finish': ['20:00'], 'start': ['12:00']},
        'Mon': {'finish': ['12:00', '20:00'], 'start': ['11:00', '13:00']},
        'Thu': {'finish': ['20:00'], 'start': ['12:00']},
        'Tue': {'finish': ['20:00'], 'start': ['12:00']},
        'Wed': {'finish': ['20:00'], 'start': ['12:00']},
    },
    'eternal_holidays': {'Mon': {'finish': ['12:34']}},
}
INFRA_EVENTS_VIEWS = {
    'new_view': {'release_schedule': 'default'},
    'switched_on_view': {'release_schedule': 'default'},
    'switched_off_view': {'release_schedule': 'larks'},
    'remain_off_view': {'release_schedule': 'owls'},
    'blocked_view': {'release_schedule': 'default'},
    'monday_lunch_view': {'release_schedule': 'no_work_at_monday_lunch'},
    'on_holidays_view': {'release_schedule': 'eternal_holidays'},
}


@pytest.mark.config(INFRA_EVENTS_FEATURES={'switch_rollout_modes': False})
async def test_disabled_feature(mongo):
    await run_cron.main(
        ['infra_events.crontasks.switch_rollout_modes', '-t', '0'],
    )

    test_context = context.create_context()

    cur_state = await db.get_rollout_mode(test_context, 'switched_on_view')
    assert cur_state['can_deploy'] is False


@pytest.mark.config(
    INFRA_EVENTS_FEATURES={'switch_rollout_modes': True},
    INFRA_EVENTS_RELEASE_SCHEDULES=INFRA_EVENTS_RELEASE_SCHEDULES,
    INFRA_EVENTS_VIEWS=INFRA_EVENTS_VIEWS,
)
@pytest.mark.now('2020-12-28T12:01:00+0300')  # Monday
async def test_switch_rollout_modes(mongo, cron_context):
    await run_cron.main(
        ['infra_events.crontasks.switch_rollout_modes', '-t', '0'],
    )

    view_to_can_deploy_map = {
        'new_view': True,
        'switched_on_view': True,
        'switched_off_view': False,
        'remain_off_view': False,
        'blocked_view': False,
        'monday_lunch_view': False,
        'on_holidays_view': False,
    }

    for view, can_deploy in view_to_can_deploy_map.items():
        cur_state = await db.get_rollout_mode(cron_context, view)
        assert (
            cur_state['can_deploy'] is can_deploy
        ), 'view "{}" not {}'.format(view, can_deploy)
