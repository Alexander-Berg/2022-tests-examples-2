import pytest

from tests_grocery_cart import common
from tests_grocery_cart import experiments
from tests_grocery_cart import models
from tests_grocery_cart.plugins import keys


async def _add_parcel_product(cart, overlord_catalog, use_update=False):
    item_id = 'item_id:st-pa'
    price = '200'
    overlord_catalog.add_product(product_id=item_id, price=price)

    if use_update:
        await cart.modify({item_id: {'p': price, 'q': 1}})
    else:
        cart.upsert_items(
            [
                models.CartItem(
                    item_id=item_id,
                    price=price,
                    quantity='1',
                    reserved=None,
                    vat=None,
                ),
            ],
        )


async def _add_markdown_product(cart, overlord_catalog, use_update=False):
    item_id = 'item_id:st-md'
    price = '100'
    overlord_catalog.add_product(product_id=item_id, price=price)

    if use_update:
        await cart.modify({item_id: {'p': price, 'q': 1}})
    else:
        cart.upsert_items(
            [
                models.CartItem(
                    item_id=item_id,
                    price=price,
                    quantity='1',
                    reserved=None,
                    vat=None,
                ),
            ],
        )


async def _add_regular_product(cart, overlord_catalog):
    item_id = 'item_id'
    price = '50'

    overlord_catalog.add_product(product_id=item_id, price=price)
    await cart.modify({item_id: {'p': price, 'q': 1}})


@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ENABLED_PICKUP_EXP
@experiments.ENABLED_PARCEL_EXP
@experiments.DELIVERY_TYPES_EXP
@pytest.mark.parametrize(
    'has_markdown, has_parcel, delivery_type, expected_flow_version',
    [
        (1, 1, 'pickup', 'grocery_flow_v1'),  # bad version case
        (0, 1, 'eats_dispatch', 'grocery_flow_v2'),
        (1, 0, 'pickup', 'grocery_flow_v1'),
        (0, 1, 'pickup', 'grocery_flow_v2'),
        (0, 0, 'pickup', 'grocery_flow_v3'),
        (0, 0, 'eats_dispatch', None),
    ],
)
async def test_basic(
        cart,
        overlord_catalog,
        tristero_parcels,
        has_markdown,
        has_parcel,
        delivery_type,
        expected_flow_version,
):
    await _add_regular_product(cart, overlord_catalog)

    response = await cart.retrieve()
    assert set(response['available_delivery_types']) == set(
        ['pickup', 'eats_dispatch'],
    )

    if has_parcel:
        await _add_parcel_product(cart, overlord_catalog, use_update=True)
        response = await cart.retrieve()
        assert set(response['available_delivery_types']) == set(
            ['pickup', 'eats_dispatch'],
        )
        assert response['order_flow_version'] == 'grocery_flow_v2'

    assert len(response['items']) == 1 + has_parcel

    if has_markdown:
        await _add_markdown_product(cart, overlord_catalog, use_update=True)
        response = await cart.retrieve()
        assert response['available_delivery_types'] == ['pickup']

        if expected_flow_version:
            assert response['order_flow_version'] == expected_flow_version
        else:
            assert response['order_flow_version'] == 'eats_core'

    response = await cart.modify({}, delivery_type=delivery_type)
    assert len(response['items']) == 1 + has_parcel + has_markdown

    if has_markdown:
        assert response['available_delivery_types'] == ['pickup']
    else:
        assert set(response['available_delivery_types']) == set(
            ['pickup', 'eats_dispatch'],
        )

    if expected_flow_version:
        assert response['order_flow_version'] == expected_flow_version
    else:
        assert response['order_flow_version'] == 'eats_core'


@experiments.ENABLED_PARCEL_EXP
@experiments.ENABLED_PICKUP_EXP
@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.DELIVERY_TYPES_EXP
async def test_only_parcels(cart, overlord_catalog, tristero_parcels):
    await _add_parcel_product(cart, overlord_catalog, use_update=True)
    await cart.modify({}, delivery_type='pickup')
    response = await cart.retrieve()

    assert set(response['available_delivery_types']) == set(
        ['pickup', 'eats_dispatch'],
    )

    assert response['order_flow_version'] == 'tristero_flow_v1'


