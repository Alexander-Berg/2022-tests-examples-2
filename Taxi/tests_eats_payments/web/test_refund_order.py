import typing

import pytest

from tests_eats_payments import db_order
from tests_eats_payments import helpers
from tests_eats_payments import models

URL = 'v1/orders/refund'

OPERATION_ID = 'refund:abcd'
ORDER_ID = 'test_order'

COMPLEMENT = models.Complement(amount='1.00')

BASE_PAYLOAD = {
    'order_id': ORDER_ID,
    'version': 2,
    'revision': 'abcd',
    'items': [],
}


@pytest.fixture(name='mock_refund_invoice_retrieve')
def _mock_refund_invoice_retrieve(mock_transactions_invoice_retrieve):
    def _inner(
            *args, invoice_status: typing.Optional[str] = 'cleared', **kwargs,
    ):
        return mock_transactions_invoice_retrieve(
            status=invoice_status, *args, **kwargs,
        )

    return _inner


@pytest.fixture(name='check_refund')
def check_refund_fixture(
        upsert_order, taxi_eats_payments, mockserver, load_json,
):
    upsert_order('test_order')

    async def _inner(
            items: typing.List[dict],
            response_status=200,
            response_body=None,
            ttl: int = None,
            order_id=ORDER_ID,
    ):
        payload: typing.Dict[str, typing.Any] = {
            **BASE_PAYLOAD,
            'items': items,
        }
        if ttl is not None:
            payload['ttl'] = ttl
        payload['order_id'] = order_id
        response = await taxi_eats_payments.post(URL, json=payload)
        assert response.status == response_status
        if response_body is not None:
            assert response.json() == response_body

    return _inner


