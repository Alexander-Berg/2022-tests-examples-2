# pylint: disable=too-many-lines

import typing

import pytest

from tests_eats_payments import helpers

URL = 'v1/orders/add_item'

BASE_HEADERS = {'X-Yandex-Uid': '100500'}
BASE_PAYLOAD = {'order_id': 'test_order', 'version': 2, 'revision': 'abcd'}


@pytest.fixture(name='check_add_item')
def check_add_item_fixture(taxi_eats_payments):
    async def _inner(
            item: dict,
            payment_type: typing.Optional[str] = None,
            response_status: int = 200,
            response_body: typing.Optional[dict] = None,
            headers: typing.Optional[dict] = None,
            ttl: int = None,
    ):
        payload: typing.Dict[str, typing.Any] = {**BASE_PAYLOAD, 'item': item}
        if payment_type is not None:
            payload['payment_method'] = {'id': '123', 'type': payment_type}
        if ttl is not None:
            payload['ttl'] = ttl
        if headers is None:
            headers = BASE_HEADERS
        response = await taxi_eats_payments.post(
            URL, json=payload, headers=headers,
        )
        assert response.status == response_status
        if response_body is not None:
            assert response.json() == response_body

    return _inner


@pytest.mark.parametrize('payment_type', ['card', 'applepay', 'googlepay'])
async def test_add_item_no_payment_method_ok(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        payment_type,
):
    first_operation_items = (
        helpers.make_transactions_payment_items(
            payment_type=payment_type,
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac_1', amount='2.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_2', amount='3.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_3', amount='3.00',
                ),
            ],
        ),
    )
    second_operation_items = (
        helpers.make_transactions_payment_items(
            payment_type=payment_type,
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac_1', amount='2.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_2', amount='3.00',
                ),
            ],
        ),
    )
    operation1 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=first_operation_items,
    )
    operation2 = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=second_operation_items,
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        items=[],
        transactions=[helpers.make_transaction(payment_type=payment_type)],
        operations=[operation1, operation2],
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac_1', amount='2.00'),
            helpers.make_transactions_item(item_id='big_mac_2', amount='3.00'),
            helpers.make_transactions_item(
                item_id='big_mac_to_add', amount='2.00',
            ),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        operation_id='add_item:abcd',
        payment_type=payment_type,
        items=[transactions_items],
    )
    item_to_add = helpers.make_item(item_id='big_mac_to_add', amount='2.00')
    await check_add_item(item=item_to_add, response_status=200)

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@pytest.mark.parametrize(
    'transactions',
    (
        pytest.param([], id='No transactions'),
        pytest.param(
            [helpers.make_transaction(payment_type=None)],
            id='Transaction with no `payment_type`',
        ),
        pytest.param(
            [helpers.make_transaction(payment_method_id=None)],
            id='Transaction with no `payment_method_id`',
        ),
    ),
)
async def test_unable_to_determine_payment_method_error(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        transactions,
):
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        items=[], transactions=transactions,
    )
    item = helpers.make_item(item_id='big_mac', amount='2.00')
    invoice_update_mock = mock_transactions_invoice_update(
        items=[], payment_type='card',
    )
    await check_add_item(item=item, response_status=500)
    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 0


