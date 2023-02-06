import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments

BASIC_HEADERS = {**common.TAXI_HEADERS, 'X-Yandex-Uid': '8484'}


@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.GROCERY_PARCEL_PAID_DELIVERY
@experiments.ENABLED_PARCEL_EXP
@pytest.mark.parametrize(
    'request_kind', [None, 'on_demand', 'hour_slot', 'wide_slot'],
)
@pytest.mark.parametrize('orders_count', [0, 2])
async def test_parcels_delivery_cost(
        cart,
        overlord_catalog,
        tristero_parcels,
        offers,
        experiments3,
        grocery_surge,
        request_kind,
        grocery_marketing,
        orders_count,
):
    """ Delivery cost of an order with a parcel should be zero if
    request_kind is not wide_slot. If requsest_kind is not in respone,
    consider request_kind as on_demand. If request kind is wide_slot,
    paid delivery should apply even if customer has no previous orders."""
    delivery = {'cost': '200', 'next_threshold': '400', 'next_cost': '100'}
    minimum_order = '0'
    paid_delivery = request_kind in ['wide_slot']
    common.create_offer(
        offers, experiments3, grocery_surge, offer_id=cart.offer_id,
    )
    grocery_marketing.add_user_tag(
        tag_name='total_orders_count',
        usage_count=orders_count,
        user_id='some_uid',
    )
    common.add_delivery_conditions(
        experiments3, delivery, surge=True, enable_newbies=True,
    )

    await _setup_products_and_cart(
        cart,
        overlord_catalog,
        tristero_parcels,
        request_kind=request_kind,
        add_product=False,
    )

    response_json = await cart.retrieve(headers=BASIC_HEADERS)

    cost_str = '200' if paid_delivery else '0'
    expected_conditions = {
        'delivery_cost': cost_str,
        'delivery_cost_template': f'{cost_str} $SIGN$$CURRENCY$',
    }
    if paid_delivery:
        expected_conditions['minimum_order_price'] = minimum_order
        expected_conditions[
            'minimum_order_price_template'
        ] = f'{minimum_order} $SIGN$$CURRENCY$'

    assert overlord_catalog.times_called() == 1
    assert tristero_parcels.times_called() == 1
    assert response_json['available_for_checkout'] is True
    assert response_json['order_conditions'] == expected_conditions
    if request_kind in [None, 'on_demand']:
        assert not response_json['is_surge']


@pytest.mark.parametrize(
    'request_kind', [None, 'on_demand', 'hour_slot', 'wide_slot'],
)
@experiments.ENABLED_PARCEL_EXP
@experiments.GROCERY_PARCEL_PAID_DELIVERY
@common.GROCERY_ORDER_CYCLE_ENABLED
async def test_parcels_minimum_order(
        cart,
        overlord_catalog,
        tristero_parcels,
        offers,
        experiments3,
        grocery_surge,
        request_kind,
):
    paid_delivery = request_kind in ['wide_slot']

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        minimum_order='10000',
        delivery={'cost': '0', 'next_cost': '0', 'next_threshold': '99999'},
        depot_id='12',
    )
    await _setup_products_and_cart(
        cart, overlord_catalog, tristero_parcels, request_kind=request_kind,
    )

    response_json = await cart.retrieve(headers=BASIC_HEADERS)

    assert overlord_catalog.times_called() == 1
    assert tristero_parcels.times_called() == 1
    if paid_delivery:
        assert response_json['available_for_checkout'] is False
        assert response_json['checkout_unavailable_reason'] == 'minimum-price'
    else:
        assert 'minimum_order_price' not in response_json['requirements']
        assert not response_json['is_surge']