@pytest.mark.parametrize(
    'items, invoice_retrieve_items, invoice_update_items, wallet_refund, ttl',
    [
        pytest.param(
            [helpers.make_item(item_id='big_mac', amount='1.00')],
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
            None,
            None,
            id=(
                'Test with a partial refund for a single item'
                ' and a single payment type'
            ),
        ),
        pytest.param(
            [helpers.make_item(item_id='big_mac', amount='2.00')],
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
            [],
            None,
            None,
            id=(
                'Test with a full refund for a single item'
                ' and a single payment type'
            ),
        ),
        pytest.param(
            [
                helpers.make_item(item_id='big_mac', amount='2.00'),
                helpers.make_item(item_id='cheeseburger', amount='1.00'),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='2.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='2.00',
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
                    ],
                ),
            ],
            None,
            None,
            id=(
                'Test with a partial refund for multiple items'
                ' and a single payment type'
            ),
        ),
        pytest.param(
            [
                helpers.make_item(item_id='big_mac', amount='2.00'),
                helpers.make_item(item_id='cheeseburger', amount='2.00'),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='2.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='cola', amount='3.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='2.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cola', amount='3.00',
                        ),
                    ],
                ),
            ],
            None,
            None,
            id=(
                'Test with a full refund for multiple items'
                ' and a single payment type, some items remaining'
            ),
        ),
        pytest.param(
            [helpers.make_item(item_id='big_mac', amount='2.00')],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='2.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                    ],
                ),
            ],
            '1.00',
            None,
            id=(
                'Test with a partial refund for a single item'
                ' and multiple payment types'
            ),
        ),
        pytest.param(
            [
                helpers.make_item(item_id='big_mac', amount='2.00'),
                helpers.make_item(item_id='cheeseburger', amount='3.00'),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='2.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='cola', amount='3.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='1.00',
                        ),
                    ],
                ),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='cola', amount='3.00',
                        ),
                    ],
                ),
            ],
            None,
            None,
            id=(
                'Test with a full refund for multiple items'
                ' and multiple payment types'
            ),
        ),
        pytest.param(
            [helpers.make_item(item_id='big_mac', amount='1.00')],
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
            None,
            15,
            id='Test passing ttl to transactions',
        ),
    ],
)
async def test_refund_items_with_amount(
        check_refund,
        mock_refund_invoice_retrieve,
        mock_transactions_invoice_update,
        pgsql,
        items,
        invoice_retrieve_items,
        invoice_update_items,
        wallet_refund,
        ttl,
):
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id=ORDER_ID,
        complement_payment_type=COMPLEMENT.payment_type,
        complement_payment_id=COMPLEMENT.payment_id,
        complement_amount=COMPLEMENT.amount,
    )
    order.upsert()

    previous_operation_items = [
        helpers.make_transactions_payment_items(
            payment_type='card',
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

    cleared = [{'payment_type': 'card', 'items': items}]

    invoice_retrieve_mock = mock_refund_invoice_retrieve(
        cleared=cleared,
        items=invoice_retrieve_items,
        operations=[operation1, operation2],
    )
    wallet_payload = (
        helpers.make_wallet_payload(
            cashback_service='eda',
            order_id=ORDER_ID,
            wallet_id=COMPLEMENT.payment_id,
        )
        if wallet_refund is not None
        else None
    )
    ttl_in_seconds = None
    if ttl is not None:
        ttl_in_seconds = ttl * 60
    invoice_update_mock = mock_transactions_invoice_update(
        items=invoice_update_items,
        operation_id=OPERATION_ID,
        wallet_payload=wallet_payload,
        ttl=ttl_in_seconds,
    )

    await check_refund(items=items, ttl=ttl)

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


# TODO: https://st.yandex-team.ru/EDAORDERS-3157
# test for quantity


async def test_refund_items_invoice_duplicate_items(
        check_refund,
        mock_refund_invoice_retrieve,
        mock_transactions_invoice_update,
):
    invoice_retrieve_items = [
        helpers.make_transactions_payment_items(
            payment_type='card',
            items=[
                helpers.make_transactions_item(
                    item_id='big_mac', amount='3.00',
                ),
            ],
        ),
    ]
    operation = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=invoice_retrieve_items,
    )
    invoice_retrieve_mock = mock_refund_invoice_retrieve(
        items=invoice_retrieve_items, operations=[operation],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[], operation_id=OPERATION_ID,
    )

    await check_refund(
        items=[
            helpers.make_item(item_id='big_mac', amount='1.00'),
            helpers.make_item(item_id='big_mac', amount='2.00'),
        ],
        response_status=400,
    )

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 0


@pytest.mark.parametrize(
    'payment_type, items, invoice_retrieve_items',
    [
        pytest.param(
            'card',
            [helpers.make_item(item_id='big_mac', amount='3.00')],
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
                'Test with items with amount'
                ' and transactions item with quantity'
            ),
        ),
        pytest.param(
            'card',
            [
                helpers.make_item(
                    item_id='big_mac', quantity='1.000', price='12.50',
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
            id=(
                'Test with items with quantity'
                ' and transactions item with amount'
            ),
        ),
        pytest.param(
            'card',
            [
                helpers.make_item(
                    item_id='big_mac', quantity='1.000', price='12.50',
                ),
            ],
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
            id='Test with different prices for items and transactions item',
        ),
    ],
)
async def test_refund_item_conflicts(
        check_refund,
        mock_refund_invoice_retrieve,
        mock_transactions_invoice_update,
        payment_type,
        items,
        invoice_retrieve_items,
):
    operation = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=invoice_retrieve_items,
    )
    invoice_retrieve_mock = mock_refund_invoice_retrieve(
        items=invoice_retrieve_items, operations=[operation],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        operation_id=OPERATION_ID,
    )

    await check_refund(items=items, response_status=409)

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 0


@pytest.mark.parametrize(
    'items, invoice_retrieve_items',
    [
        pytest.param(
            [helpers.make_item(item_id='big_mac', amount='2.00')],
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
            id='Test with a single item and a single payment type',
        ),
        pytest.param(
            [helpers.make_item(item_id='big_mac', amount='3.00')],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                    ],
                ),
            ],
            id='Test with a single item and multiple payment types',
        ),
        pytest.param(
            [
                helpers.make_item(item_id='big_mac', amount='1.00'),
                helpers.make_item(item_id='cheeseburger', amount='2.00'),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='1.00',
                        ),
                    ],
                ),
            ],
            id='Test with multiple items and a single payment type',
        ),
        pytest.param(
            [
                helpers.make_item(item_id='big_mac', amount='2.00'),
                helpers.make_item(item_id='cheeseburger', amount='2.00'),
            ],
            [
                helpers.make_transactions_payment_items(
                    payment_type='card',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                        helpers.make_transactions_item(
                            item_id='cheeseburger', amount='1.00',
                        ),
                    ],
                ),
                helpers.make_transactions_payment_items(
                    payment_type='personal_wallet',
                    items=[
                        helpers.make_transactions_item(
                            item_id='big_mac', amount='1.00',
                        ),
                    ],
                ),
            ],
            id='Test with multiple items and multiple payment types',
        ),
    ],
)
async def test_refund_not_enough_items(
        check_refund,
        mock_refund_invoice_retrieve,
        mock_transactions_invoice_update,
        items,
        invoice_retrieve_items,
):
    operation = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=invoice_retrieve_items,
    )
    invoice_retrieve_mock = mock_refund_invoice_retrieve(
        items=invoice_retrieve_items, operations=[operation],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        operation_id=OPERATION_ID,
    )

    await check_refund(items=items, response_status=409)

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 0


