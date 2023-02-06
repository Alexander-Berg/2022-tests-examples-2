# pylint: disable=too-many-lines
import decimal
import typing
import uuid

import pytest

from tests_grocery_cart import models
from tests_grocery_cart.plugins import keys

# pylint: disable=invalid-name
Decimal = decimal.Decimal

PRICE = '150'
QUANTITY = '12'
DEFAULT_ITEM = {'p': PRICE, 'q': QUANTITY}


@pytest.fixture(name='create_shared_cart')
async def _create_shared_cart(
        cart, grocery_p13n, overlord_catalog, fetch_items,
):
    async def _do(items, status_code=200):
        await cart.init(items)

        return await cart.create_shared(status_code=status_code)

    return _do


@pytest.fixture(name='retrieve_shared_cart')
async def _retrieve_shared_cart(cart, create_shared_cart, taxi_grocery_cart):
    async def _do(items):
        response = await create_shared_cart(items)
        shared_cart_id = response['shared_cart_id']

        response = await taxi_grocery_cart.post(
            '/lavka/v1/cart/v1/shared/retrieve',
            json={
                'shared_cart_id': shared_cart_id,
                'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
            },
        )
        return response.json()

    return _do


async def test_create_pg(create_shared_cart, fetch_items):
    item_1 = _get_item('item-1')
    item_2 = _get_item('item-2', cashback='10')

    response = await create_shared_cart(
        {item_1['item_id']: item_1, item_2['item_id']: item_2},
    )

    shared_cart_id = response['shared_cart_id']
    assert shared_cart_id is not None

    items = fetch_items(shared_cart_id)
    assert len(items) == 2

    _check_pg_items(items, item_1)
    _check_pg_items(items, item_2)


async def test_create_not_found(cart):
    await cart.create_shared(cart_id=str(uuid.uuid4()), status_code=404)


async def test_share_empty_cart(create_shared_cart):
    response = await create_shared_cart(items={}, status_code=400)
    assert response['code'] == 'EMPTY_CART'


async def test_retrieve(retrieve_shared_cart):
    item_1 = _get_item('item-1')
    item_2 = _get_item('item-2', cashback='10')

    response = await retrieve_shared_cart(
        {item_1['item_id']: item_1, item_2['item_id']: item_2},
    )

    items = response['items']
    assert len(items) == 2

    _check_response_items(items, item_1)
    _check_response_items(items, item_2)


async def test_deleted_before_checkout(cart, taxi_grocery_cart):
    item_1 = _get_item('item-1')
    item_2 = _get_item('item-2')

    items = {item_1['item_id']: item_1, item_2['item_id']: item_2}
    await cart.init(items)
    await cart.modify({item_1['item_id']: {'p': 345, 'q': 0}})
    response = await cart.create_shared()

    shared_cart_id = response['shared_cart_id']

    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/shared/retrieve',
        json={
            'shared_cart_id': shared_cart_id,
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        },
    )

    items = response.json()['items']
    assert len(items) == 1

    _check_response_items(items, item_2)


async def test_retrieve_not_found(taxi_grocery_cart):
    response = await taxi_grocery_cart.post(
        '/lavka/v1/cart/v1/shared/retrieve',
        json={
            'shared_cart_id': str(uuid.uuid4()),
            'position': {'location': keys.DEFAULT_DEPOT_LOCATION},
        },
    )
    return response.status_code == 404


def _get_item(item_id, cashback=None):
    return {**DEFAULT_ITEM, 'item_id': item_id, 'cashback': cashback}


def _check_pg_items(pg_items: typing.List[models.CartItem], request_item):
    item_id = request_item['item_id']

    for pg_item in pg_items:
        if pg_item.item_id == item_id:
            _check_pg_item(pg_item, request_item)
            return

    assert False, f'Cannot find {item_id} in pg'


def _check_pg_item(pg_item: models.CartItem, request_item):
    price = request_item['p']
    quantity = request_item['q']
    cashback = request_item.get('cashback', None)

    assert Decimal(pg_item.price) == Decimal(price)
    assert Decimal(pg_item.quantity) == Decimal(quantity)
    if cashback is not None:
        assert pg_item.cashback is not None
        assert Decimal(pg_item.cashback) == Decimal(cashback)


def _check_response_items(response_items, request_item):
    item_id = request_item['item_id']

    for response_item in response_items:
        if response_item['id'] == item_id:
            _check_response_item(response_item, request_item)
            return

    assert False, f'Cannot find {item_id} in response'


def _check_response_item(response_item, request_item):
    price = request_item['p']
    to_check = {
        'currency': 'RUB',
        'id': request_item['item_id'],
        'price': str(price),
        'price_template': f'{price} $SIGN$$CURRENCY$',
        'quantity': str(request_item['q']),
    }

    if request_item.get('cashback', None) is not None:
        to_check['cashback'] = request_item['cashback']

    assert response_item == to_check
