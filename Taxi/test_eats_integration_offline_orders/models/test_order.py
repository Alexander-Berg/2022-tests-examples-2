import pytest

from eats_integration_offline_orders.models.order import model as order_models


def test_order_refresh_items_update_quantity():

    existing_order = order_models.Order(
        uuid='order_uuid__1',
        items=order_models.OrderItems(
            [
                order_models.OrderItem(
                    id='1', title='Картошечка', price=1.0, quantity=1,
                ),
                order_models.OrderItem(
                    id='2', title='Котлетка', price=1.0, quantity=2,
                ),
                order_models.OrderItem(
                    id='2', title='Капустка', price=1.0, quantity=1,
                ),
            ],
        ),
    )

    outer_items = [
        order_models.OrderItem(
            id='1', title='Картошечка', price=1.0, quantity=2,
        ),
        order_models.OrderItem(
            id='2', title='Котлетка', price=1.0, quantity=1,
        ),
        order_models.OrderItem(
            id='3', title='Капустка', price=1.0, quantity=1,
        ),
    ]

    existing_order.refresh_items(outer_items)

    assert existing_order.items['1'].quantity == 2
    assert existing_order.items['2'].quantity == 1
    assert existing_order.items['3'].quantity == 1


def test_order_refresh_items_update_price():
    existing_order = order_models.Order(
        uuid='order_uuid__1',
        items=order_models.OrderItems(
            [
                order_models.OrderItem(
                    id='1',
                    title='Картошечка',
                    price=1.0,
                    base_price=2.0,
                    quantity=1,
                ),
            ],
        ),
    )
    outer_items = [
        order_models.OrderItem(
            id='1', title='Картошечка', price=2.0, base_price=2.0, quantity=1,
        ),
    ]
    existing_order.refresh_items(outer_items)

    assert existing_order.items == [
        order_models.OrderItem(
            id='1', title='Картошечка', price=2.0, base_price=2.0, quantity=1,
        ),
    ]


@pytest.mark.parametrize(
    'changed_values',
    [{'price': 1.0, 'quantity': 2}, {'price': 1.5, 'quantity': 1}],
)
async def test_order_refresh_items_update_items_hash(changed_values):
    existing_order = order_models.Order(
        uuid='order_uuid__1',
        items=order_models.OrderItems(
            [
                order_models.OrderItem(
                    id='1', title='Картошечка', price=1.0, quantity=1,
                ),
            ],
        ),
    )
    outer_items = [
        order_models.OrderItem(id='1', title='Картошечка', **changed_values),
    ]
    old_hash = existing_order.items_hash
    existing_order.refresh_items(outer_items)
    new_hash = existing_order.items_hash
    assert new_hash != old_hash


@pytest.mark.parametrize(
    'existing_quantity, in_pay, paid_count, outer_quantity, result',
    [(3, 1, 1, 2, 2), (3, 1, 2, 2, 3), (3, 1, 1, 1, 2)],
)
def test_order_refresh_items_decrease_quantity_with_paid_items(
        existing_quantity, in_pay, paid_count, outer_quantity, result,
):

    existing_order = order_models.Order(
        uuid='order_uuid__1',
        items=order_models.OrderItems(
            [
                order_models.OrderItem(
                    id='1',
                    title='Картошечка',
                    price=1.0,
                    quantity=existing_quantity,
                    in_pay_count=in_pay,
                    paid_count=paid_count,
                ),
            ],
        ),
    )

    outer_items = [
        order_models.OrderItem(
            id='1', title='Картошечка', price=1.0, quantity=outer_quantity,
        ),
    ]

    existing_order.refresh_items(outer_items)

    assert existing_order.items['1'].quantity == result


def test_order_refresh_items_add_new_items():
    existing_order = order_models.Order(
        uuid='order_uuid__1',
        items=order_models.OrderItems(
            [
                order_models.OrderItem(
                    id='1', title='Картошечка', price=1.0, quantity=1,
                ),
            ],
        ),
    )
    outer_items = [
        order_models.OrderItem(
            id='1', title='Картошечка', price=1.0, quantity=1,
        ),
        order_models.OrderItem(
            id='2', title='Котлетка', price=1.0, quantity=1,
        ),
    ]
    existing_order.refresh_items(outer_items)

    assert len(existing_order.items) == 2
    assert existing_order.items.get('1')
    assert existing_order.items.get('2')


def test_order_refresh_items_remove_items():
    existing_order = order_models.Order(
        uuid='order_uuid__1',
        items=order_models.OrderItems(
            [
                order_models.OrderItem(
                    id='1', title='Картошечка', price=1.0, quantity=1,
                ),
            ],
        ),
    )
    outer_items = []
    existing_order.refresh_items(outer_items)

    assert existing_order.items == []


@pytest.mark.parametrize(
    'existing_quantity, in_pay_count, paid_count, result',
    [(3, 1, 1, 2), (3, 1, 2, 3)],
)
def test_order_refresh_items_remove_items_with_paid(
        existing_quantity, in_pay_count, paid_count, result,
):
    existing_order = order_models.Order(
        uuid='order_uuid__1',
        items=order_models.OrderItems(
            [
                order_models.OrderItem(
                    id='1',
                    title='Картошечка',
                    price=1.0,
                    quantity=existing_quantity,
                    in_pay_count=in_pay_count,
                    paid_count=paid_count,
                ),
            ],
        ),
    )
    outer_items = []
    existing_order.refresh_items(outer_items)

    assert existing_order.items
    assert existing_order.items['1'].quantity == result


def test_order_refresh_items_remove_items_with_noninteger_quantities():
    existing_order = order_models.Order(
        uuid='order_uuid__1',
        items=order_models.OrderItems(
            [
                order_models.OrderItem(
                    id='1', title='Картошечка', price=1.0, quantity=0.1,
                ),
                order_models.OrderItem(
                    id='2', title='Капуста', price=1.0, quantity=1,
                ),
            ],
        ),
    )
    outer_items = [
        order_models.OrderItem(id='2', title='Капуста', price=1.0, quantity=1),
    ]
    existing_order.refresh_items(outer_items)

    assert existing_order.items == [
        order_models.OrderItem(id='2', title='Капуста', price=1.0, quantity=1),
    ]


def test_order_fully_paid_with_zeroprice_items():
    existing_order = order_models.Order(
        uuid='order_uuid__1',
        items=order_models.OrderItems(
            [
                order_models.OrderItem(
                    id='1',
                    title='Картошечка',
                    price=1.0,
                    quantity=1,
                    paid_count=1,
                ),
                order_models.OrderItem(
                    id='1',
                    title='Модификатор',
                    price=0.0,
                    quantity=1,
                    paid_count=0,
                ),
            ],
        ),
    )

    assert existing_order.is_fully_paid


def test_order_with_ya_discount_percents():
    existing_order = order_models.Order(
        uuid='order_uuid__1',
        ya_discount='10%',
        items=order_models.OrderItems(
            [
                order_models.OrderItem(
                    id='position_id__1',
                    title='Картошечка',
                    price=1.0,
                    quantity=2,
                ),
            ],
        ),
    )

    order_with_discount = existing_order.with_ya_discount()

    assert order_with_discount.amount == 1.8
    assert order_with_discount.ya_discount_val == 0.2

    assert order_with_discount.items.ya_discount_val == 0.2

    assert order_with_discount.items['position_id__1'].price == 0.9
    assert (
        order_with_discount.items['position_id__1'].ya_discount_for_price
        == 0.1
    )
    assert (
        order_with_discount.items['position_id__1'].ya_discount_for_amount
        == 0.2
    )
