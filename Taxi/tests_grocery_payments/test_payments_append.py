import copy
import decimal

import pytest

from . import consts
from . import headers
from . import helpers
from . import models
from . import pytest_marks
from .plugins import configs


PaymentType = models.PaymentType

COUNTRY = models.Country.Russia

ITEM_1_CARD = models.Item(item_id='item-1', price='10', quantity='2')

ITEM_2_CARD = models.Item(item_id='item-2', price='102.2', quantity='1')

ITEM_3_CARD = models.Item(
    item_id='item-3',
    price='302.2',
    quantity='1',
    item_type=models.ItemType.delivery,
)

ITEM_1_WALLET = models.Item(item_id='item-w-1', price='3', quantity='2')

ITEM_2_WALLET = models.Item(item_id='item-w-2', price='1.2', quantity='1')

OPERATION_SUM_WALLET = models.OperationSum(
    items=[ITEM_1_WALLET, ITEM_2_WALLET],
    payment_type=models.PaymentType.personal_wallet,
)

PAYMENT_METHOD = models.PaymentMethod(
    payment_type=models.PaymentType.card, payment_id=consts.CARD_ID,
)

CASHBACK_PAYMENT_METHOD = models.PaymentMethod(
    payment_type=PaymentType.personal_wallet,
    payment_id=consts.PERSONAL_WALLET_ID,
)


def _merge(item1, item2):
    assert item1.item_id == item2.item_id
    assert item1.price == item2.price

    item = copy.deepcopy(item1)
    item.quantity = str(
        decimal.Decimal(item1.quantity) + decimal.Decimal(item2.quantity),
    )
    return item


@pytest.fixture(name='grocery_payments_append')
def _grocery_payments_append(taxi_grocery_payments):
    async def _inner(
            country=COUNTRY,
            payment_method=None,
            items_by_payment_types=None,
            **kwargs,
    ):
        if items_by_payment_types is None:
            payment_method = payment_method or PAYMENT_METHOD
            items_by_payment_types = [
                {
                    'items': models.to_request_items([ITEM_3_CARD]),
                    'payment_method': payment_method.to_request(),
                },
            ]

        return await taxi_grocery_payments.post(
            '/payments/v1/append',
            json={
                'order_id': consts.ORDER_ID,
                'country_iso3': country.country_iso3,
                'items_by_payment_types': items_by_payment_types,
                'user_info': headers.DEFAULT_USER_INFO,
                'wallet_payload': consts.DEFAULT_WALLET_PAYLOAD,
                **kwargs,
            },
        )

    return _inner


@pytest.mark.parametrize(
    'current_items, append_items, result_items',
    [
        (
            [ITEM_1_CARD, ITEM_2_CARD],
            [ITEM_3_CARD],
            [ITEM_1_CARD, ITEM_2_CARD, ITEM_3_CARD],
        ),
        ([ITEM_1_CARD, ITEM_2_CARD], [], [ITEM_1_CARD, ITEM_2_CARD]),
        (
            [ITEM_1_CARD, ITEM_2_CARD],
            [ITEM_2_CARD],
            [ITEM_1_CARD, _merge(ITEM_2_CARD, ITEM_2_CARD)],
        ),
        (
            [ITEM_1_CARD, ITEM_2_CARD],
            [ITEM_1_WALLET],
            [ITEM_1_CARD, ITEM_2_CARD, ITEM_1_WALLET],
        ),
    ],
)
async def test_basic(
        grocery_payments_append,
        transactions,
        current_items,
        append_items,
        result_items,
):
    operation_id = '12345'
    operation_version = 123456
    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']

    transactions.retrieve.mock_response(
        id=consts.ORDER_ID,
        sum_to_pay=[],
        operation_info={'version': operation_version},
        operations=[
            consts.DEFAULT_OPERATION,
            helpers.make_operation(
                status='done',
                sum_to_pay=[
                    OPERATION_SUM_WALLET.to_object(),
                    models.OperationSum(
                        items=current_items,
                        payment_type=PAYMENT_METHOD.payment_type,
                    ).to_object(),
                ],
            ),
        ],
    )

    transactions.update.check(
        id=consts.ORDER_ID,
        operation_type='append',
        operation_id=operation_id,
        items_by_payment_type=[
            OPERATION_SUM_WALLET.to_object(product_id),
            models.OperationSum(
                items=result_items, payment_type=PAYMENT_METHOD.payment_type,
            ).to_object(product_id),
        ],
        version=operation_version,
    )

    response = await grocery_payments_append(
        operation_id=operation_id,
        items_by_payment_types=[
            {
                'items': models.to_request_items(append_items),
                'payment_method': PAYMENT_METHOD.to_request(),
            },
        ],
    )
    assert response.status_code == 200
    assert transactions.update.times_called == 1

    assert response.json() == {
        'invoice_id': consts.ORDER_ID,
        'operation_id': operation_id,
    }


