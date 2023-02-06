import typing

import pytest

from tests_eats_payments import configs
from tests_eats_payments import consts
from tests_eats_payments import db_order
from tests_eats_payments import helpers
from tests_eats_payments import models

URL = 'v1/orders/update'

ORDER_ID = 'test_order'
OPERATION_ID = 'operation:1234'

BASE_PAYLOAD = {
    'id': ORDER_ID,
    'payment_method': {'id': '123', 'type': 'card'},
    'version': 2,
    'revision': 'abcd',
}


async def check_update_order(
        taxi_eats_payments,
        items: typing.Optional[typing.List[dict]] = None,
        response_status=200,
):
    payload: typing.Dict[str, typing.Any] = {
        **BASE_PAYLOAD,
        'items': items or [],
        'payment_method': {'id': '123', 'type': 'card'},
    }
    response = await taxi_eats_payments.post(
        URL, json=payload, headers=consts.BASE_HEADERS,
    )
    assert response.status == response_status


@pytest.mark.parametrize('payment_type', ['personal_wallet', 'corp'])
@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@pytest.mark.parametrize(
    'test_items, complement_to_pay, complement_paid, cashback_service',
    [
        pytest.param(
            [
                models.TestItem(amount='20.00', by_complement='19.00'),
                models.TestItem(amount='30.00', by_complement='29.00'),
            ],
            '100',
            '48.00',
            'eats',
            id='Test not zero rest after editing order',
        ),
        pytest.param(
            [
                models.TestItem(amount='200.00', by_complement='40.00'),
                models.TestItem(amount='300.00', by_complement='60.00'),
            ],
            '100',
            '100.00',
            'grocery',
            id='Test apply uniform discount during update',
        ),
        pytest.param(
            [models.TestItem(amount='1.00'), models.TestItem(amount='1.00')],
            '100',
            None,
            'eats',
            id='Test no uniform discount after update',
        ),
        pytest.param(
            [
                models.TestItem(amount='270.00', by_complement='3.00'),
                models.TestItem(amount='290.00', by_complement='2.00'),
                models.TestItem(amount='420.00', by_complement='2.00'),
                models.TestItem(amount='430.00', by_complement='3.00'),
                models.TestItem(amount='0.00'),
            ],
            '10.00000',
            '10.00',
            'grocery',
            id='Test item with zero amount',
        ),
    ],
)
async def test_basic(
        taxi_eats_payments,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        pgsql,
        test_items,
        complement_to_pay,
        payment_type,
        complement_paid,
        cashback_service,
):
    primary_payment_type = 'card'

    complement = helpers.get_complement_model(
        payment_type=payment_type,
        amount=complement_to_pay,
        service=cashback_service,
    )

    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id=ORDER_ID,
        complement_payment_type=complement.payment_type,
        complement_payment_id=complement.payment_id,
        complement_amount=complement.amount,
        service=cashback_service,
    )
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=primary_payment_type, operation_id=OPERATION_ID,
            ),
            helpers.make_transaction(
                payment_type=complement.payment_type,
                operation_id=OPERATION_ID,
            ),
        ],
        items=[],
        payment_types=[primary_payment_type, complement.payment_type],
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type=primary_payment_type,
        items=helpers.make_transactions_items(test_items),
    )
    transactions_items_complements = helpers.make_transactions_payment_items(
        payment_type=complement.payment_type,
        items=helpers.make_transactions_items_complement(test_items),
    )

    expected_wallet_payload = (
        None
        if complement_paid is None
        else helpers.make_wallet_payload(
            cashback_service=helpers.map_service_to_wallet_service(
                cashback_service,
            ),
            order_id=ORDER_ID,
            wallet_id=complement.payment_id,
        )
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items, transactions_items_complements],
        payment_type=primary_payment_type,
        complement_payment=complement,
        wallet_payload=expected_wallet_payload
        if complement.is_have_wallet_payload()
        else None,
    )

    request_items = helpers.make_request_items(test_items)
    await check_update_order(
        taxi_eats_payments=taxi_eats_payments, items=request_items,
    )

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@pytest.mark.parametrize(
    'test_items, not_product_item, complement_to_pay, complement_paid',
    [
        pytest.param(
            [
                models.TestItem(amount='20.00', by_complement='19.00'),
                models.TestItem(amount='30.00', by_complement='29.00'),
            ],
            models.TestItem(
                amount='99.00',
                item_type=models.ItemType.delivery,
                billing_info=models.BillingInfo(),
            ),
            '100',
            '48.00',
            id='Test cashback for not product',
        ),
    ],
)
async def test_update_with_non_product_items(
        taxi_eats_payments,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        pgsql,
        fetch_items_from_db,
        test_items,
        not_product_item,
        complement_to_pay,
        complement_paid,
):
    test_items.append(not_product_item)

    primary_payment_type = 'card'

    complement = models.Complement(amount=complement_to_pay)
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id=ORDER_ID,
        complement_payment_type=complement.payment_type,
        complement_payment_id=complement.payment_id,
        complement_amount=complement.amount,
    )
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=primary_payment_type, operation_id=OPERATION_ID,
            ),
            helpers.make_transaction(
                payment_type=complement.payment_type,
                operation_id=OPERATION_ID,
            ),
        ],
        items=[],
        payment_types=[primary_payment_type, complement.payment_type],
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type=primary_payment_type,
        items=helpers.make_transactions_items(test_items),
    )
    transactions_items_complements = helpers.make_transactions_payment_items(
        payment_type=complement.payment_type,
        items=helpers.make_transactions_items_complement(test_items),
    )

    expected_wallet_payload = helpers.make_wallet_payload(
        cashback_service='eda',
        order_id=ORDER_ID,
        wallet_id=complement.payment_id,
    )
    invoice_update_mock = mock_transactions_invoice_update(
        items=[transactions_items, transactions_items_complements],
        payment_type=primary_payment_type,
        complement_payment=complement,
        wallet_payload=expected_wallet_payload,
    )

    request_items = helpers.make_request_items(test_items)
    await check_update_order(
        taxi_eats_payments=taxi_eats_payments, items=request_items,
    )

    assert invoice_retrieve_mock.times_called == 1
    assert invoice_update_mock.times_called == 1

    db_items = fetch_items_from_db('test_order')
    assert db_items == [
        {
            'order_id': ORDER_ID,
            'item_id': 'item_id_2',
            'place_id': not_product_item.billing_info.place_id,
            'balance_client_id': (
                not_product_item.billing_info.balance_client_id
            ),
            'type': not_product_item.item_type.value,
        },
    ]


