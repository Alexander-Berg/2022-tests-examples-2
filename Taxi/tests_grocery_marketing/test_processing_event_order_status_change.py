# pylint: disable=too-many-lines
import copy

import pytest

from tests_grocery_marketing import configs
from tests_grocery_marketing import models
from tests_grocery_marketing import utils


LIMIT_LAST_ORDER_IDS = 3
ADD_RULE_TIME = '2020-01-01T00:00:00+0000'


async def _post_order_event(taxi_grocery_marketing, order_id, status_change):
    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/order/status-change',
        json={'order_id': order_id, 'status_change': status_change},
    )
    assert response.status_code == 200


async def _add_rules(taxi_grocery_marketing, pgsql):
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, kind='marketing',
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, suffix='2', kind='marketing',
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, product=['product_1'], kind='marketing',
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, product=['product_3'], kind='marketing',
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing,
        pgsql,
        group=['category_1'],
        product=['product_1', 'product_2', 'product_3'],
        kind='marketing',
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, group=['category_2'], kind='marketing',
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, depot=['depot_1'], kind='marketing',
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing,
        pgsql,
        depot=['depot_2'],
        group=['category_1'],
        kind='marketing',
    )
    await taxi_grocery_marketing.invalidate_caches()


def _check_adjust_event(payload, status_change, matched_tags, expected_fields):
    assert payload['reason'] == 'adjust_event'
    assert payload['adjust_event']['is_successful'] == (
        status_change == 'closed'
    )

    for field_key, field_value in expected_fields.items():
        assert payload['adjust_event'][field_key] == field_value

    actual_matched_tags = payload['adjust_event']['matched_tags']
    expected_matched_tags = [
        {'tag': tag, 'count': count} for tag, count in matched_tags
    ]

    assert len(actual_matched_tags) == len(expected_matched_tags)

    for tag in expected_matched_tags:
        assert tag in actual_matched_tags


def _check_other_tag_statistic(pgsql, ids_info, tag, usage_count):
    for id_info in ids_info:
        tag_stat = models.OtherTagStatistic.fetch(
            pgsql=pgsql,
            user_id=id_info['user_id'],
            id_type=id_info['id_type'],
            tag=tag,
        )
        assert tag_stat.usage_count == usage_count


