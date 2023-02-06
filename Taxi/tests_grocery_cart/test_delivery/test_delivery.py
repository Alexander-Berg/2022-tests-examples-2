import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart.plugins import keys


def _handle_paid_delivery(enabled):
    return pytest.mark.experiments3(
        name='lavka_handle_paid_delivery',
        consumers=['grocery-cart'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': enabled},
            },
        ],
        default_value={'enabled': enabled},
        is_config=True,
    )


# тест проверяет, что для определения стоимости доставки используется цена
# корзины со скидками
@pytest.mark.parametrize(
    'price, discount_price, delivery_cost', [(399, 300, 200), (400, 350, 200)],
)
@pytest.mark.pgsql('grocery_cart', files=['taxi_one_item.sql'])
@pytest.mark.now(keys.TS_NOW)
async def test_delivery_cost(
        cart,
        price,
        discount_price,
        delivery_cost,
        overlord_catalog,
        grocery_p13n,
        offers,
        experiments3,
        grocery_surge,
        now,
):
    product_id = 'some_product_id'
    cart_price_threshold = 400

    actual_delivery = {
        'cost': '200',
        'next_threshold': str(cart_price_threshold),
        'next_cost': '100',
    }
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        offer_time=keys.TS_NOW,
        depot_id='0',
    )
    common.add_delivery_conditions(experiments3, actual_delivery)

    overlord_catalog.add_product(product_id=product_id, price=str(price))
    grocery_p13n.add_modifier(
        product_id=product_id, value=str(int(price) - int(discount_price)),
    )

    await cart.modify({product_id: {'q': 1, 'p': str(discount_price)}})

    response_json = await cart.retrieve()

    assert response_json['order_conditions'] == {
        'delivery_cost': str(delivery_cost),
        'delivery_cost_template': f'{delivery_cost} $SIGN$$CURRENCY$',
        'minimum_order_price': '0',
        'minimum_order_price_template': '0 $SIGN$$CURRENCY$',
    }
    if discount_price < cart_price_threshold:
        reqs = response_json['requirements']
        assert reqs is not None
        assert reqs['sum_to_next_delivery'] == str(
            cart_price_threshold - discount_price,
        )
    assert (
        response_json['total_price_no_delivery_template']
        == f'{discount_price} $SIGN$$CURRENCY$'
    )
    assert (
        response_json['total_price_template']
        == f'{discount_price + delivery_cost} $SIGN$$CURRENCY$'
    )


@_handle_paid_delivery(False)
@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.pgsql('grocery_cart', files=['taxi_one_item.sql'])
async def test_our_order_cycle_delivery_cost(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
        grocery_depots,
):
    product_id = 'some_product_id'
    price = 100
    cart_price_threshold = 400
    delivery_cost = 200

    overlord_catalog.add_product(product_id=product_id, price=str(price))
    await taxi_grocery_cart.invalidate_caches()

    actual_delivery = {
        'cost': str(delivery_cost),
        'next_threshold': str(cart_price_threshold),
        'next_cost': '100',
    }
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        delivery=actual_delivery,
    )

    await cart.modify({product_id: {'q': 1, 'p': str(price)}})

    response_json = await cart.retrieve()

    assert response_json['order_conditions'] == {
        'delivery_cost': '0',
        'delivery_cost_template': '0 $SIGN$$CURRENCY$',
    }
    assert not response_json['is_surge']


@_handle_paid_delivery(True)
@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.pgsql('grocery_cart', files=['taxi_one_item.sql'])
@pytest.mark.now(keys.TS_NOW)
async def test_our_order_cycle_delivery_cost_exp_no_disable(
        cart,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
        grocery_depots,
        grocery_marketing,
):
    product_id = 'some_product_id'
    price = 100
    cart_price_threshold = 400
    delivery_cost = 200
    depot_id = '12345'

    overlord_catalog.add_product(product_id=product_id, price=str(price))
    overlord_catalog.add_depot(legacy_depot_id=depot_id)
    grocery_marketing.add_user_tag(
        tag_name='total_orders_count', usage_count=2, user_id='some_uid',
    )
    grocery_depots.add_depot(int(depot_id), auto_add_zone=False)

    actual_delivery = {
        'cost': str(delivery_cost),
        'next_threshold': str(cart_price_threshold),
        'next_cost': '100',
    }

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        depot_id=depot_id,
    )
    common.add_delivery_conditions(
        experiments3, actual_delivery, surge=True, enable_newbies=True,
    )

    await cart.modify({product_id: {'q': 1, 'p': str(price)}})

    response_json = await cart.retrieve()

    assert response_json['order_conditions'] == {
        'delivery_cost': str(delivery_cost),
        'delivery_cost_template': f'{delivery_cost} $SIGN$$CURRENCY$',
        'minimum_order_price': '0',
        'minimum_order_price_template': '0 $SIGN$$CURRENCY$',
    }
    assert response_json['is_surge']


@_handle_paid_delivery(True)
@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.pgsql('grocery_cart', files=['taxi_one_item.sql'])
@pytest.mark.now(keys.TS_NOW)
@pytest.mark.parametrize('orders_count', [0, 2])
async def test_our_order_cycle_free_newbie_delivery(
        cart,
        overlord_catalog,
        offers,
        experiments3,
        grocery_surge,
        grocery_depots,
        grocery_marketing,
        orders_count,
):
    product_id = 'some_product_id'
    price = 100
    cart_price_threshold = 400
    delivery_cost = 200
    depot_id = '12345'

    overlord_catalog.add_product(product_id=product_id, price=str(price))
    overlord_catalog.add_depot(legacy_depot_id=depot_id)
    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=orders_count,
        user_id='some_uid',
    )
    grocery_depots.add_depot(int(depot_id), auto_add_zone=False)

    actual_delivery = {
        'cost': str(delivery_cost),
        'next_threshold': str(cart_price_threshold),
        'next_cost': '100',
    }

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        depot_id=depot_id,
    )
    common.add_delivery_conditions(
        experiments3, actual_delivery, surge=True, enable_newbies=True,
    )

    await cart.modify({product_id: {'q': 1, 'p': str(price)}})

    response_json = await cart.retrieve()

    if orders_count == 0:
        assert response_json['order_conditions'] == {
            'delivery_cost': '0',
            'delivery_cost_template': '0 $SIGN$$CURRENCY$',
            'minimum_order_price': '0',
            'minimum_order_price_template': '0 $SIGN$$CURRENCY$',
        }
        assert not response_json['is_surge']
    else:
        assert response_json['order_conditions'] == {
            'delivery_cost': str(delivery_cost),
            'delivery_cost_template': f'{delivery_cost} $SIGN$$CURRENCY$',
            'minimum_order_price': '0',
            'minimum_order_price_template': '0 $SIGN$$CURRENCY$',
        }
        assert response_json['is_surge']
