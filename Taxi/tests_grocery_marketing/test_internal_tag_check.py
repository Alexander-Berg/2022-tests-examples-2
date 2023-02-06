import datetime

import pytest

from tests_grocery_marketing import common
from tests_grocery_marketing import models
from tests_grocery_marketing import utils


SOME_CART_ID = '00000000-0000-0000-0000-d98013100500'

ADD_RULE_TIME = '2020-01-01T00:00:00+0000'
TAG_CHECK_TIME = '2020-01-03T00:00:00+0000'

DATETIME_NOW = datetime.datetime.strptime(
    '2020-01-05 00:00:00', '%Y-%m-%d %H:%M:%S',
)


async def _add_rules(taxi_grocery_marketing, pgsql):
    await utils.add_matching_rule(taxi_grocery_marketing, pgsql)
    await utils.add_matching_rule(taxi_grocery_marketing, pgsql, suffix='2')
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, product=['product_1'],
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing,
        pgsql,
        group=['category_1'],
        product=['product_1', 'product_2', 'product_3'],
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, group=['category_2'],
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, depot=['depot_1'],
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing, pgsql, depot=['depot_2'], group=['category_1'],
    )
    await utils.add_matching_rule(
        taxi_grocery_marketing,
        pgsql,
        depot=['depot_3'],
        min_cart_cost='100.5',
    )
    await taxi_grocery_marketing.invalidate_caches()