@pytest.mark.parametrize(
    'request_kind', [None, 'on_demand', 'hour_slot', 'wide_slot'],
)
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG_PROD
@experiments.ENABLED_PARCEL_EXP
@experiments.GROCERY_PARCEL_PAID_DELIVERY
async def test_parcels_order_cycle(
        cart,
        overlord_catalog,
        tristero_parcels,
        offers,
        experiments3,
        grocery_surge,
        request_kind,
):

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        minimum_order='100',
        delivery={'cost': '200', 'next_cost': '400', 'next_threshold': '1000'},
        depot_id='12',
    )
    await _setup_products_and_cart(
        cart,
        overlord_catalog,
        tristero_parcels,
        request_kind=request_kind,
        add_product=False,
    )
    expected_flow_version = (
        'tristero_flow_v1'
        if request_kind in [None, 'on_demand', 'hour_slot']
        else 'grocery_flow_v1'  # fallback flow version
    )
    response_json = await cart.retrieve(headers=BASIC_HEADERS)

    assert overlord_catalog.times_called() == 1
    assert tristero_parcels.times_called() == 1
    assert response_json['order_flow_version'] == expected_flow_version


@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ENABLED_PARCEL_EXP
async def test_parcels_in_response(cart, overlord_catalog, tristero_parcels):
    parcels_suffix = ':st-pa'

    parcel_product_id = 'parcel_product_id' + parcels_suffix
    parcel_from_another_depot_id = 'parcel_product_id_2' + parcels_suffix

    regular_product_id = 'just_a_product_id'
    regular_product_price = 123

    tristero_parcels.add_parcel(parcel_id=parcel_product_id)
    tristero_parcels.add_parcel(
        parcel_id=parcel_from_another_depot_id,
        depot_id='some_very_specific_id_1723',
    )
    overlord_catalog.add_product(
        product_id=regular_product_id, price=regular_product_price,
    )

    await cart.modify(
        {
            parcel_product_id: {'q': 1, 'p': 0},
            parcel_from_another_depot_id: {'q': 1, 'p': 0},
            regular_product_id: {'q': 1, 'p': regular_product_price},
        },
        headers=BASIC_HEADERS,
    )
    overlord_catalog.flush()
    tristero_parcels.flush()

    response_json = await cart.retrieve(headers=BASIC_HEADERS)

    assert overlord_catalog.times_called() == 1
    assert tristero_parcels.times_called() == 1

    assert len(response_json['items']) == 3

    for item in response_json['items']:
        if item['id'] == regular_product_id:
            regular_item = item
        elif item['id'] == parcel_product_id:
            parcel_item = item
        elif item['id'] == parcel_from_another_depot_id:
            parcel_item_unavailable = item

    assert parcel_item['price'] == '0'
    assert int(parcel_item['quantity_limit']) == 1
    assert parcel_item['title'] == f'title for {parcel_product_id}'

    assert regular_item['price'] == str(regular_product_price)
    assert regular_item['title'] == f'title for {regular_product_id}'

    assert parcel_item_unavailable['price'] == '0'
    assert int(parcel_item_unavailable['quantity_limit']) == 0
    assert response_json['checkout_unavailable_reason'] == 'parcel-wrong-depot'


async def _setup_products_and_cart(
        cart,
        overlord_catalog,
        tristero_parcels,
        can_left_at_door=True,
        add_product=True,
        request_kind=None,
):
    parcels_suffix = ':st-pa'

    parcel_product_id = 'parcel_product_id' + parcels_suffix

    regular_product_id = 'just_a_product_id'
    regular_product_price = 123
    cart_modify_request = {parcel_product_id: {'q': 1, 'p': 0}}

    tristero_parcels.add_parcel(
        parcel_id=parcel_product_id,
        can_left_at_door=can_left_at_door,
        request_kind=request_kind,
    )
    if add_product:
        overlord_catalog.add_product(
            product_id=regular_product_id, price=regular_product_price,
        )
        cart_modify_request[regular_product_id] = {
            'q': 1,
            'p': regular_product_price,
        }

    await cart.modify(cart_modify_request, headers=BASIC_HEADERS)

    overlord_catalog.flush()
    tristero_parcels.flush()