@pytest.mark.config(
    GROCERY_MARKETING_LIMIT_LAST_ORDER_IDS=LIMIT_LAST_ORDER_IDS,
)
@pytest.mark.parametrize(
    'depot_id, products, matched_tags',
    [
        (
            'depot_1',
            [
                ('product_1', ['category_1', 'category_2']),
                ('product_2', ['category_1']),
            ],
            [
                'tag_all',
                'tag_all2',
                'tag_product_1',
                'tag_category_1_product_1_product_2_product_3',
                'tag_category_2',
                'tag_depot_1',
            ],
        ),
        (
            'depot_1',
            [
                ('product_1', ['category_1']),
                ('product_2', ['category_1']),
                ('product_3', ['category_1']),
            ],
            [
                'tag_all',
                'tag_all2',
                'tag_product_1',
                'tag_category_1_product_1_product_2_product_3',
                'tag_product_3',
                'tag_depot_1',
            ],
        ),
        (
            'depot_2',
            [('product_1', ['category_2'])],
            ['tag_all', 'tag_all2', 'tag_product_1', 'tag_category_2'],
        ),
    ],
)
@pytest.mark.config(
    GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True,
    GROCERY_MARKETING_COUNTER_WITHOUT_PAYMENT='2019-09-08T00:00:00+00:00',
)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.parametrize('is_adjust_order', [True, False])
@pytest.mark.parametrize('is_order_without_payment', [True, False])
@pytest.mark.now(ADD_RULE_TIME)
async def test_basic(
        depot_id,
        products,
        matched_tags,
        taxi_grocery_marketing,
        pgsql,
        overlord_catalog,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
        experiments3,
        is_adjust_order,
        is_order_without_payment,
):
    yandex_uid = 'some_yandex_uid'
    order_id = 'some_order_id'
    taxi_user_id = 'some_taxi_user_id'
    eats_user_id = 'some_eats_user_id'
    personal_phone_id = 'some_personal_phone_id'
    phone_id = 'some_phone_id'
    payment_id = 'some_payment_id'
    app_vars = 'app_brand=some_app_vars'
    appmetrica_device_id = 'some_appmetrica'
    status_change = 'closed'
    product_ids = [product_id for product_id, _ in products]

    matched_tags = copy.deepcopy(matched_tags)
    matched_tags += ['total_orders_count']
    if is_adjust_order:
        matched_tags += ['total_adjust_orders_count']

    if is_order_without_payment:
        matched_tags += ['total_order_count_without_payments']
        grocery_cart_products = [
            models.GroceryCartItem(item_id=product_id, price='0.0')
            for product_id in product_ids
        ]
    else:
        grocery_cart_products = [
            models.GroceryCartItem(item_id=product_id)
            for product_id in product_ids
        ]

    configs.add_is_adjust_order_config(experiments3, is_adjust_order)
    await taxi_grocery_marketing.invalidate_caches()

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    await _add_rules(taxi_grocery_marketing, pgsql)

    user_ids = {
        'taxi_user_id': taxi_user_id,
        'eats_user_id': eats_user_id,
        'personal_phone_id': personal_phone_id,
        'phone_id': phone_id,
        'app_vars': app_vars,
        'appmetrica_device_id': appmetrica_device_id,
        'yandex_uid': yandex_uid,
    }

    ids_info = [
        {'user_id': appmetrica_device_id, 'id_type': 'appmetrica_device_id'},
        {'user_id': payment_id, 'id_type': 'payment_id'},
        {'user_id': personal_phone_id, 'id_type': 'personal_phone_id'},
    ]

    mocked_order = grocery_orders.add_order(
        order_id=order_id,
        yandex_uid=yandex_uid,
        depot_id=depot_id,
        region_id=213,
        user_info=user_ids,
    )

    for product_id, category_ids in products:
        overlord_catalog.add_product(
            product_id=product_id, category_ids=category_ids,
        )

    grocery_cart.set_cart_data(
        cart_id=mocked_order['cart_id'],
        cart_version=mocked_order['cart_version'],
    )
    grocery_cart.set_payment_method(
        {'id': payment_id, 'type': 'card', 'discount': False},
    )
    grocery_cart.set_items(items=grocery_cart_products)

    current_tag_stat = models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=yandex_uid,
        tag='total_current_orders_count',
        usage_count=2,
    )
    assert current_tag_stat.usage_count == 2

    await _post_order_event(
        taxi_grocery_marketing, order_id=order_id, status_change=status_change,
    )

    for tag in matched_tags:
        tag_stat = models.TagStatistic.fetch(
            pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
        )
        assert tag_stat.usage_count == 1

        _check_other_tag_statistic(pgsql, ids_info, tag, 1)

    current_tag_stat.update()
    assert current_tag_stat.usage_count == 1

    # Check adjust event
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    if is_adjust_order:
        assert len(events) == 1
        event = events[-1]
        _check_adjust_event(
            event.payload,
            status_change,
            [(tag, 1) for tag in matched_tags],
            {**user_ids, 'order_id': order_id},
        )
    else:
        assert not events

    # Check: no increment for the same order
    await _post_order_event(
        taxi_grocery_marketing, order_id=order_id, status_change=status_change,
    )
    for tag in matched_tags:
        tag_stat = models.TagStatistic.fetch(
            pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
        )
        assert tag_stat.usage_count == 1

        _check_other_tag_statistic(pgsql, ids_info, tag, 1)

    # Check adjust event
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    if is_adjust_order:
        assert len(events) == 2
    else:
        assert not events

    # Add new tag
    new_tag = 'tag_all3'
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, suffix='3', kind='marketing',
    )
    await taxi_grocery_marketing.invalidate_caches()

    # Create new order
    order_id = order_id + '_new'
    mocked_order.update(order_id=order_id)
    await _post_order_event(
        taxi_grocery_marketing, order_id=order_id, status_change=status_change,
    )

    for tag in matched_tags:
        tag_stat = models.TagStatistic.fetch(
            pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
        )
        assert tag_stat.usage_count == 2

        _check_other_tag_statistic(pgsql, ids_info, tag, 2)

    tag_stat = models.TagStatistic.fetch(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=new_tag,
    )
    assert tag_stat.usage_count == 1

    current_tag_stat.update()
    assert current_tag_stat.usage_count == 1

    _check_other_tag_statistic(pgsql, ids_info, new_tag, 1)

    # Check adjust event
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    if is_adjust_order:
        assert len(events) == 3
        event = events[-1]
        _check_adjust_event(
            event.payload,
            status_change,
            [(tag, 2) for tag in matched_tags] + [(new_tag, 1)],
            {**user_ids, 'order_id': order_id},
        )
    else:
        assert not events

    # Check: no increment for the same order
    await _post_order_event(
        taxi_grocery_marketing, order_id=order_id, status_change=status_change,
    )

    for tag in matched_tags:
        tag_stat = models.TagStatistic.fetch(
            pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
        )
        assert tag_stat.usage_count == 2

        _check_other_tag_statistic(pgsql, ids_info, tag, 2)

    tag_stat = models.TagStatistic.fetch(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=new_tag,
    )
    assert tag_stat.usage_count == 1

    _check_other_tag_statistic(pgsql, ids_info, new_tag, 1)

    # Check adjust event
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    if is_adjust_order:
        assert len(events) == 4
    else:
        assert not events