@pytest.mark.parametrize(
    'depot_id, products, tag',
    [
        (
            'depot_1',
            [
                ('product_1', ['category_1', 'category_2'], True),
                ('product_2', ['category_1'], True),
            ],
            'tag_all',
        ),
        (
            'depot_1',
            [
                ('product_1', ['category_1', 'category_2'], True),
                ('product_2', ['category_1'], True),
            ],
            'tag_all2',
        ),
        (
            'depot_1',
            [
                ('product_1', ['category_1', 'category_2'], True),
                ('product_2', ['category_1'], False),
            ],
            'tag_product_1',
        ),
        (
            'depot_1',
            [
                ('product_1', ['category_1', 'category_2'], True),
                ('product_2', ['category_1'], True),
                ('product_3', ['category_2'], False),
                ('product_4', ['category_1'], False),
            ],
            'tag_category_1_product_1_product_2_product_3',
        ),
        (
            'depot_2',
            [
                ('product_1', ['category_2'], False),
                ('product_2', ['category_2'], False),
                ('product_3', ['category_1'], False),
            ],
            'tag_category_1',
        ),
        (
            'depot_1',
            [
                ('product_1', ['category_2'], True),
                ('product_2', ['category_2'], True),
                ('product_3', ['category_1'], True),
            ],
            'tag_depot_1',
        ),
        (
            'depot_1',
            [
                ('product_1', ['category_2'], False),
                ('product_2', ['category_2'], False),
                ('product_3', ['category_1'], False),
            ],
            'tag_depot_2_category_1',
        ),
        (
            'depot_2',
            [
                ('product_1', ['category_2'], False),
                ('product_2', ['category_2'], False),
                ('product_3', ['category_1'], True),
            ],
            'tag_depot_2_category_1',
        ),
    ],
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now(ADD_RULE_TIME)
async def test_basic(
        taxi_grocery_marketing,
        pgsql,
        grocery_cart,
        overlord_catalog,
        grocery_depots,
        depot_id,
        products,
        tag,
):
    kind = 'promocode'

    cart_version = 1

    grocery_cart.set_cart_data(cart_id=SOME_CART_ID, cart_version=cart_version)
    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    for (product_id, category_ids, _) in products:
        overlord_catalog.add_product(
            product_id=product_id, category_ids=category_ids,
        )

    grocery_cart.set_items(
        items=[
            models.GroceryCartItem(item_id=product_id)
            for (product_id, _, _) in products
        ],
    )

    await _add_rules(taxi_grocery_marketing, pgsql)

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v1/tag/check',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': cart_version,
            'depot_id': depot_id,
            'kind': kind,
            'tag': tag,
            'request_time': TAG_CHECK_TIME,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200

    assert response.json()['products'] == [
        product_id for (product_id, _, matched) in products if matched
    ]


@pytest.mark.parametrize(
    'depot_id, products, tag, min_cart_cost',
    [
        (
            'depot_3',
            [
                ('product_1', ['category_1', 'category_2'], True),
                ('product_2', ['category_1'], True),
            ],
            'tag_depot_3_100.5',
            '100.5',
        ),
        (
            'depot_1',
            [
                ('product_1', ['category_1', 'category_2'], True),
                ('product_2', ['category_1'], True),
            ],
            'tag_all',
            None,
        ),
    ],
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now(ADD_RULE_TIME)
async def test_min_cart_cost(
        taxi_grocery_marketing,
        pgsql,
        grocery_cart,
        overlord_catalog,
        grocery_depots,
        depot_id,
        products,
        tag,
        min_cart_cost,
):
    kind = 'promocode'

    cart_version = 1

    grocery_cart.set_cart_data(cart_id=SOME_CART_ID, cart_version=cart_version)
    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    for (product_id, category_ids, _) in products:
        overlord_catalog.add_product(
            product_id=product_id, category_ids=category_ids,
        )

    grocery_cart.set_items(
        items=[
            models.GroceryCartItem(item_id=product_id)
            for (product_id, _, _) in products
        ],
    )

    await _add_rules(taxi_grocery_marketing, pgsql)

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v1/tag/check',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': cart_version,
            'depot_id': depot_id,
            'kind': kind,
            'tag': tag,
            'request_time': TAG_CHECK_TIME,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200

    assert response.json()['products'] == [
        product_id for (product_id, _, matched) in products if matched
    ]

    if min_cart_cost is not None:
        assert response.json()['min_cart_cost'] == min_cart_cost
    else:
        assert 'min_cart_cost' not in response.json()


@pytest.mark.parametrize(
    'depot_id, products, tag, usage_count',
    [
        (
            'depot_3',
            [
                ('product_1', ['category_1', 'category_2'], True),
                ('product_2', ['category_1'], True),
            ],
            'tag_depot_3_100.5',
            4,
        ),
        (
            'depot_1',
            [
                ('product_1', ['category_1', 'category_2'], True),
                ('product_2', ['category_1'], True),
            ],
            'tag_all',
            None,
        ),
    ],
)
@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now(ADD_RULE_TIME)
async def test_usage_count(
        taxi_grocery_marketing,
        pgsql,
        grocery_cart,
        overlord_catalog,
        grocery_depots,
        depot_id,
        products,
        tag,
        usage_count,
):
    kind = 'promocode'

    cart_version = 1

    grocery_cart.set_cart_data(cart_id=SOME_CART_ID, cart_version=cart_version)
    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    for (product_id, category_ids, _) in products:
        overlord_catalog.add_product(
            product_id=product_id, category_ids=category_ids,
        )

    grocery_cart.set_items(
        items=[
            models.GroceryCartItem(item_id=product_id)
            for (product_id, _, _) in products
        ],
    )

    await _add_rules(taxi_grocery_marketing, pgsql)

    if usage_count is not None:
        models.TagStatistic(
            pgsql=pgsql,
            yandex_uid=common.YANDEX_UID,
            tag=tag,
            usage_count=usage_count,
        )
    else:
        models.TagStatistic(
            pgsql=pgsql,
            yandex_uid=common.YANDEX_UID + '123',
            tag=tag,
            usage_count=usage_count,
        )

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v1/tag/check',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': cart_version,
            'depot_id': depot_id,
            'kind': kind,
            'tag': tag,
            'request_time': TAG_CHECK_TIME,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200

    assert response.json()['products'] == [
        product_id for (product_id, _, matched) in products if matched
    ]

    if usage_count is not None:
        assert response.json()['usage_count'] == usage_count
    else:
        assert response.json()['usage_count'] == 0


@pytest.mark.pgsql('grocery_marketing', files=['init.sql'])
@pytest.mark.now(ADD_RULE_TIME)
async def test_no_cart_version(
        taxi_grocery_marketing,
        pgsql,
        grocery_cart,
        overlord_catalog,
        grocery_depots,
):
    kind = 'promocode'

    cart_version = 1
    depot_id = 'some_depot'
    product_id = 'product_id'
    category_ids = ['category_1']
    tag = 'tag_all'

    grocery_cart.set_cart_data(cart_id=SOME_CART_ID, cart_version=cart_version)
    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)

    overlord_catalog.add_product(
        product_id=product_id, category_ids=category_ids,
    )

    grocery_cart.set_items(items=[models.GroceryCartItem(item_id=product_id)])

    await _add_rules(taxi_grocery_marketing, pgsql)

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v1/tag/check',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': cart_version + 1,
            'depot_id': depot_id,
            'kind': kind,
            'tag': tag,
            'request_time': TAG_CHECK_TIME,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 404


async def test_empty(
        taxi_grocery_marketing,
        pgsql,
        grocery_cart,
        overlord_catalog,
        grocery_depots,
):
    depot_id = '12345'
    tag = 'some_tag'
    kind = 'promocode'
    cart_version = 1
    product_id = 'some_product_id'
    category_ids = ['category_1', 'category_2']

    grocery_cart.set_cart_data(cart_id=SOME_CART_ID, cart_version=cart_version)
    grocery_depots.add_depot(depot_test_id=1, legacy_depot_id=depot_id)
    overlord_catalog.add_product(
        product_id=product_id, category_ids=category_ids,
    )
    grocery_cart.set_items(items=[models.GroceryCartItem(item_id=product_id)])

    response = await taxi_grocery_marketing.post(
        '/internal/v1/marketing/v1/tag/check',
        json={
            'cart_id': SOME_CART_ID,
            'cart_version': cart_version,
            'depot_id': depot_id,
            'kind': kind,
            'tag': tag,
            'request_time': TAG_CHECK_TIME,
        },
        headers=common.DEFAULT_USER_HEADERS,
    )

    assert response.status_code == 200
    assert not response.json()['products']
