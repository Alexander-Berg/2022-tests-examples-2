import pytest

from tests_grocery_goals import common
from tests_grocery_goals import models


async def _make_action_request(taxi_grocery_goals, action):
    return await taxi_grocery_goals.post(
        '/lavka/v1/goals/v1/action',
        json={'goal_id': common.GOAL_ID, 'action': action},
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
            'X-YaTaxi-User': common.USER_INFO,
        },
    )


@pytest.mark.parametrize('action', ['new_seen', 'completed_seen'])
async def test_goal_not_exists(taxi_grocery_goals, action, coupons):
    response = await _make_action_request(taxi_grocery_goals, action)

    assert response.status_code == 404
    assert coupons.series_info_times_called == 0


@pytest.mark.parametrize('action', ['new_seen', 'completed_seen'])
@pytest.mark.now('2020-01-20T18:00:00+00:00')
async def test_goal_not_started(taxi_grocery_goals, pgsql, action, coupons):
    models.insert_goal(pgsql)
    response = await _make_action_request(taxi_grocery_goals, action)

    assert response.status_code == 404
    assert coupons.series_info_times_called == 0


@pytest.mark.now('2020-03-30T18:00:00+00:00')
async def test_goal_expired(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)
    response = await _make_action_request(taxi_grocery_goals, 'new_seen')

    assert response.status_code == 404
    assert coupons.series_info_times_called == 0


@common.GROCERY_GOALS_TRANSLATIONS
@pytest.mark.now('2021-10-24T10:00:00+00:00')
async def test_new_seen(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)

    coupons.check_series_info_request(
        series_id=common.GOAL_REWARD_PROMOCODE['extra']['promocode_series'],
    )

    expected_response = {
        'goal_id': common.GOAL_ID,
        'type': common.ORDERS_COUNT_GOAL_TYPE,
        'title': common.TITLE_TEXT,
        'status': 'in_progress',
        'icon_link': common.GOAL_ICON_LINK,
        'page_icon_link': common.GOAL_PAGE_ICON_LINK,
        'legal_text': common.LEGAL_TEXT_TRANSLATED,
        'remaining_time_text': '1 дня',
        'progress': {
            'progress_text': common.PROGRESS_TEXT_NOT_STARTED,
            'completed_progress_text': common.COMPLETED_PROGRESS_TEXT,
            'max_counter': str(
                common.GOAL_ORDER_COUNT_ARGS[common.ORDER_COUNT_ARG_TYPE],
            ),
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
    }

    response = await _make_action_request(taxi_grocery_goals, 'new_seen')
    assert response.status_code == 200
    assert response.json() == expected_response

    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )
    assert progress.new_seen

    assert coupons.series_info_times_called == 1
    # test idempotency
    response = await _make_action_request(taxi_grocery_goals, 'new_seen')
    assert response.status_code == 200
    assert response.json() == expected_response

    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )
    assert progress.new_seen


@common.GROCERY_GOALS_TRANSLATIONS
@pytest.mark.now('2021-10-25T11:00:00+00:00')
async def test_completed_seen(taxi_grocery_goals, pgsql, coupons):
    promocode = 'goal_promocode'
    models.insert_goal(pgsql)
    models.insert_goal_progress(
        pgsql, progress_status='completed', reward={'promocode': promocode},
    )

    coupons.check_series_info_request(
        series_id=common.GOAL_REWARD_PROMOCODE['extra']['promocode_series'],
    )

    expected_response = {
        'goal_id': common.GOAL_ID,
        'type': common.ORDERS_COUNT_GOAL_TYPE,
        'title': common.TITLE_TEXT,
        'status': 'completed',
        'icon_link': common.GOAL_ICON_LINK,
        'page_icon_link': common.GOAL_PAGE_ICON_LINK,
        'legal_text': common.LEGAL_TEXT_TRANSLATED,
        'progress': {
            'progress_text': common.PROGRESS_TEXT,
            'completed_progress_text': common.COMPLETED_PROGRESS_TEXT,
            'max_counter': str(
                common.GOAL_ORDER_COUNT_ARGS[common.ORDER_COUNT_ARG_TYPE],
            ),
            'current_counter': '1',
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
                'promocode': promocode,
            },
        },
        'expires': common.GOAL_EXPIRES,
    }

    response = await _make_action_request(taxi_grocery_goals, 'completed_seen')
    assert response.status_code == 200
    assert response.json() == expected_response

    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )
    assert progress.completed_seen

    assert coupons.series_info_times_called == 1
    # test idempotency
    response = await _make_action_request(taxi_grocery_goals, 'completed_seen')
    assert response.status_code == 200
    assert response.json() == expected_response

    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )
    assert progress.completed_seen


@common.GROCERY_GOALS_TRANSLATIONS
@pytest.mark.parametrize('action', ['new_seen', 'completed_seen'])
@pytest.mark.now('2020-02-26T18:00:00+00:00')
async def test_time_zone(taxi_grocery_goals, pgsql, action):
    models.insert_goal(pgsql, starts='2020-02-26T20:00:00+03:00')
    if action == 'completed_seen':
        models.insert_goal_progress(pgsql, progress_status='completed')

    response = await _make_action_request(taxi_grocery_goals, action)
    assert response.status_code == 200


@common.GROCERY_GOALS_TRANSLATIONS
@pytest.mark.now('2020-02-26T18:00:00+00:00')
async def test_not_completed(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)
    models.insert_goal_progress(pgsql, progress_status='in_progress')

    response = await _make_action_request(taxi_grocery_goals, 'completed_seen')
    assert response.status_code == 404
    assert coupons.series_info_times_called == 0


@common.GROCERY_GOALS_TRANSLATIONS
@pytest.mark.now('2021-10-24T10:00:00+00:00')
@pytest.mark.parametrize(
    'goal_type, goal_args',
    [
        ('orders_count', common.GOAL_ORDER_COUNT_ARGS),
        ('orders_total_sum', common.GOAL_TOTAL_SUM_ARGS),
        ('skus_count', common.GOAL_SKUS_COUNT_ARGS),
        ('skus_total_sum', common.GOAL_SKUS_TOTAL_SUM_ARGS),
    ],
)
async def test_default_progress(
        taxi_grocery_goals, pgsql, coupons, goal_type, goal_args,
):
    models.insert_goal(pgsql, goal_type=goal_type, goal_args=goal_args)

    coupons.check_series_info_request(
        series_id=common.GOAL_REWARD_PROMOCODE['extra']['promocode_series'],
    )

    response = await _make_action_request(taxi_grocery_goals, 'new_seen')
    assert response.status_code == 200

    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )
    assert progress.new_seen

    assert coupons.series_info_times_called == 1