@pytest.mark.config(GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@configs.GROCERY_MARKETING_IS_ADJUST_ORDER
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now(ADD_RULE_TIME)
async def test_only_marketing_tags_to_adjust(
        taxi_grocery_marketing,
        pgsql,
        overlord_catalog,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
):
    yandex_uid = 'some_yandex_uid'
    order_id = 'some_order_id'
    status_change = 'closed'
    depot_id = 'depot_id'
    product_id = 'some_product_id'
    category_id = 'some_category_id'
    marketing_tag = 'tag_all1'

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, suffix='1', kind='marketing',
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, suffix='2', kind='promocode',
    )
    await taxi_grocery_marketing.invalidate_caches()

    mocked_order = grocery_orders.add_order(
        order_id=order_id,
        yandex_uid=yandex_uid,
        depot_id=depot_id,
        region_id=213,
    )

    grocery_cart.set_cart_data(
        cart_id=mocked_order['cart_id'],
        cart_version=mocked_order['cart_version'],
    )
    grocery_cart.set_items(items=[models.GroceryCartItem(item_id=product_id)])

    overlord_catalog.add_product(
        product_id=product_id, category_ids=[category_id],
    )

    await _post_order_event(
        taxi_grocery_marketing, order_id=order_id, status_change=status_change,
    )

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 1
    event = events[-1]
    _check_adjust_event(
        event.payload,
        status_change,
        [
            (marketing_tag, 1),
            ('total_orders_count', 1),
            ('total_adjust_orders_count', 1),
        ],
        {'yandex_uid': yandex_uid, 'order_id': order_id},
    )


