import datetime

import pytest

from tests_grocery_goals import common
from tests_grocery_goals import helpers
from tests_grocery_goals import models

EATS_USER_ID = 'eats-user-id'
PERSONAL_PHONE_ID = 'personal-phone-id'
USER_INFO = (
    f'eats_user_id={EATS_USER_ID}, personal_phone_id={PERSONAL_PHONE_ID}'
)

USER_LOCATION = {'lat': 50, 'lon': 30}


@pytest.fixture(autouse=True)
def add_tags(grocery_tags):
    grocery_tags.add_tag(
        personal_phone_id=PERSONAL_PHONE_ID, tag=common.GOAL_MARKETING_TAGS[0],
    )


async def _make_list_request(taxi_grocery_goals, statuses=None, location=None):
    return await taxi_grocery_goals.post(
        '/lavka/v1/goals/v1/list',
        json={'statuses': statuses, 'location': location},
        headers={
            'X-Yandex-UID': common.YANDEX_UID,
            'X-YaTaxi-Session': 'taxi:1234',
            'X-YaTaxi-User': USER_INFO,
        },
    )


GROCERY_GOALS_LIST_RETRIEVE_POLICY = pytest.mark.experiments3(
    name='grocery_goals_list_retrieve_policy',
    consumers=['grocery-goals/list'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'is_signal': False,
            'title': 'Always enabled',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {
                'not_list_expired_after_min': 60,
                'not_list_complete_reward_used_after_min': 240,
                'not_list_complete_reward_not_used_after_min': 480,
            },
        },
    ],
    is_config=True,
)


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-24T12:00:00+0000')
async def test_new_goal(taxi_grocery_goals, pgsql):
    models.insert_goal(pgsql)

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    response_goal = response.json()['goals'][0]
    assert response_goal['goal_id'] == common.GOAL_ID
    assert response_goal['type'] == common.ORDERS_COUNT_GOAL_TYPE
    assert response_goal['status'] == 'new'
    assert response_goal['icon_link'] == common.GOAL_ICON_LINK
    assert response_goal['page_icon_link'] == common.GOAL_PAGE_ICON_LINK
    assert response_goal['remaining_time_text'] == '1 дня'
    assert response_goal['expires'] == common.GOAL_EXPIRES


