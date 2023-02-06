import datetime

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks.models import cart
# pylint: enable=import-error
import pytest

from tests_grocery_goals import common
from tests_grocery_goals import models


PERSONAL_PHONE_ID = 'personal_phone_id'

ORDERS_COUNT_TYPE = 'orders_count'
TOTAL_SUM_COUNT = 'orders_total_sum'
SKUS_COUNT_TYPE = 'skus_count'
SKUS_TOTAL_SUM_TYPE = 'skus_total_sum'

COUPONS_PROMOCODE = 'promocode_for_goals'

CART_ID = '28fe4a6e-c00d-45c1-a34e-6329c4a4e329'
CART_VERSION = 10
ITEM_PRICE = 150
ITEM_QUANTITY = 2

ORDER_ID = 'order_id-grocery'
ORDER_CREATED = '2021-09-25T12:00:00+0000'

DEPOT_ID = 'some_depot_id'

CART_ITEMS = [
    cart.GroceryCartItem(
        item_id='sku1', price=str(ITEM_PRICE), quantity=str(ITEM_QUANTITY),
    ),
]


@pytest.fixture(name='add_user_tag')
def add_user_tag_fixture(grocery_tags):
    def _do(
            personal_phone_id=PERSONAL_PHONE_ID,
            tag=common.GOAL_MARKETING_TAGS[0],
    ):
        grocery_tags.add_tag(personal_phone_id=personal_phone_id, tag=tag)

    return _do


@pytest.fixture(name='add_cart')
def add_cart_fixture(grocery_cart):
    def _do(items=None):
        if items is None:
            items = CART_ITEMS
        grocery_cart.set_cart_data(cart_id=CART_ID, cart_version=CART_VERSION)
        grocery_cart.set_items(items=items)

    return _do


@pytest.fixture(name='add_order')
def add_order_fixture(grocery_orders_lib):
    def _do():
        grocery_orders_lib.add_order(
            order_id=ORDER_ID,
            cart_id=CART_ID,
            created=ORDER_CREATED,
            yandex_uid=common.YANDEX_UID,
            personal_phone_id=PERSONAL_PHONE_ID,
            locale='ru',
            app_info='app_name=lavka_iphone',
            user_info={
                'personal_phone_id': PERSONAL_PHONE_ID,
                'taxi_user_id': 'taxi_user_id',
                'eats_user_id': common.EATS_USER_ID,
            },
            depot_id=DEPOT_ID,
            finish_started=common.GOAL_COMPLETE_AT,
        )

    return _do


@pytest.fixture(name='add_coupon')
def add_coupon_fixture(coupons):
    def _do():
        coupons.set_coupons_generate_response({'promocode': COUPONS_PROMOCODE})
        coupons.check_generate_request(
            yandex_uid=common.YANDEX_UID,
            series_id=common.GOAL_REWARD_PROMOCODE_SERIES,
        )

    return _do


@pytest.fixture(name='check_goal_progress')
def check_goal_progress_fixture(pgsql, coupons):
    def _do(
            expected_status,
            expected_progress,
            reward_type=common.GOAL_REWARD_PROMOCODE_TYPE,
    ):
        progress = models.get_goal_progress(
            pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
        )

        assert progress.progress == expected_progress

        assert progress.progress_status == expected_status

        if expected_status == 'completed':
            if reward_type == common.GOAL_REWARD_PROMOCODE_TYPE:
                assert progress.reward == {'promocode': COUPONS_PROMOCODE}
            elif reward_type == common.GOAL_REWARD_SKU_TYPE:
                assert progress.reward == {'sku': common.DEFAULT_SKUS[0]}
            elif reward_type == common.GOAL_REWARD_EXTERNAL_VENDOR_TYPE:
                assert not progress.reward
            else:
                assert False
        else:
            assert not progress.reward

    return _do