@pytest.mark.config(GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@pytest.mark.parametrize('is_adjust_order', [True, False])
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now(ADD_RULE_TIME)
async def test_status_change_canceled(
        taxi_grocery_marketing,
        pgsql,
        overlord_catalog,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
        experiments3,
        is_adjust_order,
):
    yandex_uid = 'some_yandex_uid'
    order_id = 'some_order_id'
    status_change = 'canceled'
    depot_id = 'depot_id'
    product_id = 'some_product_id'
    category_id = 'some_category_id'

    configs.add_is_adjust_order_config(experiments3, is_adjust_order)
    await taxi_grocery_marketing.invalidate_caches()

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    marketing_tag = 'tag_all'

    tag_stat = models.TagStatistic(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=marketing_tag, usage_count=2,
    )
    assert tag_stat.usage_count == 2

    current_tag_stat = models.TagStatistic(
        pgsql=pgsql,
        yandex_uid=yandex_uid,
        tag='total_current_orders_count',
        usage_count=2,
    )
    assert current_tag_stat.usage_count == 2

    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, kind='marketing',
    )
    await taxi_grocery_marketing.invalidate_caches()

    mocked_order = grocery_orders.add_order(
        order_id=order_id,
        yandex_uid=yandex_uid,
        depot_id=depot_id,
        region_id=213,
    )

    grocery_cart.set_cart_data(
        cart_id=mocked_order['cart_id'],
        cart_version=mocked_order['cart_version'],
    )
    grocery_cart.set_items(items=[models.GroceryCartItem(item_id=product_id)])

    overlord_catalog.add_product(
        product_id=product_id, category_ids=[category_id],
    )

    await _post_order_event(
        taxi_grocery_marketing, order_id=order_id, status_change=status_change,
    )

    # Check: no increment
    tag_stat.update()
    assert tag_stat.usage_count == 2

    current_tag_stat.update()
    assert current_tag_stat.usage_count == 1

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    if is_adjust_order:
        assert len(events) == 1
        event = events[-1]

        tags = [
            (marketing_tag, 2),
            ('total_orders_count', 0),
            ('total_adjust_orders_count', 0),
        ]

        _check_adjust_event(
            event.payload,
            status_change,
            tags,
            {'yandex_uid': yandex_uid, 'order_id': order_id},
        )
    else:
        assert not events


@pytest.mark.config(GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now(ADD_RULE_TIME)
async def test_status_change_disabled(
        taxi_grocery_marketing,
        pgsql,
        overlord_catalog,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
):
    yandex_uid = 'some_yandex_uid'
    order_id = 'some_order_id'
    status_change = 'canceled'
    depot_id = 'depot_id'
    product_id = 'some_product_id'
    category_id = 'some_category_id'

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    marketing_tag = 'tag_all'

    tag_stat = models.TagStatistic(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=marketing_tag, usage_count=2,
    )
    assert tag_stat.usage_count == 2

    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, kind='marketing',
    )
    await taxi_grocery_marketing.invalidate_caches()

    mocked_order = grocery_orders.add_order(
        order_id=order_id,
        yandex_uid=yandex_uid,
        depot_id=depot_id,
        region_id=131,
    )

    grocery_cart.set_cart_data(
        cart_id=mocked_order['cart_id'],
        cart_version=mocked_order['cart_version'],
    )
    grocery_cart.set_items(items=[models.GroceryCartItem(item_id=product_id)])

    overlord_catalog.add_product(
        product_id=product_id, category_ids=[category_id],
    )

    await _post_order_event(
        taxi_grocery_marketing, order_id=order_id, status_change=status_change,
    )

    # Check: no increment
    tag_stat.update()
    assert tag_stat.usage_count == 2

    # Check: no logbroker event
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert not events


@pytest.mark.config(GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now(ADD_RULE_TIME)
async def test_status_change_disabled_only_adjust(
        taxi_grocery_marketing,
        pgsql,
        overlord_catalog,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
):
    yandex_uid = 'some_yandex_uid'
    order_id = 'some_order_id_123'
    status_change = 'closed'
    depot_id = 'depot_id'
    product_id = 'some_product_id'
    category_id = 'some_category_id'

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    marketing_tag = 'tag_all'

    tag_stat = models.TagStatistic(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=marketing_tag, usage_count=2,
    )
    assert tag_stat.usage_count == 2

    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, kind='marketing',
    )
    await taxi_grocery_marketing.invalidate_caches()

    mocked_order = grocery_orders.add_order(
        order_id=order_id,
        yandex_uid=yandex_uid,
        depot_id=depot_id,
        region_id=155,
    )

    grocery_cart.set_cart_data(
        cart_id=mocked_order['cart_id'],
        cart_version=mocked_order['cart_version'],
    )
    grocery_cart.set_items(items=[models.GroceryCartItem(item_id=product_id)])

    overlord_catalog.add_product(
        product_id=product_id, category_ids=[category_id],
    )

    await _post_order_event(
        taxi_grocery_marketing, order_id=order_id, status_change=status_change,
    )

    # Check: has increment
    tag_stat.update()
    assert tag_stat.usage_count == 3

    # Check: no logbroker event
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert not events