@pytest_marks.INVOICE_ORIGINATORS
async def test_originator(grocery_payments_append, transactions, originator):
    invoice_id = originator.prefix + consts.ORDER_ID

    transactions.retrieve.mock_response(id=invoice_id)
    transactions.update.check(id=invoice_id)

    response = await grocery_payments_append(
        order_id=consts.ORDER_ID, originator=originator.request_name,
    )
    assert response.status_code == 200
    assert transactions.update.times_called == 1

    assert response.json()['invoice_id'] == invoice_id


async def test_append_with_new_payment_type(
        grocery_payments_append, transactions,
):
    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']

    transactions.retrieve.mock_response(
        id=consts.ORDER_ID,
        status='held',
        sum_to_pay=[],
        operations=[
            consts.DEFAULT_OPERATION,
            helpers.make_operation(
                status='done', sum_to_pay=[OPERATION_SUM_WALLET.to_object()],
            ),
        ],
    )

    items = [ITEM_1_CARD]

    transactions.update.check(
        id=consts.ORDER_ID,
        operation_type='append',
        items_by_payment_type=[
            OPERATION_SUM_WALLET.to_object(product_id),
            models.OperationSum(
                items=items, payment_type=PAYMENT_METHOD.payment_type,
            ).to_object(product_id),
        ],
    )

    response = await grocery_payments_append(
        items_by_payment_types=[
            {
                'items': models.to_request_items(items),
                'payment_method': PAYMENT_METHOD.to_request(),
            },
        ],
    )
    assert response.status_code == 200
    assert transactions.update.times_called == 1


@pytest.mark.parametrize(
    'status_code', ['item_price_modified', 'item_duplicate'],
)
async def test_400(grocery_payments_append, transactions, status_code):
    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']
    item = ITEM_1_CARD

    transactions.retrieve.mock_response(
        id=consts.ORDER_ID,
        status='held',
        sum_to_pay=[],
        operations=[
            helpers.make_operation(
                status='done',
                sum_to_pay=[
                    models.OperationSum(
                        items=[item], payment_type=PAYMENT_METHOD.payment_type,
                    ).to_object(product_id),
                ],
            ),
        ],
    )

    if status_code == 'item_price_modified':
        items = [models.Item(item_id=item.item_id, price='1234', quantity='1')]
        assert item.price != items[0].price
    elif status_code == 'item_duplicate':
        items = [ITEM_2_CARD, ITEM_2_CARD]
    else:
        assert False

    response = await grocery_payments_append(
        items_by_payment_types=[
            {
                'items': models.to_request_items(items),
                'payment_method': PAYMENT_METHOD.to_request(),
            },
        ],
    )
    assert response.status_code == 400
    assert response.json()['code'] == status_code
    assert transactions.update.times_called == 0


@pytest.mark.parametrize('enable_modification', [True, False])
async def test_modification_policy(
        grocery_payments_append,
        grocery_payments_configs,
        transactions,
        enable_modification,
):
    grocery_payments_configs.invoice_modification_policy(
        enabled=enable_modification,
    )

    response = await grocery_payments_append()

    if enable_modification:
        assert response.status_code == 200
        assert transactions.update.times_called == 1
    else:
        assert response.status_code == 400
        assert transactions.update.times_called == 0


async def test_idempotency(
        grocery_payments_append, grocery_payments_db, transactions,
):
    invoice_id = consts.ORDER_ID
    operation_id = 'operation_id'

    for _ in range(2):
        response = await grocery_payments_append(operation_id=operation_id)
        assert response.status_code == 200

        assert grocery_payments_db.has_invoice_operation(
            invoice_id, f'append:{operation_id}',
        )

    assert transactions.update.times_called == 1


@pytest.mark.parametrize('operation_id', ['', ':', 'op:', ':op', 'o:p'])
async def test_wrong_operation_id(grocery_payments_append, operation_id):
    response = await grocery_payments_append(operation_id=operation_id)
    assert response.status_code == 400
