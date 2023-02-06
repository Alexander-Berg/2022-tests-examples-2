import pytest

from tests_grocery_goals import common
from tests_grocery_goals import models


@pytest.fixture(autouse=True)
def add_tags(grocery_tags):
    grocery_tags.add_tag(
        personal_phone_id=common.PERSONAL_PHONE_ID,
        tag=common.GOAL_MARKETING_TAGS[0],
    )


async def _make_get_info_request(taxi_grocery_goals, goal_id=common.GOAL_ID):
    return await taxi_grocery_goals.post(
        '/lavka/v1/goals/v1/get-info',
        json={'goal_id': goal_id},
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
            'X-YaTaxi-User': common.USER_INFO,
        },
    )


@common.GROCERY_GOALS_TRANSLATIONS
@pytest.mark.now('2021-10-24T12:00:00+00:00')
async def test_new_goal(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)

    response = await _make_get_info_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json() == {
        'goal_info': {
            'goal_id': common.GOAL_ID,
            'type': common.ORDERS_COUNT_GOAL_TYPE,
            'title': common.TITLE_TEXT,
            'status': 'new',
            'icon_link': common.GOAL_ICON_LINK,
            'page_icon_link': common.GOAL_PAGE_ICON_LINK,
            'legal_text': common.LEGAL_TEXT_TRANSLATED,
            'remaining_time_text': '1 дня',
            'progress': {
                'progress_text': common.PROGRESS_TEXT_NOT_STARTED,
                'max_counter': str(
                    common.GOAL_ORDER_COUNT_ARGS[common.ORDER_COUNT_ARG_TYPE],
                ),
                'completed_progress_text': common.COMPLETED_PROGRESS_TEXT,
                'current_counter': '0',
                'progress_type': 'discrete',
                'progress_bar_color': common.PROGRESS_BAR_COLOR,
            },
            'reward_info': {
                'type': 'promocode',
                'extra': {
                    'value_text': '-$SIGN$500$CURRENCY$',
                    'promocode_type': 'fixed',
                    'currency_sign': '₽',
                    'orders_count_text': '2',
                    'orders_count': 2,
                },
            },
            'expires': common.GOAL_EXPIRES,
        },
    }


@pytest.mark.now('2020-01-20T18:00:00+00:00')
async def test_not_started(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)

    response = await _make_get_info_request(taxi_grocery_goals)

    assert response.status_code == 404


@pytest.mark.now('2021-10-25T15:00:00+00:00')
async def test_expired(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)

    response = await _make_get_info_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json()['goal_info']['status'] == 'expired'
    assert 'remaining_time_text' not in response.json()


@common.GROCERY_GOALS_TRANSLATIONS
@pytest.mark.now('2021-10-24T12:00:00+0000')
async def test_in_progress(taxi_grocery_goals, pgsql, coupons):
    order_count = 3
    models.insert_goal(pgsql)
    models.insert_goal_progress(
        pgsql,
        new_seen=True,
        progress={common.ORDER_COUNT_ARG_TYPE: order_count},
    )

    response = await _make_get_info_request(taxi_grocery_goals)

    assert response.status_code == 200
    goal = response.json()['goal_info']
    assert goal['status'] == 'in_progress'
    assert goal['progress']['current_counter'] == str(order_count)


async def test_completed(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)
    models.insert_goal_progress(pgsql, progress_status='completed')

    response = await _make_get_info_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json()['goal_info']['status'] == 'completed_not_seen'
    assert 'remaining_time_text' not in response.json()


async def test_completed_seen(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)
    models.insert_goal_progress(
        pgsql, progress_status='completed', completed_seen=True,
    )

    response = await _make_get_info_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json()['goal_info']['status'] == 'completed'
    assert 'remaining_time_text' not in response.json()


async def test_tag_filter(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql, marketing_tags=['another_tag'])

    response = await _make_get_info_request(taxi_grocery_goals)

    assert response.status_code == 404