@pytest.mark.config(GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@configs.GROCERY_MARKETING_IS_ADJUST_ORDER
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now(ADD_RULE_TIME)
async def test_status_change_race(
        taxi_grocery_marketing,
        pgsql,
        overlord_catalog,
        grocery_depots,
        grocery_orders,
        grocery_cart,
        processing,
):
    yandex_uid = 'some_yandex_uid'
    order_id_1 = 'some_order_id_1'
    order_id_2 = 'some_order_id_2'
    status_change = 'closed'
    depot_id = 'depot_id'
    product_id = 'some_product_id'
    category_id = 'some_category_id'

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    marketing_tag = 'tag_all'

    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, kind='marketing',
    )
    await taxi_grocery_marketing.invalidate_caches()

    mocked_order = grocery_orders.add_order(
        yandex_uid=yandex_uid, depot_id=depot_id, region_id=213,
    )

    grocery_cart.set_cart_data(
        cart_id=mocked_order['cart_id'],
        cart_version=mocked_order['cart_version'],
    )
    grocery_cart.set_items(items=[models.GroceryCartItem(item_id=product_id)])

    overlord_catalog.add_product(
        product_id=product_id, category_ids=[category_id],
    )

    # Status change for first order
    mocked_order.update(order_id=order_id_1)

    await _post_order_event(
        taxi_grocery_marketing,
        order_id=order_id_1,
        status_change=status_change,
    )

    tag_stat = models.TagStatistic.fetch(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=marketing_tag,
    )

    assert tag_stat.usage_count == 1

    # Check: has logbroker event with usage_count == 1
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 1
    event = events[0]
    _check_adjust_event(
        event.payload,
        status_change,
        [
            (marketing_tag, 1),
            ('total_orders_count', 1),
            ('total_adjust_orders_count', 1),
        ],
        {'yandex_uid': yandex_uid},
    )

    # Status change for second order
    mocked_order.update(order_id=order_id_2)

    await _post_order_event(
        taxi_grocery_marketing,
        order_id=order_id_2,
        status_change=status_change,
    )

    tag_stat = models.TagStatistic.fetch(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=marketing_tag,
    )

    assert tag_stat.usage_count == 2

    # Check: has logbroker event with usage_count == 2
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 2
    event = events[1]
    _check_adjust_event(
        event.payload,
        status_change,
        [
            (marketing_tag, 2),
            ('total_orders_count', 2),
            ('total_adjust_orders_count', 2),
        ],
        {'yandex_uid': yandex_uid},
    )

    # Status change for first order again
    mocked_order.update(order_id=order_id_1)

    await _post_order_event(
        taxi_grocery_marketing,
        order_id=order_id_1,
        status_change=status_change,
    )

    tag_stat = models.TagStatistic.fetch(
        pgsql=pgsql, yandex_uid=yandex_uid, tag=marketing_tag,
    )

    assert tag_stat.usage_count == 2

    # Check: has logbroker event with usage_count == 1
    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )
    assert len(events) == 3
    event = events[2]
    _check_adjust_event(
        event.payload,
        status_change,
        [
            (marketing_tag, 1),
            ('total_orders_count', 1),
            ('total_adjust_orders_count', 1),
        ],
        {'yandex_uid': yandex_uid},
    )