@pytest.mark.now('2021-8-25T11:00:00+0000')
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
async def test_not_started(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    goals = response.json()['goals']
    assert not goals

    assert coupons.series_info_times_called == 0


@pytest.mark.now('2021-10-25T12:30:00+00:00')
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
async def test_expired(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    goal = response.json()['goals'][0]
    assert goal['status'] == 'expired'
    assert 'remaining_time_text' not in goal

    assert coupons.series_info_times_called == 1


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T10:00:00+00:00')
async def test_in_progress(taxi_grocery_goals, pgsql, coupons):
    order_count = 3
    models.insert_goal(pgsql)
    models.insert_goal_progress(
        pgsql,
        new_seen=True,
        progress={common.ORDER_COUNT_ARG_TYPE: order_count},
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    goal = response.json()['goals'][0]
    assert goal['status'] == 'in_progress'
    assert goal['progress']['current_counter'] == str(order_count)

    assert coupons.series_info_times_called == 1


@GROCERY_GOALS_LIST_RETRIEVE_POLICY
async def test_completed(taxi_grocery_goals, pgsql, coupons):
    promocode = 'goal_promocode'

    models.insert_goal(pgsql)
    models.insert_goal_progress(
        pgsql, progress_status='completed', reward={'promocode': promocode},
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    goal = response.json()['goals'][0]
    assert goal['status'] == 'completed_not_seen'
    assert 'remaining_time_text' not in goal
    assert goal['reward_info']['extra']['promocode'] == promocode
    assert 'alt_reward_info' not in goal

    assert coupons.series_info_times_called == 1


@GROCERY_GOALS_LIST_RETRIEVE_POLICY
async def test_completed_seen(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)
    models.insert_goal_progress(
        pgsql, progress_status='completed', completed_seen=True,
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    goal = response.json()['goals'][0]
    assert goal['status'] == 'completed'
    assert 'remaining_time_text' not in goal

    assert coupons.series_info_times_called == 1


@GROCERY_GOALS_LIST_RETRIEVE_POLICY
async def test_tag_filter(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql, marketing_tags=['another_tag'])

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json() == {'goals': []}

    assert coupons.series_info_times_called == 0


@pytest.mark.now('2021-10-25T10:00:00+00:00')
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
async def test_status_filter(taxi_grocery_goals, pgsql, coupons):
    goal_id = '222'
    models.insert_goal(pgsql)
    models.insert_goal_progress(
        pgsql, progress_status='completed', completed_seen=True,
    )

    models.insert_goal(pgsql, goal_id=goal_id, name='other_goal')
    models.insert_goal_progress(
        pgsql,
        goal_id=goal_id,
        progress_status='in_progress',
        completed_seen=True,
    )

    response = await _make_list_request(taxi_grocery_goals, statuses=['new'])

    assert response.status_code == 200
    goals = response.json()['goals']
    assert len(goals) == 1
    assert goals[0]['goal_id'] == goal_id

    assert coupons.series_info_times_called == 2


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T10:00:00+00:00')
@pytest.mark.parametrize(
    'goal_args, currency_sign',
    [
        (common.GOAL_TOTAL_SUM_ARGS, '₽'),
        (common.GOAL_ORDER_COUNT_ARGS, None),
        (common.GOAL_SKUS_COUNT_ARGS, None),
        (common.GOAL_SKUS_TOTAL_SUM_ARGS, '₽'),
    ],
)
async def test_currency_sign(
        taxi_grocery_goals, pgsql, goal_args, currency_sign, coupons,
):
    models.insert_goal(pgsql, goal_args=goal_args)

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    goal = response.json()['goals'][0]
    if currency_sign is not None:
        assert goal['currency_sign'] == currency_sign
    else:
        assert 'currency_sign' not in goal


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T10:00:00+00:00')
@pytest.mark.parametrize(
    'goal_type, goal_args',
    [
        ('orders_count', common.GOAL_ORDER_COUNT_ARGS),
        ('orders_total_sum', common.GOAL_TOTAL_SUM_ARGS),
        ('skus_count', common.GOAL_SKUS_COUNT_ARGS),
        ('skus_total_sum', common.GOAL_SKUS_TOTAL_SUM_ARGS),
    ],
)
async def test_title(taxi_grocery_goals, pgsql, goal_type, goal_args):
    models.insert_goal(pgsql, goal_type=goal_type, goal_args=goal_args)

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json()['goals'][0]['title'] == common.TITLE_TRANSLATED % (
        {common.TITLE_ARG: common.get_typed_args_value(goal_args)}
    )


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T10:00:00+00:00')
@pytest.mark.parametrize(
    'goal_type, goal_args, progress, completed_progress_text, progress_type',
    [
        (
            'orders_count',
            common.GOAL_ORDER_COUNT_ARGS,
            {common.ORDER_COUNT_ARG_TYPE: 5},
            common.ORDERS_COUNT_COMPLETED_TRANSLATED,
            'discrete',
        ),
        (
            'orders_total_sum',
            common.GOAL_TOTAL_SUM_ARGS,
            {common.TOTAL_SUM_ARG_TYPE: '100'},
            common.ORDERS_TOTAL_SUM_COMPLETED_TRANSLATED,
            'continuous',
        ),
        (
            'skus_count',
            common.GOAL_SKUS_COUNT_ARGS,
            {common.SKUS_COUNT_ARG_TYPE: 5},
            common.SKUS_COUNT_COMPLETED_TRANSLATED,
            'discrete',
        ),
        (
            'skus_total_sum',
            common.GOAL_SKUS_TOTAL_SUM_ARGS,
            {common.SKUS_TOTAL_SUM_ARG_TYPE: '100'},
            common.SKUS_TOTAL_SUM_COMPLETED_TRANSLATED,
            'continuous',
        ),
    ],
)
async def test_progress(
        taxi_grocery_goals,
        pgsql,
        goal_type,
        goal_args,
        progress,
        completed_progress_text,
        progress_type,
):
    models.insert_goal(pgsql, goal_type=goal_type, goal_args=goal_args)
    models.insert_goal_progress(
        pgsql, goal_id=common.GOAL_ID, progress=progress,
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json()['goals'][0]['progress'] == {
        'progress_text': common.PROGRESS_TEXT_TRANSLATED % (
            {
                common.PROGRESS_TEXT_ARG: common.get_typed_args_value(
                    goal_args, progress,
                ),
            }
        ),
        'max_counter': str(common.get_args_value(goal_args)),
        'current_counter': str(common.get_args_value(progress)),
        'completed_progress_text': completed_progress_text % (
            {common.TITLE_ARG: common.get_typed_args_value(goal_args)}
        ),
        'progress_type': progress_type,
        'progress_bar_color': common.PROGRESS_BAR_COLOR,
    }


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T10:00:00+00:00')
async def test_promocode_reward_info(taxi_grocery_goals, pgsql, coupons):
    models.insert_goal(pgsql)

    coupons.check_series_info_request(
        series_id=common.GOAL_REWARD_PROMOCODE['extra']['promocode_series'],
    )

    promocode_value = 555
    coupons.set_series_info_response(body={'value': promocode_value})

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json()['goals'][0]['reward_info'] == {
        'type': 'promocode',
        'extra': {
            'value_text': '-$SIGN$' + str(promocode_value) + '$CURRENCY$',
            'promocode_type': 'fixed',
            'currency_sign': '₽',
            'orders_count_text': '2',
            'orders_count': 2,
        },
    }

    assert coupons.series_info_times_called == 1


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T10:00:00+00:00')
async def test_sku_reward_info(taxi_grocery_goals, pgsql, overlord_catalog):
    sku_image_url_template = 'url/image_1.jpg'

    models.insert_goal(pgsql, goal_reward=common.GOAL_REWARD_SKU)

    skus = list(
        map(
            lambda x: {'id': x, 'picture_link': sku_image_url_template},
            common.DEFAULT_SKUS,
        ),
    )

    overlord_catalog.add_product_data(
        product_id=common.DEFAULT_SKUS[0],
        title='Product 1',
        image_url_template=sku_image_url_template,
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json()['goals'][0]['reward_info'] == {
        'type': 'sku',
        'extra': {'skus': skus},
    }


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T10:00:00+00:00')
async def test_external_vendor_reward_info(
        taxi_grocery_goals, pgsql, overlord_catalog,
):
    models.insert_goal(pgsql, goal_reward=common.GOAL_REWARD_EXTERNAL_VENDOR)

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200
    assert response.json()['goals'][0]['reward_info'] == {
        'type': 'external_vendor',
        'extra': {
            'text': common.EXTERNAL_VENDOR_TEXT_TRANSLATED,
            'picture_link': common.EXTERNAL_VENDOR_PICTURE_LINK,
            'completed_text': common.EXTERNAL_VENDOR_COMPLETED_TEXT_TRANSLATED,
            'more_info': common.EXTERNAL_VENDOR_MORE_INFO,
        },
    }


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T10:00:00+00:00')
async def test_goal_order_by_status(taxi_grocery_goals, pgsql):
    for i in range(1, 6):
        models.insert_goal(pgsql, goal_id=i, name='name' + str(i))

    models.insert_goal_progress(pgsql, goal_id=1, progress_status='expired')
    models.insert_goal_progress(
        pgsql, goal_id=2, progress_status='in_progress', new_seen=True,
    )
    models.insert_goal_progress(
        pgsql, goal_id=3, progress_status='in_progress', new_seen=False,
    )
    models.insert_goal_progress(
        pgsql, goal_id=4, progress_status='completed', completed_seen=True,
    )
    models.insert_goal_progress(
        pgsql, goal_id=5, progress_status='completed', completed_seen=False,
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    goals = response.json()['goals']

    assert goals[0]['status'] == 'completed_not_seen'
    assert goals[1]['status'] == 'new'
    assert goals[2]['status'] == 'in_progress'
    assert goals[3]['status'] == 'completed'
    assert goals[4]['status'] == 'expired'


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T10:00:00+00:00')
async def test_goal_order_by_progress(taxi_grocery_goals, pgsql):
    models.insert_goal(
        pgsql, goal_id=1, name='second', goal_args=common.GOAL_TOTAL_SUM_ARGS,
    )
    models.insert_goal(
        pgsql, goal_id=2, name='first', goal_args=common.GOAL_ORDER_COUNT_ARGS,
    )

    models.insert_goal_progress(
        pgsql,
        goal_id=1,
        progress_status='in_progress',
        progress={'total_sum': '100.0'},
    )
    models.insert_goal_progress(
        pgsql,
        goal_id=2,
        progress_status='in_progress',
        progress={'order_count': 2},
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    goals = response.json()['goals']

    assert goals[0]['goal_id'] == '2'
    assert goals[1]['goal_id'] == '1'


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T18:00:00+00:00')
async def test_goal_list_expired(taxi_grocery_goals, pgsql):
    models.insert_goal(
        pgsql,
        goal_id=1,
        name='expired_should_show',
        expires='2021-10-25T17:10:00+00:00',
    )
    models.insert_goal(
        pgsql,
        goal_id=2,
        name='expired_should_not_show',
        expires='2021-10-25T16:00:00+00:00',
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    goals = response.json()['goals']

    assert len(goals) == 1
    assert goals[0]['goal_id'] == '1'


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T20:00:00+03:00')
async def test_remaining_time_hours(taxi_grocery_goals, pgsql):
    models.insert_goal(pgsql, expires='2021-10-25T20:00:00+01:00')

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    goal = response.json()['goals'][0]
    assert goal['remaining_time_text'] == '2 часа'


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2020-02-28T19:00:00+00:00')
async def test_goal_expired_but_in_progress(taxi_grocery_goals, pgsql):
    models.insert_goal(
        pgsql,
        goal_id=common.GOAL_ID,
        starts='2020-01-01T12:00:00+00:00',
        expires='2020-02-28T16:00:00+00:00',
    )

    models.insert_goal_progress(
        pgsql, goal_id=common.GOAL_ID, progress_status='in_progress',
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    goals = response.json()['goals']
    assert not goals


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-09-01T13:00:00+00:00')
async def test_goal_complete_reward_not_used(taxi_grocery_goals, pgsql):
    models.insert_goal(pgsql, goal_id=common.GOAL_ID)

    models.insert_goal_progress(
        pgsql,
        goal_id=common.GOAL_ID,
        progress_status='completed',
        completed_seen=True,
        complete_at=common.GOAL_COMPLETE_AT,
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    assert response.json()['goals'][0]['status'] == 'completed'
    assert 'reward_used_at' not in response.json()['goals'][0]['reward_info']


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-08-26T12:00:00+00:00')
async def test_goal_complete_reward_used(
        taxi_grocery_goals, pgsql, mocked_time,
):
    reward_used_at = '2021-08-26T12:00:00+00:00'
    models.insert_goal(pgsql, goal_id=common.GOAL_ID)

    models.insert_goal_progress(
        pgsql,
        goal_id=common.GOAL_ID,
        progress_status='completed',
        completed_seen=True,
        complete_at='2021-8-26T11:00:00+00:00',
        reward_used_at=reward_used_at,
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    assert response.json()['goals'][0]['status'] == 'completed'
    assert (
        response.json()['goals'][0]['reward_info']['reward_used_at']
        == reward_used_at
    )

    mocked_time.set(
        datetime.datetime.fromisoformat('2021-08-26T17:00:00+00:00'),
    )
    await taxi_grocery_goals.invalidate_caches()

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    assert not response.json()['goals']


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T10:00:00+00:00')
@pytest.mark.parametrize(
    'goal_args, expected_extra',
    [
        (common.GOAL_TOTAL_SUM_ARGS, None),
        (common.GOAL_ORDER_COUNT_ARGS, None),
        (
            common.GOAL_SKUS_COUNT_ARGS,
            {
                'skus': common.GOAL_SKUS,
                'catalog_text': common.CATALOG_TEXT_TRANSLATED,
                'group_text': common.GROUP_TEXT_TRANSLATED,
                'catalog_picture_link': common.CATALOG_PICTURE_LINK,
                'catalog_link': common.CATALOG_LINK,
            },
        ),
        (
            common.GOAL_SKUS_TOTAL_SUM_ARGS,
            {
                'skus': common.GOAL_SKUS,
                'catalog_text': common.CATALOG_TEXT_TRANSLATED,
                'group_text': common.GROUP_TEXT_TRANSLATED,
                'catalog_picture_link': common.CATALOG_PICTURE_LINK,
                'catalog_link': common.CATALOG_LINK,
            },
        ),
    ],
)
async def test_goal_info_extra(
        taxi_grocery_goals, pgsql, goal_args, expected_extra,
):
    models.insert_goal(pgsql, goal_args=goal_args)

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    response_goal = response.json()['goals'][0]
    if expected_extra:
        assert response_goal['extra'] == expected_extra
    else:
        assert 'extra' not in response_goal


@common.GROCERY_GOALS_TRANSLATIONS
@pytest.mark.experiments3(
    name='grocery_goals_list_retrieve_policy',
    consumers=['grocery-goals/list'],
    match={'predicate': {'init': {}, 'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'is_signal': False,
            'title': 'Always enabled',
            'predicate': {'init': {}, 'type': 'true'},
            'value': {},
        },
    ],
    is_config=True,
)
@pytest.mark.now('2021-10-25T10:00:00+00:00')
async def test_goal_list_all(taxi_grocery_goals, pgsql):
    models.insert_goal(pgsql, goal_id=1, name='expired')
    models.insert_goal(pgsql, goal_id=2, name='in_progress')
    models.insert_goal(pgsql, goal_id=3, name='completed_not_used')
    models.insert_goal(pgsql, goal_id=4, name='completed_used')

    models.insert_goal_progress(pgsql, goal_id=1, progress_status='expired')
    models.insert_goal_progress(
        pgsql, goal_id=2, progress_status='in_progress',
    )
    models.insert_goal_progress(pgsql, goal_id=3, progress_status='completed')
    models.insert_goal_progress(
        pgsql,
        goal_id=4,
        progress_status='completed',
        reward_used_at='2021-10-25T10:00:00+00:00',
        complete_at='2021-10-25T10:00:00+00:00',
    )

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    goals = response.json()['goals']

    assert goals[0]['goal_id'] == '4'
    assert goals[1]['goal_id'] == '3'
    assert goals[2]['goal_id'] == '2'
    assert goals[3]['goal_id'] == '1'


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-09-01T13:00:00+00:00')
async def test_alt_goal_available(
        taxi_grocery_goals, coupons, overlord_catalog, pgsql,
):
    reward_promocode = models.GoalRewardPromocode()
    reward_sku = models.GoalRewardSku()

    models.insert_goal(
        pgsql,
        goal_id=common.GOAL_ID,
        goal_reward=reward_sku.get_reward_db_info(),
        goal_alt_reward=reward_promocode.get_reward_db_info(),
    )

    models.insert_goal_progress(
        pgsql,
        goal_id=common.GOAL_ID,
        progress_status='completed',
        completed_seen=True,
        complete_at=common.GOAL_COMPLETE_AT,
    )

    helpers.configure_goal_reward_promocode(coupons, reward_promocode)
    helpers.configure_goal_reward_sku(overlord_catalog, reward_sku)

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    goal = response.json()['goals'][0]
    assert goal['reward_info'] == reward_sku.get_reward_info()
    assert goal['alt_reward_info'] == reward_promocode.get_reward_info()


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-09-01T13:00:00+00:00')
async def test_alt_goal_swapped(taxi_grocery_goals, coupons, pgsql):
    reward_promocode = models.GoalRewardPromocode()
    reward_sku = models.GoalRewardSku()

    models.insert_goal(
        pgsql,
        goal_id=common.GOAL_ID,
        goal_reward=reward_sku.get_reward_db_info(),
        goal_alt_reward=reward_promocode.get_reward_db_info(),
    )

    models.insert_goal_progress(
        pgsql,
        goal_id=common.GOAL_ID,
        progress_status='completed',
        completed_seen=True,
        complete_at=common.GOAL_COMPLETE_AT,
        reward_swap_at=common.GOAL_REWARD_SWAP_AT,
    )

    helpers.configure_goal_reward_promocode(coupons, reward_promocode)

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    goal = response.json()['goals'][0]
    assert goal['reward_info'] == reward_promocode.get_reward_info()


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-10-25T20:00:00+03:00')
async def test_remaining_time_less_than_hour(taxi_grocery_goals, pgsql):
    models.insert_goal(pgsql, expires='2021-10-25T20:00:59+03:00')

    response = await _make_list_request(taxi_grocery_goals)

    assert response.status_code == 200

    goal = response.json()['goals'][0]
    assert (
        goal['remaining_time_text']
        == common.REMAINING_TIME_LESS_THAN_HOUR_TRANSLATED
    )


@common.GROCERY_GOALS_TRANSLATIONS
@GROCERY_GOALS_LIST_RETRIEVE_POLICY
@pytest.mark.now('2021-09-01T13:00:00+00:00')
@pytest.mark.parametrize(
    'stocks, expected_available',
    [
        (
            [
                {
                    'in_stock': '10',
                    'product_id': 'user_reward_sku',
                    'quantity_limit': '5',
                },
                {
                    'in_stock': '10',
                    'product_id': 'more_sku',
                    'quantity_limit': '5',
                },
            ],
            True,
        ),
        (
            [
                {
                    'in_stock': '10',
                    'product_id': 'more_sku',
                    'quantity_limit': '5',
                },
            ],
            False,
        ),
    ],
)
async def test_goal_sku_reward(
        taxi_grocery_goals,
        pgsql,
        mockserver,
        overlord_catalog,
        grocery_depots,
        stocks,
        expected_available,
):
    sku_user_reward = 'user_reward_sku'
    sku_reward = 'more_sku'

    sku_image_url_template = 'url/image_1.jpg'

    models.insert_goal(
        pgsql,
        goal_id=common.GOAL_ID,
        goal_reward={
            'type': common.GOAL_REWARD_SKU_TYPE,
            'extra': {'skus': [sku_user_reward, sku_reward]},
        },
    )

    models.insert_goal_progress(
        pgsql,
        goal_id=common.GOAL_ID,
        progress_status='completed',
        reward={'sku': sku_user_reward},
    )

    grocery_depots.add_depot(
        legacy_depot_id='legacy_depot_id',
        depot_id='1235123',
        location=USER_LOCATION,
    )

    overlord_catalog.add_product_data(
        product_id=sku_reward,
        title='Product 1',
        image_url_template=sku_image_url_template,
    )

    overlord_catalog.add_product_data(
        product_id=sku_user_reward,
        title='Product 1',
        image_url_template=sku_image_url_template,
    )

    @mockserver.json_handler('/overlord-catalog/internal/v1/catalog/v1/stocks')
    def _mock_stocks(request):
        return {'stocks': stocks}

    response = await _make_list_request(
        taxi_grocery_goals, location=USER_LOCATION,
    )

    assert response.status_code == 200

    assert response.json()['goals'][0]['reward_info'] == {
        'extra': {
            'skus': [
                {
                    'id': sku_user_reward,
                    'picture_link': sku_image_url_template,
                },
                {'id': sku_reward, 'picture_link': sku_image_url_template},
            ],
            'user_sku': {
                'available': expected_available,
                'id': sku_user_reward,
            },
        },
        'type': 'sku',
    }