@pytest.fixture(name='check_finished_calls')
def check_finished_calls_fixture(stq, coupons):
    def _do(expected_status):
        if expected_status == 'completed':
            assert coupons.generate_times_called == 1
            assert stq.grocery_goals_finish_push.times_called == 1
        else:
            assert coupons.generate_times_called == 0
            assert stq.grocery_goals_finish_push.times_called == 0

    return _do


@pytest.fixture(name='call_order_close')
def call_order_close_fixture(stq_runner):
    async def _do():
        await stq_runner.grocery_goals_order_close.call(
            task_id=ORDER_ID, kwargs={'order_id': ORDER_ID},
        )

    return _do


@pytest.mark.parametrize(
    'starting_order_count, expected_status',
    [(8, 'in_progress'), (9, 'completed')],
)
async def test_order_count(
        taxi_grocery_goals,
        add_user_tag,
        add_order,
        add_cart,
        add_coupon,
        check_goal_progress,
        check_finished_calls,
        call_order_close,
        pgsql,
        starting_order_count,
        expected_status,
):
    add_user_tag()
    add_cart()
    add_order()
    add_coupon()

    models.insert_goal(
        pgsql=pgsql,
        goal_type=ORDERS_COUNT_TYPE,
        goal_args={common.ORDER_COUNT_ARG_TYPE: 10},
    )

    models.insert_goal_progress(
        pgsql, progress={common.ORDER_COUNT_ARG_TYPE: starting_order_count},
    )

    await call_order_close()

    expected_progress = {common.ORDER_COUNT_ARG_TYPE: starting_order_count + 1}
    check_goal_progress(expected_status, expected_progress)

    check_finished_calls(expected_status)

    await call_order_close()

    check_goal_progress(expected_status, expected_progress)


@pytest.mark.parametrize(
    'starting_sum, expected_status',
    [(1000, 'in_progress'), (1200, 'completed')],
)
async def test_order_total_sum(
        taxi_grocery_goals,
        add_user_tag,
        add_order,
        add_cart,
        add_coupon,
        check_goal_progress,
        check_finished_calls,
        call_order_close,
        pgsql,
        starting_sum,
        expected_status,
):
    add_user_tag()
    add_cart()
    add_order()
    add_coupon()

    models.insert_goal(
        pgsql=pgsql,
        goal_type=TOTAL_SUM_COUNT,
        goal_args={common.TOTAL_SUM_ARG_TYPE: '1500', 'currency_code': 'RUB'},
    )

    models.insert_goal_progress(
        pgsql, progress={common.TOTAL_SUM_ARG_TYPE: str(starting_sum)},
    )

    await call_order_close()

    expected_progress = {
        common.TOTAL_SUM_ARG_TYPE: str(
            starting_sum + ITEM_PRICE * ITEM_QUANTITY,
        ),
    }
    check_goal_progress(expected_status, expected_progress)

    check_finished_calls(expected_status)

    await call_order_close()

    check_goal_progress(expected_status, expected_progress)


@pytest.mark.parametrize(
    'starting_skus_count, expected_status',
    [(2, 'in_progress'), (3, 'completed')],
)
async def test_skus_count(
        taxi_grocery_goals,
        add_user_tag,
        add_order,
        add_cart,
        add_coupon,
        check_goal_progress,
        check_finished_calls,
        call_order_close,
        pgsql,
        starting_skus_count,
        expected_status,
):
    add_user_tag()
    add_order()
    add_coupon()

    sku1 = 'sku1'
    sku1_quantity = 2
    sku2 = 'sku2'
    sku2_quantity = 1

    add_cart(
        items=[
            cart.GroceryCartItem(
                item_id=sku1,
                price=str(ITEM_PRICE),
                quantity=str(sku1_quantity),
            ),
            cart.GroceryCartItem(
                item_id=sku2,
                price=str(ITEM_PRICE),
                quantity=str(sku2_quantity),
            ),
        ],
    )

    models.insert_goal(
        pgsql=pgsql,
        goal_type=SKUS_COUNT_TYPE,
        goal_args={common.SKUS_COUNT_ARG_TYPE: 6, 'skus': [sku1, sku2]},
    )

    models.insert_goal_progress(
        pgsql, progress={common.SKUS_COUNT_ARG_TYPE: starting_skus_count},
    )

    await call_order_close()

    expected_progress = {
        common.SKUS_COUNT_ARG_TYPE: (
            starting_skus_count + sku1_quantity + sku2_quantity
        ),
    }
    check_goal_progress(expected_status, expected_progress)

    check_finished_calls(expected_status)

    await call_order_close()

    check_goal_progress(expected_status, expected_progress)