@pytest.mark.config(GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now(ADD_RULE_TIME)
async def test_no_yandex_uid(
        taxi_grocery_marketing,
        pgsql,
        overlord_catalog,
        grocery_depots,
        grocery_orders,
        grocery_cart,
):
    yandex_uid = 'some_yandex_uid'
    order_id = 'some_order_id'
    depot_id = 'depot_1'
    product_id = 'product_1'
    category_id = 'category_1'
    matched_tags = [
        'tag_all',
        'tag_all2',
        'tag_product_1',
        'tag_category_1_product_1_product_2_product_3',
        'tag_depot_1',
        'total_orders_count',
    ]

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    await _add_rules(taxi_grocery_marketing, pgsql)

    mocked_order = grocery_orders.add_order(
        order_id=order_id, depot_id=depot_id, region_id=213,
    )
    del mocked_order['yandex_uid']

    grocery_cart.set_cart_data(
        cart_id=mocked_order['cart_id'],
        cart_version=mocked_order['cart_version'],
    )
    grocery_cart.set_items(items=[models.GroceryCartItem(item_id=product_id)])

    overlord_catalog.add_product(
        product_id=product_id, category_ids=[category_id],
    )

    await _post_order_event(
        taxi_grocery_marketing, order_id=order_id, status_change='closed',
    )

    for tag in matched_tags:
        models.TagStatistic.check_no(
            pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
        )


@pytest.mark.config(GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@pytest.mark.parametrize('status_change', ['closed', 'canceled'])
async def test_eats_order(
        taxi_grocery_marketing, pgsql, grocery_order_log, status_change,
):
    yandex_uid = 'some_yandex_uid'
    order_id = '123123-456456'

    grocery_order_log.check_request(order_id=order_id)
    grocery_order_log.set_yandex_uid(yandex_uid=yandex_uid)

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/order/status-change',
        json={
            'order_id': order_id,
            'status_change': status_change,
            'yandex_uid': yandex_uid,
        },
    )
    assert response.status_code == 200

    assert grocery_order_log.times_order_by_id_called() == 1

    if status_change == 'closed':
        for tag in ['total_orders_count', 'total_adjust_orders_count']:
            tag_stat = models.TagStatistic.fetch(
                pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
            )

            assert tag_stat.usage_count == 1
            assert tag_stat.last_order_ids == [order_id]
    else:
        for tag in ['total_orders_count', 'total_adjust_orders_count']:
            models.TagStatistic.check_no(
                pgsql=pgsql, yandex_uid=yandex_uid, tag=tag,
            )


@pytest.mark.config(GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@pytest.mark.parametrize('status_change', ['closed', 'canceled'])
async def test_eats_order_no_yandex_uid(
        taxi_grocery_marketing, grocery_order_log, pgsql, status_change,
):
    order_id = '123123-456456'

    grocery_order_log.check_request(order_id=order_id)

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/order/status-change',
        json={'order_id': order_id, 'status_change': status_change},
    )

    assert grocery_order_log.times_order_by_id_called() == 1
    assert response.status_code == 409


@pytest.mark.config(GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@pytest.mark.parametrize('status_change', ['closed', 'canceled'])
async def test_eats_order_not_found(
        taxi_grocery_marketing, pgsql, grocery_order_log, status_change,
):
    order_id = '123123-456456'

    grocery_order_log.check_request(order_id=order_id)
    grocery_order_log.set_order_by_id_error(code=404)

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/order/status-change',
        json={'order_id': order_id, 'status_change': status_change},
    )

    assert grocery_order_log.times_order_by_id_called() == 1
    assert response.status_code == 404


@pytest.mark.experiments3(
    name='grocery_marketing_is_adjust_order',
    consumers=['grocery-marketing/common'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'adjust',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'init': {
                                'arg_name': 'delivery_type',
                                'set_elem_type': 'string',
                                'set': ['courier', 'eats_dispatch', 'rover'],
                            },
                        },
                        {
                            'init': {
                                'arg_name': 'has_store',
                                'arg_type': 'int',
                                'value': 1,
                            },
                        },
                    ],
                },
            },
            'value': {'enabled': True},
        },
        {
            'title': 'not adjust',
            'predicate': {'type': 'true'},
            'value': {'enabled': False},
        },
    ],
    is_config=True,
)
@pytest.mark.parametrize(
    'delivery_type, product_ids, grocery_flow_version, is_adjust',
    [
        ('courier', ['123'], 'grocery_flow_v3', True),
        ('rover', ['123'], 'grocery_flow_v3', True),
        ('pickup', ['123'], 'grocery_flow_v3', False),
        ('courier', ['123:st-pa'], 'tristero_flow_v1', False),
        ('courier', ['345', '123:st-pa'], 'grocery_flow_v3', True),
    ],
)
async def test_is_adjust_order(
        taxi_grocery_marketing,
        pgsql,
        grocery_orders,
        grocery_cart,
        overlord_catalog,
        delivery_type,
        product_ids,
        grocery_flow_version,
        is_adjust,
):
    yandex_uid = '123456'
    depot_id = '991234'
    order_id = 'something-grocery'
    status_change = 'closed'
    grocery_cart_products = [
        models.GroceryCartItem(item_id=product_id)
        for product_id in product_ids
    ]

    mocked_order = grocery_orders.add_order(
        order_id=order_id,
        yandex_uid=yandex_uid,
        depot_id=depot_id,
        region_id=213,
        grocery_flow_version=grocery_flow_version,
    )

    grocery_cart.set_cart_data(
        cart_id=mocked_order['cart_id'],
        cart_version=mocked_order['cart_version'],
    )
    grocery_cart.set_delivery_type(delivery_type=delivery_type)
    grocery_cart.set_items(items=grocery_cart_products)

    for product_id in product_ids:
        overlord_catalog.add_product(
            product_id=product_id, category_ids=['some_category_id'],
        )

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/order/status-change',
        json={
            'order_id': order_id,
            'status_change': status_change,
            'yandex_uid': yandex_uid,
        },
    )
    assert response.status_code == 200