@pytest.mark.parametrize(
    'payment_type, item, invoice_retrieve_items, invoice_update_items',
    [
        pytest.param(
            'card',
            helpers.make_item(item_id='big_mac', amount='2.00'),
            [],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='2.00',
                        ),
                    ],
                ),
            ],
            id='Test with empty items in invoice',
        ),
        pytest.param(
            'card',
            helpers.make_item(item_id='big_mac', amount='2.00'),
            [
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='2.00',
                        ),
                    ],
                ),
            ],
            id='Test with the same item but different payment type',
        ),
        pytest.param(
            'card',
            helpers.make_item(item_id='big_mac', amount='2.00'),
            [
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='1.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='1.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='2.00',
                        ),
                    ],
                ),
            ],
            id='Test with the different item but the same payment type',
        ),
        pytest.param(
            'card',
            helpers.make_item(item_id='big_mac', amount='2.00'),
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='1.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cola', amount='3.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='1.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='2.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cola', amount='3.00',
                        ),
                    ],
                ),
            ],
            id='Test with the different item and some items already available',
        ),
        pytest.param(
            'card',
            helpers.make_item(item_id='big_mac', amount='2.00'),
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='3.00',
                        ),
                    ],
                ),
            ],
            id='Test with the same item and the same payment type',
        ),
        pytest.param(
            'card',
            helpers.make_item(item_id='big_mac', amount='2.00'),
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='1.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='2.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cola', amount='3.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='1.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='4.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cola', amount='3.00',
                        ),
                    ],
                ),
            ],
            id='Test with the same item and some items already available',
        ),
    ],
)
async def test_add_item_with_amount(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        payment_type,
        item,
        invoice_retrieve_items,
        invoice_update_items,
):
    previous_operation_items = [
        helpers.make_transactions_payment_items(
            payment_type=payment_type,
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac_1', amount='2.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_2', amount='3.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_3', amount='3.00',
                ),
            ],
        ),
    ]
    operation1 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=previous_operation_items,
    )
    operation2 = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=invoice_retrieve_items,
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        items=invoice_retrieve_items, operations=[operation1, operation2],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        operation_id='add_item:abcd',
        items=invoice_update_items,
        payment_type=payment_type,
    )

    await check_add_item(item=item, payment_type=payment_type)

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@pytest.mark.parametrize(
    'payment_type, item, invoice_retrieve_items, invoice_update_items',
    [
        pytest.param(
            'card',
            helpers.make_item(
                item_id='big_mac', quantity='1.000', price='12.50',
            ),
            [],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', quantity='1.000', price='12.50',
                        ),
                    ],
                ),
            ],
            id='Test with empty items in invoice',
        ),
        pytest.param(
            'card',
            helpers.make_item(
                item_id='big_mac', quantity='1.000', price='12.50',
            ),
            [
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac',
                            quantity='1.000',
                            price='12.50',
                            calc_amount=True,
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', quantity='1.000', price='12.50',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', quantity='1.000', price='12.50',
                        ),
                    ],
                ),
            ],
            id='Test with the same item but different payment type',
        ),
        pytest.param(
            'card',
            helpers.make_item(
                item_id='big_mac', quantity='1.000', price='12.50',
            ),
            [
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger',
                            quantity='1.000',
                            price='8.00',
                            calc_amount=True,
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger',
                            quantity='1.000',
                            price='8.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', quantity='1.000', price='12.50',
                        ),
                    ],
                ),
            ],
            id='Test with the different item but the same payment type',
        ),
        pytest.param(
            'card',
            helpers.make_item(
                item_id='big_mac', quantity='2.000', price='12.50',
            ),
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger',
                            quantity='1.000',
                            price='8.00',
                            calc_amount=True,
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cola',
                            quantity='3.000',
                            price='5.00',
                            calc_amount=True,
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger',
                            quantity='1.000',
                            price='8.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='big_mac', quantity='2.000', price='12.50',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cola', quantity='3.000', price='5.00',
                        ),
                    ],
                ),
            ],
            id='Test with the different item and some items already available',
        ),
        pytest.param(
            'card',
            helpers.make_item(
                item_id='big_mac', quantity='1.000', price='12.50',
            ),
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac',
                            quantity='1.000',
                            price='12.50',
                            calc_amount=True,
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', quantity='2.000', price='12.50',
                        ),
                    ],
                ),
            ],
            id='Test with the same item and the same payment type',
        ),
        pytest.param(
            'card',
            helpers.make_item(
                item_id='big_mac', quantity='1.000', price='12.50',
            ),
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger',
                            quantity='1.000',
                            price='8.00',
                            calc_amount=True,
                        ),
                        helpers.make_transactions_item(
                            item_id='big_mac',
                            quantity='2.000',
                            price='12.50',
                            calc_amount=True,
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cola',
                            quantity='3.000',
                            price='5.00',
                            calc_amount=True,
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cheeseburger',
                            quantity='1.000',
                            price='8.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='big_mac', quantity='3.000', price='12.50',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='applepay',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cola', quantity='3.000', price='5.00',
                        ),
                    ],
                ),
            ],
            id='Test with the same item and some items already available',
        ),
    ],
)
async def test_add_item_with_quantity(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        payment_type,
        item,
        invoice_retrieve_items,
        invoice_update_items,
):
    previous_operation_items = [
        helpers.make_transactions_payment_items(
            payment_type=payment_type,
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac_1', amount='2.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_2', amount='3.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_3', amount='3.00',
                ),
            ],
        ),
    ]
    operation1 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=previous_operation_items,
    )
    operation2 = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=invoice_retrieve_items,
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        items=invoice_retrieve_items, operations=[operation1, operation2],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        operation_id='add_item:abcd',
        items=invoice_update_items,
        payment_type=payment_type,
    )

    await check_add_item(item=item, payment_type=payment_type)

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@pytest.mark.parametrize(
    'payment_type, item, invoice_retrieve_items',
    [
        pytest.param(
            'card',
            helpers.make_item(item_id='big_mac', amount='3.00'),
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', quantity='1.000', price='12.50',
                        ),
                    ],
                ),
            ],
            id=(
                'Test with new item with amount'
                ' and transactions item with quantity'
            ),
        ),
        pytest.param(
            'card',
            helpers.make_item(
                item_id='big_mac', quantity='1.000', price='12.50',
            ),
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='3.00',
                        ),
                    ],
                ),
            ],
            id=(
                'Test with new item with quantity'
                ' and transactions item with amount'
            ),
        ),
        pytest.param(
            'card',
            helpers.make_item(
                item_id='big_mac', quantity='1.000', price='12.50',
            ),
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', quantity='1.000', price='12.51',
                        ),
                    ],
                ),
            ],
            id='Test with different prices for new item and transactions item',
        ),
    ],
)
async def test_add_item_conflicts(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        payment_type,
        item,
        invoice_retrieve_items,
):
    previous_operation_items = [
        helpers.make_transactions_payment_items(
            payment_type=payment_type,
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac_1', amount='2.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_2', amount='3.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_3', amount='3.00',
                ),
            ],
        ),
    ]
    operation1 = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=previous_operation_items,
    )
    operation2 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=invoice_retrieve_items,
    )

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        items=invoice_retrieve_items, operations=[operation1, operation2],
    )
    invoice_update_mock = mock_transactions_invoice_update()

    await check_add_item(
        item=item, payment_type=payment_type, response_status=409,
    )

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 0


