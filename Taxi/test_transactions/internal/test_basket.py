import decimal
from typing import Dict
from typing import Optional

import pytest

from transactions.internal import basket

CompositeBasket = basket.CompositeBasket


def _basket(sum_items: Dict[str, str]) -> basket.Basket:
    return basket.Basket.make_from_sum_items(sum_items)


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'transaction_sum, to_resize, e_new_transaction_basket, e_left_to_resize',
    [
        (
            {'ride': '100', 'tips': '10'},
            _basket({'ride': '100', 'burgers': '50'}),
            # It is important, that 0 is preserved,
            # otherwise we wont update it
            _basket({'ride': '0', 'tips': '10'}),
            _basket({'burgers': '50'}),
        ),
        (
            {'ride': '100', 'tips': '10'},
            _basket({'ride': '120', 'tips': '6'}),
            # It is important, that 0 is preserved,
            # otherwise we wont update it
            _basket({'ride': '0', 'tips': '4'}),
            _basket({'ride': '20'}),
        ),
        (
            {'ride': '100', 'tips': '10'},
            _basket({'burgers': '120', 'milk': '6'}),
            None,
            _basket({'burgers': '120', 'milk': '6'}),
        ),
    ],
)
def test_calc_transaction_resized(
        transaction_sum, to_resize, e_new_transaction_basket, e_left_to_resize,
):
    transaction = {'sum': transaction_sum}
    (new_transaction_basket, left_to_resize) = basket.calc_transaction_resized(
        transaction, to_resize,
    )
    if e_new_transaction_basket is None:
        assert new_transaction_basket is None
    else:
        assert not e_new_transaction_basket - new_transaction_basket
    assert not e_left_to_resize - left_to_resize


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'transaction_sum, to_refund, e_this_refund, e_left_to_refund',
    [
        (
            {'ride': '100', 'tips': '10'},
            _basket({'ride': '100', 'burgers': '50'}),
            _basket({'ride': '100'}),
            _basket({'burgers': '50'}),
        ),
        (
            {'ride': '100', 'tips': '10'},
            _basket({'ride': '120', 'tips': '6'}),
            _basket({'ride': '100', 'tips': '6'}),
            _basket({'ride': '20'}),
        ),
        (
            {'ride': '100', 'tips': '10'},
            _basket({'burgers': '120', 'milk': '6'}),
            None,
            _basket({'burgers': '120', 'milk': '6'}),
        ),
    ],
)
def test_calc_transaction_refund(
        transaction_sum, to_refund, e_this_refund, e_left_to_refund,
):
    transaction = {'sum': transaction_sum}
    this_refund, left_to_refund = basket.calc_transaction_refund(
        transaction, to_refund,
    )
    if e_this_refund is None:
        assert this_refund is None
    else:
        assert e_this_refund == this_refund
    assert not e_left_to_refund - left_to_refund


@pytest.mark.parametrize(
    'basket_to_pay, paid, expected',
    [
        (
            CompositeBasket({}),
            CompositeBasket({}),
            (CompositeBasket({}), CompositeBasket({})),
        ),
        (
            CompositeBasket({'a': _basket({'b': '1'})}),
            CompositeBasket({'a': _basket({'b': '1'})}),
            (CompositeBasket({}), CompositeBasket({})),
        ),
        (
            CompositeBasket({'a': _basket({'b': '2'})}),
            CompositeBasket({'a': _basket({'b': '1'})}),
            (CompositeBasket({'a': _basket({'b': '1'})}), CompositeBasket({})),
        ),
        (
            CompositeBasket({'a': _basket({'b': '1'})}),
            CompositeBasket({'a': _basket({'b': '2'})}),
            (CompositeBasket({}), CompositeBasket({'a': _basket({'b': '1'})})),
        ),
        (
            CompositeBasket({'a': _basket({'b': '2'})}),
            CompositeBasket({'a': _basket({'с': '1'})}),
            (
                CompositeBasket({'a': _basket({'b': '2'})}),
                CompositeBasket({'a': _basket({'с': '1'})}),
            ),
        ),
        (
            CompositeBasket({'a': _basket({'b': '1', 'c': '1'})}),
            CompositeBasket({'a': _basket({'b': '2', 'c': '2'})}),
            (
                CompositeBasket({}),
                CompositeBasket({'a': _basket({'b': '1', 'c': '1'})}),
            ),
        ),
        (
            CompositeBasket({'a': _basket({'b': '1', 'c': '1'})}),
            CompositeBasket({'a': _basket({'b': '2', 'c': '1'})}),
            (CompositeBasket({}), CompositeBasket({'a': _basket({'b': '1'})})),
        ),
        (
            CompositeBasket(
                {'a': _basket({'b': '1'}), 'c': _basket({'d': '1'})},
            ),
            CompositeBasket({}),
            (
                CompositeBasket(
                    {'a': _basket({'b': '1'}), 'c': _basket({'d': '1'})},
                ),
                CompositeBasket({}),
            ),
        ),
        (
            CompositeBasket({'a': _basket({'b': '1'})}),
            CompositeBasket({'c': _basket({'d': '1'})}),
            (
                CompositeBasket({'a': _basket({'b': '1'})}),
                CompositeBasket({'c': _basket({'d': '1'})}),
            ),
        ),
    ],
)
@pytest.mark.nofilldb
def test_calc_hold_resize_refund(basket_to_pay, paid, expected):
    actual = basket.calc_hold_resize_refund(basket_to_pay, paid)
    assert actual == expected