@pytest.mark.experiments3(
    name='grocery_marketing_should_send_to_plus_game',
    consumers=['grocery-marketing/common'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'sending enabled',
            'predicate': {
                'type': 'all_of',
                'init': {
                    'predicates': [
                        {
                            'type': 'in_set',
                            'init': {
                                'arg_name': 'delivery_type',
                                'set_elem_type': 'string',
                                'set': ['courier', 'eats_dispatch', 'rover'],
                            },
                        },
                        {
                            'type': 'eq',
                            'init': {
                                'arg_name': 'has_store',
                                'arg_type': 'int',
                                'value': 1,
                            },
                        },
                    ],
                },
            },
            'value': {'enabled': True},
        },
        {
            'title': 'sending disabled',
            'predicate': {'type': 'true'},
            'value': {'enabled': False},
        },
    ],
    is_config=True,
)
@configs.GROCERY_MARKETING_HANDLE_STATUS_CHANGE
@pytest.mark.config(GROCERY_MARKETING_HANDLE_STATUS_CHANGE=True)
@pytest.mark.parametrize(
    'status, stq_times_called', [('canceled', 0), ('closed', 1)],
)
async def test_plus_game(
        taxi_grocery_marketing,
        stq,
        grocery_cart,
        grocery_orders,
        overlord_catalog,
        grocery_depots,
        status,
        stq_times_called,
):
    yandex_uid = '123456'
    depot_id = '991234'
    order_id = 'something-grocery'
    product_ids = ['123']

    mocked_order = grocery_orders.add_order(
        order_id=order_id,
        yandex_uid=yandex_uid,
        depot_id=depot_id,
        region_id=213,
    )

    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    for product_id in product_ids:
        overlord_catalog.add_product(
            product_id=product_id, category_ids=['123'],
        )

    grocery_cart_products = [
        models.GroceryCartItem(item_id=product_id)
        for product_id in product_ids
    ]

    grocery_cart.set_cart_data(
        cart_id=mocked_order['cart_id'],
        cart_version=mocked_order['cart_version'],
    )
    grocery_cart.set_delivery_type(delivery_type='eats_dispatch')
    grocery_cart.set_items(items=grocery_cart_products)

    response = await taxi_grocery_marketing.post(
        '/processing/v1/marketing/v1/event/order/status-change',
        json={
            'order_id': order_id,
            'status_change': status,
            'yandex_uid': yandex_uid,
        },
    )
    assert response.status_code == 200

    assert stq.grocery_marketing_plus_game.times_called == stq_times_called