@pytest.mark.parametrize(
    'item',
    [
        pytest.param(
            helpers.make_item(
                item_id='big_mac', amount='3.00', quantity='1.000',
            ),
            id='Test item with amount and quantity',
        ),
        pytest.param(
            helpers.make_item(item_id='big_mac', amount='3.00', price='10.00'),
            id='Test item with amount and price',
        ),
        pytest.param(
            helpers.make_item(
                item_id='big_mac',
                amount='3.00',
                price='10.00',
                quantity='1.000',
            ),
            id='Test item with amount, price and quantity',
        ),
        pytest.param(
            helpers.make_item(
                item_id='big_mac', amount='3.00', quantity='1.000',
            ),
            id='Test item with only quantity',
        ),
        pytest.param(
            helpers.make_item(item_id='big_mac', amount='3.00', price='10.00'),
            id='Test item with only price',
        ),
    ],
)
async def test_add_item_invalid_item(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        item,
):
    invoice_retrieve_mock = mock_transactions_invoice_retrieve()
    invoice_update_mock = mock_transactions_invoice_update()

    await check_add_item(item=item, payment_type='card', response_status=400)

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 0


async def test_items_info_inserted(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        fetch_items_from_db,
):
    mock_transactions_invoice_retrieve(items={}, operations=[])
    item = helpers.make_item(
        item_id='big_mac',
        amount='2.00',
        billing_info={
            'place_id': 'some_place_id',
            'balance_client_id': 'some_id',
            'item_type': 'product',
        },
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    mock_transactions_invoice_update(
        operation_id='add_item:abcd',
        items=[transactions_items],
        payment_type='card',
    )
    await check_add_item(item=item, payment_type='card')

    db_items = fetch_items_from_db('test_order')
    assert db_items == [
        helpers.make_db_row(
            item_id='big_mac',
            place_id='some_place_id',
            balance_client_id='some_id',
            item_type='product',
        ),
    ]


async def test_items_info_updated(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        insert_items,
        fetch_items_from_db,
):
    insert_items(
        [
            helpers.make_db_row(
                item_id='big_mac',
                place_id='foo',
                balance_client_id='bar',
                item_type='assembly',
            ),
        ],
    )
    mock_transactions_invoice_retrieve(items=[], operations=[])
    item = helpers.make_item(
        item_id='big_mac',
        amount='2.00',
        billing_info={
            'place_id': 'some_place_id',
            'balance_client_id': 'some_id',
            'item_type': 'product',
        },
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    mock_transactions_invoice_update(
        operation_id='add_item:abcd',
        items=[transactions_items],
        payment_type='card',
    )
    await check_add_item(item=item, payment_type='card')

    db_items = fetch_items_from_db('test_order')
    assert db_items == [
        helpers.make_db_row(
            item_id='big_mac',
            place_id='some_place_id',
            balance_client_id='some_id',
            item_type='product',
        ),
    ]


async def test_fiscal_info_passed(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
):
    mock_transactions_invoice_retrieve(items=[], operations=[])
    item = helpers.make_item(
        item_id='big_mac',
        amount='2.00',
        fiscal_receipt_info={
            'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
            'vat': 'nds_20',
            'title': 'Big Mac Burger',
        },
    )
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(
                item_id='big_mac',
                amount='2.00',
                fiscal_receipt_info={
                    'personal_tin_id': '634333f24bc54736b4ad70dcf69759c7',
                    'vat': 'nds_20',
                    'title': 'Big Mac Burger',
                },
            ),
        ],
    )
    mock_transactions_invoice_update(
        operation_id='add_item:abcd',
        items=[transactions_items],
        payment_type='card',
    )
    await check_add_item(item=item, payment_type='card')