@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ENABLED_PARCEL_EXP
@pytest.mark.parametrize(
    'parcel_status', ['ordered', 'order_cancelled', 'delivering', 'delivered'],
)
@pytest.mark.parametrize('check_statuses', [True, False])
async def test_parcels_already_ordered(
        cart,
        overlord_catalog,
        tristero_parcels,
        parcel_status,
        check_statuses,
        taxi_config,
):
    await _setup_products_and_cart(cart, overlord_catalog, tristero_parcels)
    taxi_config.set_values(
        {'GROCERY_CART_CHECK_PARCEL_STATUS': check_statuses},
    )

    await cart.invalidate_caches()

    parcel_product_id = 'parcel_product_id:st-pa'

    tristero_parcels.add_parcel(
        parcel_id=parcel_product_id, status=parcel_status,
    )

    response = await cart.retrieve(headers=BASIC_HEADERS)

    assert overlord_catalog.times_called() == 1
    assert tristero_parcels.times_called() == 1

    if check_statuses:
        assert (
            response['checkout_unavailable_reason'] == 'parcel-already-ordered'
        )
    else:
        assert 'checkout_unavailable_reason' not in response

    response = await cart.checkout(headers=BASIC_HEADERS)

    if check_statuses:
        assert (
            response['checkout_unavailable_reason'] == 'parcel-already-ordered'
        )
    else:
        assert 'checkout_unavailable_reason' not in response

    assert overlord_catalog.times_called() == 2
    assert tristero_parcels.times_called() == 2


@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.parametrize(
    'config_enabled,checkout_unavailable_reason',
    [(True, None), (False, 'parcel-already-ordered')],
)
async def test_parcels_retrieve_hack(
        cart,
        overlord_catalog,
        tristero_parcels,
        taxi_config,
        config_enabled,
        checkout_unavailable_reason,
        experiments3,
):
    experiments3.add_config(
        name='lavka_parcel',
        consumers=['internal:overlord-catalog:special-categories'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {'type': 'true'},
                'value': {'enabled': config_enabled},
            },
        ],
        default_value={'enabled': False},
    )
    await _setup_products_and_cart(cart, overlord_catalog, tristero_parcels)

    await cart.invalidate_caches()

    parcel_product_id = 'parcel_product_id:st-pa'

    tristero_parcels.add_parcel(parcel_id=parcel_product_id, status='in_depot')

    response = await cart.retrieve(headers=BASIC_HEADERS)
    assert ('checkout_unavailable_reason' in response) == (
        checkout_unavailable_reason is not None
    )
    if checkout_unavailable_reason is not None:
        assert (
            response['checkout_unavailable_reason']
            == checkout_unavailable_reason
        )

    assert overlord_catalog.times_called() == 1
    assert tristero_parcels.times_called() == 1