@configs.PERSONAL_WALLET_FIRM_BY_SERVICE
@pytest.mark.parametrize(
    'test_items, complement_to_pay',
    [
        pytest.param(
            [
                models.TestItem(price='10.00', quantity='2'),
                models.TestItem(price='10.00', quantity='2'),
                models.TestItem(price='10.00', quantity='2'),
            ],
            '40',
            id='Unavailable to split because not `1` quantity',
        ),
        pytest.param(
            [models.TestItem(price='200.00')],
            '100',
            id='Only price without quantity',
        ),
        pytest.param(
            [models.TestItem(quantity='2.00')],
            '100',
            id='Only quantity without price',
        ),
    ],
)
async def test_unable_to_split(
        taxi_eats_payments,
        mock_transactions_invoice_retrieve,
        pgsql,
        test_items,
        complement_to_pay,
):
    primary_payment_type = 'card'

    complement = models.Complement(amount=complement_to_pay)
    order = db_order.DBOrder(
        pgsql=pgsql,
        order_id=ORDER_ID,
        complement_payment_type=complement.payment_type,
        complement_payment_id=complement.payment_id,
        complement_amount=complement.amount,
    )
    order.upsert()

    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        transactions=[
            helpers.make_transaction(
                payment_type=primary_payment_type, operation_id=OPERATION_ID,
            ),
            helpers.make_transaction(
                payment_type=complement.payment_type,
                operation_id=OPERATION_ID,
            ),
        ],
        items=[],
        payment_types=[primary_payment_type, complement.payment_type],
    )

    request_items = helpers.make_request_items(test_items)
    await check_update_order(
        taxi_eats_payments=taxi_eats_payments,
        items=request_items,
        response_status=400,
    )

    assert invoice_retrieve_mock.times_called == 1