@pytest.mark.parametrize(
    'starting_sum, expected_status',
    [(1000, 'in_progress'), (1200, 'completed')],
)
async def test_skus_total_sum(
        taxi_grocery_goals,
        add_user_tag,
        add_order,
        add_cart,
        add_coupon,
        check_goal_progress,
        check_finished_calls,
        call_order_close,
        pgsql,
        starting_sum,
        expected_status,
):
    add_user_tag()
    add_order()
    add_coupon()

    sku1 = 'sku1'
    sku1_quantity = 2
    sku1_price = 50
    sku2 = 'sku2'
    sku2_price = 200
    sku2_quantity = 1

    add_cart(
        items=[
            cart.GroceryCartItem(
                item_id=sku1,
                price=str(sku1_price),
                quantity=str(sku1_quantity),
            ),
            cart.GroceryCartItem(
                item_id=sku2,
                price=str(sku2_price),
                quantity=str(sku2_quantity),
            ),
            cart.GroceryCartItem(
                item_id='sku3', price=str(ITEM_PRICE), quantity='2',
            ),
        ],
    )

    models.insert_goal(
        pgsql=pgsql,
        goal_type=SKUS_TOTAL_SUM_TYPE,
        goal_args={
            'skus': [sku1, sku2],
            common.SKUS_TOTAL_SUM_ARG_TYPE: '1500',
            'currency_code': 'RUB',
        },
    )

    models.insert_goal_progress(
        pgsql, progress={common.SKUS_TOTAL_SUM_ARG_TYPE: str(starting_sum)},
    )

    await call_order_close()

    expected_progress = {
        common.SKUS_TOTAL_SUM_ARG_TYPE: str(
            starting_sum
            + sku1_price * sku1_quantity
            + sku2_price * sku2_quantity,
        ),
    }

    check_goal_progress(expected_status, expected_progress)

    check_finished_calls(expected_status)

    await call_order_close()

    check_goal_progress(expected_status, expected_progress)


async def test_no_progress(
        taxi_grocery_goals, add_user_tag, add_order, call_order_close, pgsql,
):
    add_user_tag()
    add_order()

    models.insert_goal(pgsql=pgsql)

    await call_order_close()

    goal_progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )

    assert goal_progress.progress_status == 'in_progress'
    assert goal_progress.complete_at is None
    assert goal_progress.progress == {'order_count': 1}


async def test_goal_not_started(
        taxi_grocery_goals, add_user_tag, add_order, call_order_close, pgsql,
):
    add_user_tag()
    add_order()

    models.insert_goal(pgsql=pgsql, starts='2021-10-24T12:00:00+0000')
    starting_progress = {common.ORDER_COUNT_ARG_TYPE: 8}
    models.insert_goal_progress(pgsql, progress=starting_progress)

    await call_order_close()

    goal_progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )

    assert goal_progress.progress == starting_progress


async def test_already_completed_goal(
        taxi_grocery_goals,
        add_user_tag,
        call_order_close,
        add_order,
        pgsql,
        stq,
):
    add_user_tag()
    add_order()

    models.insert_goal(pgsql=pgsql)
    models.insert_goal_progress(
        pgsql,
        progress_status='completed',
        progress={common.ORDER_COUNT_ARG_TYPE: 10},
        reward_used_at=common.GOAL_REWARD_USED_AT,
        complete_at=common.GOAL_COMPLETE_AT,
    )

    await call_order_close()

    goal_progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )

    assert goal_progress.progress_status == 'completed'
    assert goal_progress.complete_at == datetime.datetime.fromisoformat(
        common.GOAL_COMPLETE_AT,
    )
    assert stq.grocery_goals_finish_push.times_called == 0


