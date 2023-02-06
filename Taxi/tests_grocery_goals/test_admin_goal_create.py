import copy

import pytest

from tests_grocery_goals import common
from tests_grocery_goals import models

ALL_GOAL_TYPES = pytest.mark.parametrize(
    'goal_type, goal_args',
    [
        ('orders_count', common.GOAL_ORDER_COUNT_ARGS),
        ('orders_total_sum', common.GOAL_TOTAL_SUM_ARGS),
        ('skus_count', common.GOAL_SKUS_COUNT_ARGS),
        ('skus_total_sum', common.GOAL_SKUS_TOTAL_SUM_ARGS),
    ],
)

ALL_REWARD_TYPES = pytest.mark.parametrize(
    'goal_reward',
    [
        common.GOAL_REWARD_PROMOCODE,
        common.GOAL_REWARD_SKU,
        common.GOAL_REWARD_EXTERNAL_VENDOR,
    ],
)


def _get_request_body(
        goal_name=common.GOAL_NAME,
        starts=common.GOAL_STARTS,
        expires=common.GOAL_EXPIRES,
        goal_type=common.ORDERS_COUNT_GOAL_TYPE,
        goal_args=copy.deepcopy(common.GOAL_ORDER_COUNT_ARGS),
        goal_reward=copy.deepcopy(common.GOAL_REWARD_PROMOCODE),
        goal_alt_reward=None,
):
    alt_reward = (
        {} if goal_alt_reward is None else {'goal_alt_reward': goal_alt_reward}
    )

    return {
        'goal_name': goal_name,
        'display_info': common.GOAL_DISPLAY_INFO,
        'starts': starts,
        'expires': expires,
        'goal_type': goal_type,
        'goal_args': goal_args,
        'goal_reward': goal_reward,
        'marketing_tags': common.GOAL_MARKETING_TAGS,
        **alt_reward,
    }


@ALL_GOAL_TYPES
@ALL_REWARD_TYPES
@pytest.mark.now('2019-01-01T11:30:00+0000')
async def test_basic(
        taxi_grocery_goals, goal_type, goal_args, goal_reward, pgsql,
):
    alt_reward_promocode = models.GoalRewardPromocode()

    response = await taxi_grocery_goals.post(
        'admin/v1/goals/v1/create',
        json=_get_request_body(
            goal_type=goal_type,
            goal_args=goal_args,
            goal_reward=goal_reward,
            goal_alt_reward=[alt_reward_promocode.get_reward_db_info()],
        ),
    )

    assert response.status_code == 200

    goal = models.get_goal_by_id(pgsql, response.json()['goal_id'])

    assert goal.name == common.GOAL_NAME
    assert goal.title == common.GOAL_TITLE
    assert goal.icon_link == common.GOAL_ICON_LINK
    assert goal.goal_page_icon_link == common.GOAL_PAGE_ICON_LINK
    assert goal.legal_text == common.GOAL_LEGAL_TEXT
    assert goal.goal_type == goal_type
    assert goal.goal_args == goal_args
    assert goal.goal_reward == goal_reward
    assert goal.progress_bar_color == common.PROGRESS_BAR_COLOR
    assert goal.catalog_text == common.CATALOG_TEXT
    assert goal.group_text == common.GROUP_TEXT
    assert goal.catalog_link == common.CATALOG_LINK
    assert goal.catalog_picture_link == common.CATALOG_PICTURE_LINK
    assert goal.marketing_tags == common.GOAL_MARKETING_TAGS
    assert (
        goal.finish_push_title
        == common.GOAL_PUSH_INFO['finish_title_tanker_key']
    )
    assert (
        goal.finish_push_message
        == common.GOAL_PUSH_INFO['finish_message_tanker_key']
    )
    assert goal.goal_alt_reward == [alt_reward_promocode.get_reward_db_info()]


@ALL_GOAL_TYPES
@ALL_REWARD_TYPES
@pytest.mark.now('2019-01-01T11:30:00+0000')
async def test_already_exists(
        taxi_grocery_goals, goal_type, goal_reward, goal_args,
):
    starts = '2020-01-27T16:00:00+00:00'
    different_starts = '2020-01-28T16:00:00+00:00'

    response = await taxi_grocery_goals.post(
        'admin/v1/goals/v1/create',
        json=_get_request_body(
            goal_type=goal_type,
            goal_args=goal_args,
            starts=starts,
            goal_reward=goal_reward,
        ),
    )

    assert response.status_code == 200

    response = await taxi_grocery_goals.post(
        'admin/v1/goals/v1/create',
        json=_get_request_body(
            goal_type=goal_type,
            goal_args=goal_args,
            goal_reward=goal_reward,
            starts=starts,
        ),
    )

    assert response.status_code == 200

    response = await taxi_grocery_goals.post(
        'admin/v1/goals/v1/create',
        json=_get_request_body(
            goal_type=goal_type,
            goal_args=goal_args,
            goal_reward=goal_reward,
            starts=different_starts,
        ),
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    'goal_type, goal_args',
    [
        ('orders_count', {common.TOTAL_SUM_ARG_TYPE: '1000'}),
        ('orders_total_sum', {common.ORDER_COUNT_ARG_TYPE: 10}),
    ],
)
@pytest.mark.now('2019-01-01T11:30:00+0000')
async def test_types_not_match(taxi_grocery_goals, goal_type, goal_args):
    response = await taxi_grocery_goals.post(
        'admin/v1/goals/v1/create',
        json=_get_request_body(goal_type=goal_type, goal_args=goal_args),
    )

    assert response.status_code == 400


@pytest.mark.now('2019-01-01T11:30:00+0000')
async def test_starts_less_than_now(taxi_grocery_goals):
    response = await taxi_grocery_goals.post(
        'admin/v1/goals/v1/create',
        json=_get_request_body(starts='2010-01-01T11:30:00+0000'),
    )

    assert response.status_code == 400


@pytest.mark.now('2019-01-01T11:30:00+0000')
async def test_expires_before_starts(taxi_grocery_goals):
    response = await taxi_grocery_goals.post(
        'admin/v1/goals/v1/create',
        json=_get_request_body(
            starts='2021-01-01T11:30:00+0000',
            expires='2020-01-01T11:30:00+0000',
        ),
    )

    assert response.status_code == 400


@pytest.mark.now('2019-01-01T11:30:00+0000')
async def test_coupons_error(taxi_grocery_goals, coupons):
    coupons.set_series_info_response(status_code=404)
    response = await taxi_grocery_goals.post(
        'admin/v1/goals/v1/create', json=_get_request_body(),
    )

    assert response.status_code == 400