@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.ENABLED_PARCEL_EXP
@experiments.DELIVERY_TYPES_EXP
@pytest.mark.parametrize(
    'has_markdown, has_parcel, expected_flow_version',
    [
        (1, 1, 'grocery_flow_v2'),
        (0, 1, 'grocery_flow_v2'),
        (1, 0, None),
        (0, 0, None),
    ],
)
async def test_pickup_unavailable(
        cart,
        overlord_catalog,
        tristero_parcels,
        has_markdown,
        has_parcel,
        expected_flow_version,
):
    """
    Check that flow_version doesn't depend on the presence of markdown
    in the cart when it's not available for user
    """
    await _add_regular_product(cart, overlord_catalog)
    response = await cart.retrieve()

    assert response['available_delivery_types'] == ['eats_dispatch']

    if has_markdown:
        await _add_markdown_product(cart, overlord_catalog)
        response = await cart.retrieve()
        assert response['available_delivery_types'] == []

    assert len(response['items']) == 1 + has_markdown

    if has_parcel:
        await _add_parcel_product(cart, overlord_catalog)
        response = await cart.retrieve()
        assert (
            response['available_delivery_types'] == []
            if has_markdown
            else ['eats_dispatch']
        )

    assert len(response['items']) == 1 + has_parcel + has_markdown

    if not has_markdown:
        response = await cart.modify({}, delivery_type='eats_dispatch')
        assert (
            response['available_delivery_types'] == []
            if has_markdown
            else ['eats_dispatch']
        )

    assert len(response['items']) == 1 + has_parcel + has_markdown

    if expected_flow_version:
        assert response['order_flow_version'] == expected_flow_version
    else:
        assert response['order_flow_version'] == 'eats_core'


@experiments.ENABLED_PICKUP_EXP
@experiments.GROCERY_ORDER_FLOW_VERSION_CONFIG
@experiments.GROCERY_ORDER_CYCLE_ENABLED
@experiments.DELIVERY_TYPES_EXP
@pytest.mark.parametrize(
    'has_parcel, has_markdown, expected_flow_version',
    [
        (1, 1, 'grocery_flow_v1'),
        (0, 1, 'grocery_flow_v1'),
        (1, 0, 'grocery_flow_v3'),
        (0, 0, 'grocery_flow_v3'),
    ],
)
async def test_parcel_unavailable(
        cart,
        overlord_catalog,
        tristero_parcels,
        has_parcel,
        has_markdown,
        expected_flow_version,
):
    """
    Check that flow_version doesn't depend on the presence of parcel
    in the cart when it's not available for user
    """

    await _add_regular_product(cart, overlord_catalog)
    response = await cart.retrieve()
    assert set(response['available_delivery_types']) == set(
        ['pickup', 'eats_dispatch'],
    )

    if has_parcel:
        await _add_parcel_product(cart, overlord_catalog)
        response = await cart.retrieve()
        assert set(response['available_delivery_types']) == set(
            ['pickup', 'eats_dispatch'],
        )

    assert len(response['items']) == 1 + has_parcel

    delivery_types = (
        set(['pickup']) if has_markdown else set(['pickup', 'eats_dispatch'])
    )

    if has_markdown:
        await _add_markdown_product(cart, overlord_catalog)
        response = await cart.retrieve()
        assert set(response['available_delivery_types']) == delivery_types

    assert len(response['items']) == 1 + has_parcel + has_markdown

    response = await cart.modify({}, delivery_type='pickup')
    assert len(response['items']) == 1 + has_parcel + has_markdown

    if expected_flow_version:
        assert response['order_flow_version'] == expected_flow_version
    else:
        assert response['order_flow_version'] == 'eats_core'


@common.GROCERY_ORDER_CYCLE_ENABLED
@pytest.mark.experiments3(
    name='grocery_order_flow_version',
    consumers=['grocery-cart/order-cycle'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'title': 'Matched by country_iso3',
            'predicate': {
                'type': 'eq',
                'init': {
                    'value': 'ISR',
                    'arg_name': 'country_iso3',
                    'arg_type': 'string',
                },
            },
            'value': {'flow_version': 'grocery_flow_v3'},
        },
    ],
    default_value={'flow_version': 'grocery_flow_v1'},
    is_config=True,
)
@pytest.mark.parametrize(
    'country_iso3, expected_flow_version',
    [('ISR', 'grocery_flow_v3'), ('RUS', 'grocery_flow_v1')],
)
async def test_country_iso3_match(
        taxi_grocery_cart,
        cart,
        overlord_catalog,
        country_iso3,
        expected_flow_version,
        grocery_depots,
):
    depot_id = 'my_depot_id'
    item_id = 'item_id'
    price = '50'

    overlord_catalog.add_product(product_id=item_id, price=price)

    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        100,
        legacy_depot_id=depot_id,
        country_iso3=country_iso3,
        location=keys.DEFAULT_DEPOT_LOCATION_OBJ,
    )
    await taxi_grocery_cart.invalidate_caches()

    await cart.modify({item_id: {'p': price, 'q': 1}})

    response = await cart.retrieve()

    assert response['order_flow_version'] == expected_flow_version


@experiments.GROCERY_ORDER_CYCLE_DISABLED
@pytest.mark.parametrize(
    'has_yandex_uid, expected_flow_version',
    [(True, 'eats_payments'), (False, 'eats_core')],
)
async def test_eats_order_flow(
        cart,
        overlord_catalog,
        has_yandex_uid,
        expected_flow_version,
        experiments3,
):
    experiments.grocery_cashback_percent(experiments3)
    experiments.eats_payments_flow(experiments3)

    await _add_regular_product(cart, overlord_catalog)

    headers = common.TAXI_HEADERS

    if not has_yandex_uid:
        headers.pop('X-Yandex-UID')

    response = await cart.retrieve(headers=common.TAXI_HEADERS)

    assert response['order_flow_version'] == expected_flow_version