# Test localizations for tristero parcels.
@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ENABLED_PARCEL_EXP
@pytest.mark.config(
    TRISTERO_PARCELS_VENDORS_SETTINGS={
        'market': {
            'image-parcel': 'market-image-parcel.jpg',
            'image-informer': 'market-image-informer.jpg',
        },
        'few_vendors': {'image-informer': 'few_vendors-image-informer.jpg'},
    },
)
@pytest.mark.parametrize(
    'parcels, bottom_text, informer_image, informer_title, informer_text',
    [
        pytest.param(
            [('market', 1, 1)],
            'Заказ уже в корзине',
            'market-image-informer.jpg',
            'Ваш заказ из Яндекс.Маркета',
            'Ваш заказ из Яндекс.Маркета уже в корзине.',
            id='ONE_VENDOR_ONE_PARCEL',
        ),
        pytest.param(
            [('market', 1, 1), ('market', 2, 2), ('market', 2, 3)],
            '2 заказа уже в корзине',
            'market-image-informer.jpg',
            'Ваши заказы из Яндекс.Маркета',
            '2 ваших заказа из Яндекс.Маркета уже в корзине.',
            id='ONE_VENDOR_FEW_PARCELS',
        ),
        pytest.param(
            [('market', 1, 1), ('d-mir', 2, 2), ('d-mir', 2, 3)],
            '2 заказа уже в корзине',
            'few_vendors-image-informer.jpg',
            'Ваши заказы',
            '2 ваших заказа из Детский мир, Яндекс.Маркет уже в корзине.',
            id='FEW_VENDORS_FEW_PARCELS',
        ),
    ],
)
async def test_parcels_l10n(
        cart,
        overlord_catalog,
        tristero_parcels,
        parcels,
        bottom_text,
        informer_image,
        informer_title,
        informer_text,
):
    # prepare parcels
    order_prefix = '00000000-0000-0000-0000-00000000000'
    parcels_suffix = ':st-pa'
    cart_modifier = {}
    for (vendor_name, order_id, parcel_id) in parcels:
        parcel_product_id = str(parcel_id) + parcels_suffix
        tristero_parcels.add_parcel(
            vendor=vendor_name,
            order_id=order_prefix + str(order_id),
            parcel_id=parcel_product_id,
        )
        cart_modifier[parcel_product_id] = {'q': 1, 'p': 0}

    # prepare cart
    await cart.modify(cart_modifier, headers=BASIC_HEADERS)

    response_json = await cart.retrieve(headers=BASIC_HEADERS)
    assert response_json['l10n']['parcels.orders_in_cart'] == bottom_text
    assert response_json['l10n']['parcels.informer.image'] == informer_image
    assert response_json['l10n']['parcels.informer.title'] == informer_title
    assert response_json['l10n']['parcels.informer.text'] == informer_text
    assert (
        response_json['l10n']['parcels.informer.button.checkout']
        == 'Вызвать курьера'
    )
    assert (
        response_json['l10n']['parcels.informer.button.catalog']
        == 'Добавить кое-что'
    )


@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ENABLED_PARCEL_EXP
@pytest.mark.parametrize(
    'can_left_at_door, restrictions',
    [(True, []), (False, ['parcel_too_expensive'])],
)
async def test_parcels_left_at_door(
        cart,
        overlord_catalog,
        tristero_parcels,
        offers,
        experiments3,
        grocery_surge,
        can_left_at_door,
        restrictions,
):
    """ should return parcel_too_expensive restriction if
    parcel could not be left at door """
    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        minimum_order='10000',
        delivery={'cost': '0', 'next_cost': '0', 'next_threshold': '99999'},
    )
    await _setup_products_and_cart(
        cart,
        overlord_catalog,
        tristero_parcels,
        can_left_at_door=can_left_at_door,
    )

    response_json = await cart.retrieve(headers=BASIC_HEADERS)
    for item in response_json['items']:
        if 'st-pa' in item['id']:
            assert item['restrictions'] == restrictions


@common.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ENABLED_PARCEL_EXP
async def test_parcels_send_flag_p13n(
        cart,
        overlord_catalog,
        tristero_parcels,
        grocery_p13n,
        offers,
        experiments3,
        grocery_surge,
):
    """Sends flag to p13n/v1/discount-modifiers if has parcels in cart"""

    grocery_p13n.set_modifiers_request_check(
        on_modifiers_request=lambda headers, json: json['has_parcels'],
    )

    common.create_offer(
        offers,
        experiments3,
        grocery_surge,
        offer_id=cart.offer_id,
        minimum_order='100',
        delivery={'cost': '200', 'next_cost': '400', 'next_threshold': '1000'},
        depot_id='12',
    )

    await _setup_products_and_cart(
        cart, overlord_catalog, tristero_parcels, add_product=False,
    )

    await cart.retrieve(headers=BASIC_HEADERS)

    assert overlord_catalog.times_called() == 1
    assert tristero_parcels.times_called() == 1
    assert grocery_p13n.discount_modifiers_times_called == 2