async def test_mark_expired_goals(
        taxi_grocery_goals,
        add_user_tag,
        add_order,
        call_order_close,
        stq,
        pgsql,
):
    other_yandex_uid_in_progress = 'other_yandex_uid_in_progress'
    other_yandex_uid_completed = 'other_yandex_uid_completed'
    goal_expires = '2021-09-24T12:00:00+0000'

    add_user_tag()
    add_order()

    models.insert_goal(pgsql=pgsql, expires=goal_expires)

    models.insert_goal_progress(pgsql)

    models.insert_goal_progress(
        pgsql,
        yandex_uid=other_yandex_uid_in_progress,
        goal_id=common.GOAL_ID,
        progress_status='in_progress',
    )

    models.insert_goal_progress(
        pgsql,
        yandex_uid=other_yandex_uid_completed,
        goal_id=common.GOAL_ID,
        progress_status='completed',
        reward_used_at=common.GOAL_REWARD_USED_AT,
    )

    await call_order_close()

    goal_progress_current = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )
    other_goal_progress_in_progress = models.get_goal_progress(
        pgsql, yandex_uid=other_yandex_uid_in_progress, goal_id=common.GOAL_ID,
    )
    other_goal_progress_completed = models.get_goal_progress(
        pgsql, yandex_uid=other_yandex_uid_completed, goal_id=common.GOAL_ID,
    )

    assert goal_progress_current.progress_status == 'expired'
    assert other_goal_progress_in_progress.progress_status == 'in_progress'
    assert other_goal_progress_completed.progress_status == 'completed'

    assert stq.grocery_goals_finish_push.times_called == 0


@pytest.mark.now('2021-08-26T12:00:00+00:00')
async def test_goal_finish_push(
        taxi_grocery_goals,
        add_user_tag,
        call_order_close,
        add_order,
        stq,
        pgsql,
):
    models.insert_goal(pgsql=pgsql)
    models.insert_goal_progress(
        pgsql, progress={common.ORDER_COUNT_ARG_TYPE: 9},
    )

    add_user_tag()
    add_order()

    await call_order_close()

    goal_progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )

    assert goal_progress.progress_status == 'completed'
    assert goal_progress.complete_at == datetime.datetime.fromisoformat(
        common.GOAL_COMPLETE_AT,
    )

    next_stq_call = stq.grocery_goals_finish_push.next_call()

    assert (
        next_stq_call['id']
        == str(ORDER_ID) + '-' + str(common.GOAL_ID) + '-goals_finish_push'
    )
    assert next_stq_call['queue'] == 'grocery_goals_finish_push'

    stq_args = next_stq_call['kwargs']['args']
    assert (
        stq_args['title_tanker_key']
        == common.GOAL_PUSH_INFO['finish_title_tanker_key']
    )
    assert (
        stq_args['message_tanker_key']
        == common.GOAL_PUSH_INFO['finish_message_tanker_key']
    )
    assert stq_args['application'] == 'lavka_iphone'
    assert stq_args['goal_id'] == common.GOAL_ID
    assert (
        stq_args['idempotency_token']
        == str(ORDER_ID) + '-' + str(common.GOAL_ID) + '-goals_finish_push'
    )
    assert stq_args['locale'] == 'ru'
    assert stq_args['taxi_user_id'] == 'taxi_user_id'
    assert stq_args['yandex_uid'] == common.YANDEX_UID
    assert stq_args['eats_user_id'] == common.EATS_USER_ID


async def test_no_push_on_no_title_and_text(
        taxi_grocery_goals,
        add_user_tag,
        call_order_close,
        add_order,
        stq,
        pgsql,
):
    models.insert_goal(
        pgsql=pgsql, finish_push_title=None, finish_push_message=None,
    )
    models.insert_goal_progress(
        pgsql, progress={common.ORDER_COUNT_ARG_TYPE: 9},
    )

    add_user_tag()
    add_order()

    await call_order_close()

    goal_progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )

    assert goal_progress.progress_status == 'completed'
    assert stq.grocery_goals_finish_push.times_called == 0