@pytest.mark.parametrize(
    'refund_items, invoice_cleared_items, invoice_retrieve_items, '
    'response_code, update_called',
    [
        pytest.param(
            [helpers.make_item(item_id='big_mac')],
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
            400,
            0,
            id='Test with empty amount and empty price or quantity',
        ),
        pytest.param(
            [helpers.make_item(item_id='big_mac', amount='20.00')],
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
            409,
            0,
            id='Test with amount to refund more than cleared amount',
        ),
        pytest.param(
            [helpers.make_item(item_id='big_mac', amount='2.00')],
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
            200,
            1,
            id='Test with correct cleared',
        ),
    ],
)
async def test_refund_on_hold_failed_invoice(
        check_refund,
        mock_refund_invoice_retrieve,
        mock_transactions_invoice_update,
        refund_items,
        invoice_retrieve_items,
        invoice_cleared_items,
        response_code,
        update_called,
):
    operation = helpers.make_operation(
        created='2021-03-06T13:00:00.000000+03:00',
        sum_to_pay=invoice_retrieve_items,
    )
    invoice_retrieve_mock = mock_refund_invoice_retrieve(
        cleared=invoice_cleared_items,
        invoice_status='hold-failed',
        items=invoice_retrieve_items,
        operations=[operation],
        transactions=[helpers.make_transaction(status='clear_success')],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        operation_id=OPERATION_ID,
    )

    await check_refund(items=refund_items, response_status=response_code)

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == update_called


async def test_duplicate_refund_request(
        check_refund,
        mock_refund_invoice_retrieve,
        mock_transactions_invoice_update,
):
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
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
    operation = {
        'created': '2021-03-06T13:00:00.000000+03:00',
        'id': OPERATION_ID,
        'status': 'done',
        'sum_to_pay': invoice_retrieve_items,
    }
    invoice_retrieve_mock = mock_refund_invoice_retrieve(
        items=invoice_retrieve_items, operations=[operation],
    )
    invoice_update_mock = mock_transactions_invoice_update(
        operation_id=OPERATION_ID,
    )

    await check_refund(items=items, response_status=200)

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 0


async def test_refunding_cancelled(check_refund, upsert_order):
    items = [helpers.make_item(item_id='big_mac', amount='2.00')]
    upsert_order('cancelled_order', cancelled=True)
    await check_refund(
        order_id='cancelled_order', items=items, response_status=400,
    )