async def test_no_billing_and_fiscal_info_ok(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        fetch_items_from_db,
):
    mock_transactions_invoice_retrieve(items=[], operations=[])
    item = helpers.make_item(item_id='big_mac', amount='2.00')
    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(item_id='big_mac', amount='2.00'),
        ],
    )
    mock_transactions_invoice_update(
        operation_id='add_item:abcd',
        items=[transactions_items],
        payment_type='card',
    )
    await check_add_item(item=item, payment_type='card')

    db_items = fetch_items_from_db('test_order')
    assert db_items == []


@pytest.mark.parametrize(
    ('invoice_retrieve_response,' 'response_status,' 'response_body'),
    [
        (
            {
                'status': 404,
                'json': {'code': 'not-found', 'message': 'invoice not found'},
            },
            404,
            {
                'code': 'not-found',
                'message': (
                    'Transactions error while retrieving invoice. '
                    'Error: `invoice not found`'
                ),
            },
        ),
        (
            {
                'status': 500,
                'json': {
                    'code': 'internal-server-error',
                    'message': 'exception',
                },
            },
            500,
            None,
        ),
    ],
)
async def test_retrieve_invoice_errors(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        invoice_retrieve_response,
        response_status,
        response_body,
):
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        invoice_retrieve_response=invoice_retrieve_response,
    )
    invoice_update_mock = mock_transactions_invoice_update()

    await check_add_item(
        item=helpers.make_item(item_id='big_mac', amount='2.00'),
        payment_type='card',
        response_status=response_status,
        response_body=response_body,
    )

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 0


@pytest.mark.parametrize(
    ('invoice_update_response,' 'response_status,' 'response_body'),
    [
        (
            {
                'status': 400,
                'json': {
                    'code': 'bad-request',
                    'message': 'something wrong was sent',
                },
            },
            400,
            {
                'code': 'bad-request',
                'message': (
                    'Transactions error while adding an item to invoice. '
                    'Error: `something wrong was sent`'
                ),
            },
        ),
        (
            {'status': 404},
            404,
            {
                'code': 'invoice-not-found',
                'message': (
                    'Transactions error while adding an item to invoice. '
                    'Error: `invoice not found`'
                ),
            },
        ),
        (
            {
                'status': 409,
                'json': {'code': 'conflict', 'message': 'conflict happened'},
            },
            409,
            {
                'code': 'conflict',
                'message': (
                    'Transactions error while adding an item to invoice. '
                    'Error: `conflict happened`'
                ),
            },
        ),
        (
            {
                'status': 500,
                'json': {
                    'code': 'internal-server-error',
                    'message': 'exception',
                },
            },
            500,
            None,
        ),
    ],
)
async def test_update_invoice_errors(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        invoice_update_response,
        response_status,
        response_body,
):
    invoice_retrieve_items = [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac', amount='1.00',
                ),
            ],
        ),
    ]
    operation1 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=invoice_retrieve_items,
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        items=invoice_retrieve_items, operations=[operation1],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        invoice_update_response=invoice_update_response,
    )
    await check_add_item(
        item=helpers.make_item(item_id='big_mac', amount='2.00'),
        payment_type='card',
        response_status=response_status,
        response_body=response_body,
    )

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@pytest.mark.parametrize('payment_type', ['card', 'applepay', 'googlepay'])
async def test_passing_ttl_to_transactions(
        check_add_item,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        payment_type,
):
    first_operation_items = (
        helpers.make_transactions_payment_items(
            payment_type=payment_type,
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac_1', amount='2.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_2', amount='3.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_3', amount='3.00',
                ),
            ],
        ),
    )
    second_operation_items = (
        helpers.make_transactions_payment_items(
            payment_type=payment_type,
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac_1', amount='2.00',
                ),
                helpers.make_transactions_item(
                    item_id='big_mac_2', amount='3.00',
                ),
            ],
        ),
    )
    operation1 = helpers.make_operation(
        created='2021-03-06T12:00:00.000000+03:00',
        sum_to_pay=first_operation_items,
    )
    operation2 = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=second_operation_items,
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        items=[],
        transactions=[helpers.make_transaction(payment_type=payment_type)],
        operations=[operation1, operation2],
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type=payment_type,
        items=[
            helpers.make_transactions_item(item_id='big_mac_1', amount='2.00'),
            helpers.make_transactions_item(item_id='big_mac_2', amount='3.00'),
            helpers.make_transactions_item(
                item_id='big_mac_to_add', amount='2.00',
            ),
        ],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        operation_id='add_item:abcd',
        payment_type=payment_type,
        items=[transactions_items],
        ttl=600,
    )
    item_to_add = helpers.make_item(item_id='big_mac_to_add', amount='2.00')
    await check_add_item(item=item_to_add, response_status=200, ttl=10)

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1