@pytest.mark.parametrize(
    'goal_type, goal_progress',
    [
        ('orders_total_sum', {common.TOTAL_SUM_ARG_TYPE: '200'}),
        ('skus_total_sum', {common.SKUS_TOTAL_SUM_ARG_TYPE: '200'}),
    ],
)
async def test_goal_currency_mismatch(
        taxi_grocery_goals,
        add_order,
        add_cart,
        add_user_tag,
        call_order_close,
        pgsql,
        goal_type,
        goal_progress,
):
    add_cart(
        items=[
            cart.GroceryCartItem(
                item_id='item_id', price='150', quantity='2', currency='EUR',
            ),
        ],
    )

    add_user_tag()
    add_order()

    models.insert_goal(
        pgsql, goal_type=goal_type, goal_args=common.GOAL_ARGS[goal_type],
    )
    models.insert_goal_progress(pgsql, progress=goal_progress)

    await call_order_close()

    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )

    assert progress.progress == goal_progress


@pytest.mark.parametrize('goal_type', ['orders_total_sum', 'skus_total_sum'])
async def test_goal_currency_mismatch_no_progress(
        taxi_grocery_goals,
        add_order,
        add_cart,
        add_user_tag,
        call_order_close,
        pgsql,
        goal_type,
):
    add_cart(
        items=[
            cart.GroceryCartItem(
                item_id='item_id', price='150', quantity='2', currency='EUR',
            ),
        ],
    )

    add_user_tag()
    add_order()

    models.insert_goal(
        pgsql, goal_type=goal_type, goal_args=common.GOAL_ARGS[goal_type],
    )

    await call_order_close()

    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )

    assert not progress


async def test_no_update_completed(
        taxi_grocery_goals, add_order, add_user_tag, call_order_close, pgsql,
):
    goal_progress = {common.ORDER_COUNT_ARG_TYPE: 10}

    add_user_tag()
    add_order()

    models.insert_goal(pgsql)
    models.insert_goal_progress(
        pgsql,
        progress=goal_progress,
        progress_status='completed',
        reward_used_at=common.GOAL_REWARD_USED_AT,
    )

    await call_order_close()

    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )

    assert progress.progress == goal_progress
    assert progress.progress_status == 'completed'


async def test_not_started_goal_with_progress(
        taxi_grocery_goals,
        grocery_tags,
        pgsql,
        grocery_orders_lib,
        stq,
        stq_runner,
):
    order_id = 'order_id-grocery'
    order_created = '2021-09-24T12:00:00+0000'
    personal_phone_id = 'some_personal_phone_id'
    marketing_tag = 'some_tag'

    goal_expires = '2021-09-25T15:00:00+0000'
    goal_starts = '2021-09-24T13:00:00+0000'

    grocery_tags.add_tag(
        personal_phone_id=personal_phone_id, tag=marketing_tag,
    )

    grocery_orders_lib.add_order(
        order_id=order_id,
        created=order_created,
        yandex_uid=common.YANDEX_UID,
        personal_phone_id=personal_phone_id,
    )

    models.insert_goal(
        pgsql=pgsql,
        goal_id=common.GOAL_ID,
        expires=goal_expires,
        starts=goal_starts,
        marketing_tags=[marketing_tag],
    )

    models.insert_goal_progress(
        pgsql,
        yandex_uid=common.YANDEX_UID,
        goal_id=common.GOAL_ID,
        progress_status='in_progress',
    )

    await stq_runner.grocery_goals_order_close.call(
        task_id=order_id, kwargs={'order_id': order_id},
    )

    goal_progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )

    assert goal_progress.progress_status == 'in_progress'

    assert stq.grocery_goals_finish_push.times_called == 0