def _build_basket(
        item_id: str = 'some_item_id',
        amount: decimal.Decimal = decimal.Decimal(100),
        price_and_quantity: Optional[basket.PriceAndQuantity] = None,
        merchant: Optional[basket.Merchant] = None,
):
    merchant_id = None
    if merchant is not None:
        merchant_id = merchant.id
    item = _build_basket_item(
        item_id=item_id,
        amount=amount,
        price_and_quantity=price_and_quantity,
        merchant=merchant,
    )
    key = basket.Key(item_id, merchant_id)
    items = {key: item}
    return basket.Basket(items)


def _build_basket_item(
        item_id='some_item_id',
        amount=decimal.Decimal(100),
        price_and_quantity=None,
        merchant=None,
) -> basket.BasketItem:
    return basket.BasketItem(
        item_id=item_id,
        amount=amount,
        price_and_quantity=price_and_quantity,
        merchant=merchant,
    )


def _build_merchant(
        id_: str, order_id: Optional[str] = None,
) -> basket.Merchant:
    return basket.Merchant(id=id_, order_id=order_id)


@pytest.mark.parametrize(
    'a_basket, serialized',
    [
        pytest.param(
            _build_basket('some_item_id', amount=decimal.Decimal(100)),
            {'some_item_id': {'item_id': 'some_item_id', 'amount': '100'}},
            id='should work on baskets with minimum set of fields',
        ),
        pytest.param(
            _build_basket(
                'some_item_id',
                amount=decimal.Decimal(100),
                price_and_quantity=basket.PriceAndQuantity(
                    decimal.Decimal(50), decimal.Decimal(2),
                ),
                merchant=_build_merchant('some_merchant_id'),
            ),
            {
                'some_item_id|some_merchant_id': {
                    'item_id': 'some_item_id',
                    'amount': '100',
                    'price': '50',
                    'quantity': '2',
                    'merchant': {'id': 'some_merchant_id'},
                },
            },
            id='should work on baskets with full set of fields',
        ),
    ],
)
def test_basket_serde(a_basket, serialized):
    actual_serialized = a_basket.serialize()
    assert actual_serialized == serialized

    actual_deserialized = basket.Basket.deserialize(actual_serialized)
    assert actual_deserialized == a_basket


@pytest.mark.parametrize(
    'merchant, serialized',
    [
        pytest.param(
            _build_merchant('some_merchant_id'),
            {'id': 'some_merchant_id'},
            id='should work on merchants with minimum set of fields',
        ),
        pytest.param(
            _build_merchant('some_merchant_id', 'some_merchant_order_id'),
            {'id': 'some_merchant_id', 'order_id': 'some_merchant_order_id'},
            id='should work on merchants with full set of fields',
        ),
    ],
)
def test_merchant_serde(merchant, serialized):
    actual_serialized = merchant.serialize()
    assert actual_serialized == serialized

    actual_deserialized = basket.Merchant.deserialize(actual_serialized)
    assert actual_deserialized == merchant


@pytest.mark.parametrize(
    'key, serialized',
    [
        pytest.param(
            basket.Key('some_item_id', 'some_merchant_id'),
            'some_item_id|some_merchant_id',
            id='should work on keys with merchant id',
        ),
        pytest.param(
            basket.Key('some_item_id', None),
            'some_item_id',
            id='should be backward compatible on keys without merchant id',
        ),
    ],
)
def test_basket_key_serde(key, serialized):
    actual_serialized = key.serialize()
    assert actual_serialized == serialized

    actual_deserialized = basket.Key.deserialize(actual_serialized)
    assert actual_deserialized == key


@pytest.mark.parametrize(
    'a_basket, expected',
    [
        pytest.param(
            _build_basket(price_and_quantity=None, merchant=None),
            False,
            id=(
                'basket without price_and_quantity and merchant_id '
                'should not be serialized'
            ),
        ),
        pytest.param(
            _build_basket(
                price_and_quantity=basket.PriceAndQuantity(
                    decimal.Decimal(50), decimal.Decimal(2),
                ),
            ),
            True,
            id='basket with prices_and_quantities should be serialized',
        ),
        pytest.param(
            _build_basket(merchant=_build_merchant('some_merchant_id')),
            True,
            id='basket with merchant_id should be serialized',
        ),
    ],
)
def test_should_be_serialized(a_basket, expected):
    actual = a_basket.should_be_serialized()

    assert actual is expected


@pytest.mark.parametrize(
    'a_basket, expected',
    [
        pytest.param(
            basket.Basket({}), True, id='empty basket has unique item_ids',
        ),
        pytest.param(
            basket.Basket(
                {
                    basket.Key(
                        'first_item_id', 'first_merchant_id',
                    ): _build_basket_item(),
                    basket.Key(
                        'second_item_id', 'second_merchant_id',
                    ): _build_basket_item(),
                },
            ),
            True,
            id='should return True if all item_ids are unique',
        ),
        pytest.param(
            basket.Basket(
                {
                    basket.Key(
                        'first_item_id', 'first_merchant_id',
                    ): _build_basket_item(),
                    basket.Key(
                        'first_item_id', 'second_merchant_id',
                    ): _build_basket_item(),
                },
            ),
            False,
            id='should return False if there are duplicate item_ids',
        ),
    ],
)
def test_has_unique_item_ids(a_basket, expected):
    assert a_basket.has_unique_item_ids() is expected