async def test_sku_reward_basic(
        taxi_grocery_goals,
        mockserver,
        add_user_tag,
        add_order,
        add_cart,
        add_coupon,
        check_goal_progress,
        call_order_close,
        pgsql,
):
    add_user_tag()
    add_cart()
    add_order()
    add_coupon()

    models.insert_goal(
        pgsql=pgsql,
        goal_type=ORDERS_COUNT_TYPE,
        goal_args={common.ORDER_COUNT_ARG_TYPE: 10},
        goal_reward=common.GOAL_REWARD_SKU,
    )

    models.insert_goal_progress(
        pgsql, progress={common.ORDER_COUNT_ARG_TYPE: 9},
    )

    @mockserver.json_handler('/overlord-catalog/internal/v1/catalog/v1/stocks')
    def _mock_stocks(request):
        return {
            'stocks': [
                {
                    'in_stock': '10',
                    'product_id': common.DEFAULT_SKUS[0],
                    'quantity_limit': '5',
                },
            ],
        }

    await call_order_close()

    expected_progress = {common.ORDER_COUNT_ARG_TYPE: 10}
    check_goal_progress(
        'completed',
        expected_progress,
        reward_type=common.GOAL_REWARD_SKU_TYPE,
    )


async def test_sku_reward_not_use_received(
        taxi_grocery_goals,
        mockserver,
        add_user_tag,
        add_order,
        add_cart,
        add_coupon,
        check_goal_progress,
        call_order_close,
        pgsql,
):
    other_goal_id = '12345'

    sku_1 = 'sku_1'
    sku_2 = 'sku_2'
    goal_reward = {
        'type': common.GOAL_REWARD_SKU_TYPE,
        'extra': {'skus': [sku_1, sku_2]},
    }

    add_user_tag()
    add_cart()
    add_order()
    add_coupon()

    models.insert_goal(
        pgsql=pgsql,
        goal_type=ORDERS_COUNT_TYPE,
        goal_args={common.ORDER_COUNT_ARG_TYPE: 10},
        goal_reward=goal_reward,
    )

    models.insert_goal_progress(
        pgsql, progress={common.ORDER_COUNT_ARG_TYPE: 9},
    )

    models.insert_goal(
        pgsql=pgsql,
        goal_id=other_goal_id,
        name='other_name',
        goal_type=ORDERS_COUNT_TYPE,
        goal_args={common.ORDER_COUNT_ARG_TYPE: 10},
        goal_reward=goal_reward,
    )

    models.insert_goal_progress(
        pgsql,
        goal_id=other_goal_id,
        progress_status='completed',
        reward={'sku': sku_1},
    )

    @mockserver.json_handler('/overlord-catalog/internal/v1/catalog/v1/stocks')
    def _mock_stocks(request):
        return {
            'stocks': [
                {'in_stock': '10', 'product_id': sku_1, 'quantity_limit': '5'},
                {'in_stock': '10', 'product_id': sku_2, 'quantity_limit': '5'},
            ],
        }

    await call_order_close()

    progress = models.get_goal_progress(
        pgsql, yandex_uid=common.YANDEX_UID, goal_id=common.GOAL_ID,
    )

    assert progress.reward == {'sku': sku_2}


async def test_external_vendor_reward_basic(
        taxi_grocery_goals,
        add_user_tag,
        add_order,
        add_cart,
        add_coupon,
        check_goal_progress,
        call_order_close,
        pgsql,
):
    add_user_tag()
    add_cart()
    add_order()
    add_coupon()

    models.insert_goal(
        pgsql=pgsql,
        goal_type=ORDERS_COUNT_TYPE,
        goal_args={common.ORDER_COUNT_ARG_TYPE: 10},
        goal_reward=common.GOAL_REWARD_EXTERNAL_VENDOR,
    )

    models.insert_goal_progress(
        pgsql, progress={common.ORDER_COUNT_ARG_TYPE: 9},
    )

    await call_order_close()

    expected_progress = {common.ORDER_COUNT_ARG_TYPE: 10}
    check_goal_progress(
        'completed',
        expected_progress,
        reward_type=common.GOAL_REWARD_EXTERNAL_VENDOR_TYPE,
    )
