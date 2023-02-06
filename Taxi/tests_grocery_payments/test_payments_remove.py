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
# pylint: disable=invalid-name
Decimal = decimal.Decimal

COUNTRY = models.Country.Russia

ITEM_1_CARD = models.Item(
    item_id='item-1',
    price='10',
    quantity='2',
    item_type=models.ItemType.product,
)

ITEM_2_CARD = models.Item(
    item_id='item-2',
    price='102.2',
    quantity='1',
    item_type=models.ItemType.delivery,
)

ITEM_1_WALLET = models.Item(item_id='item-1', price='3', quantity='2')

ITEM_2_WALLET = models.Item(item_id='item-2', price='1.2', quantity='1')

ITEM_TO_REMOVE = {
    'item_id': ITEM_1_CARD.item_id,
    'quantity': ITEM_1_CARD.quantity,
}

PAYMENT_METHOD = models.PaymentMethod(
    payment_type=PaymentType.card, payment_id=consts.CARD_ID,
)

CASHBACK_PAYMENT_METHOD = models.PaymentMethod(
    payment_type=PaymentType.personal_wallet,
    payment_id=consts.PERSONAL_WALLET_ID,
)

SUM_TO_PAY = [
    {
        'items': models.to_operation_items([ITEM_1_CARD, ITEM_2_CARD]),
        'payment_type': PAYMENT_METHOD.payment_type.value,
    },
    {
        'items': models.to_operation_items([ITEM_1_WALLET, ITEM_2_WALLET]),
        'payment_type': CASHBACK_PAYMENT_METHOD.payment_type.value,
    },
]

LAST_OPERATION = {
    'created': '2021-02-10T11:51:11.207000+03:00',
    'id': 'create:a5d66e1d57be46308d71ade837c199e',
    'status': 'done',
    'sum_to_pay': [
        {
            'items': models.to_operation_items([ITEM_1_CARD, ITEM_2_CARD]),
            'payment_type': PAYMENT_METHOD.payment_type.value,
        },
        {
            'items': models.to_operation_items([ITEM_1_WALLET, ITEM_2_WALLET]),
            'payment_type': CASHBACK_PAYMENT_METHOD.payment_type.value,
        },
    ],
}


@pytest.fixture(name='grocery_payments_remove')
def _grocery_payments_remove(taxi_grocery_payments):
    async def _inner(country=COUNTRY, items=None, **kwargs):
        items = items or [ITEM_TO_REMOVE]

        return await taxi_grocery_payments.post(
            '/payments/v1/remove',
            json={
                'order_id': consts.ORDER_ID,
                'country_iso3': country.country_iso3,
                'items': items,
                'user_info': headers.DEFAULT_USER_INFO,
                'wallet_payload': consts.DEFAULT_WALLET_PAYLOAD,
                **kwargs,
            },
        )

    return _inner


@pytest.mark.parametrize(
    'item_to_remove, card_item_left, personal_wallet_item_left',
    [
        (
            {'item_id': ITEM_1_CARD.item_id, 'quantity': ITEM_1_CARD.quantity},
            ITEM_2_CARD,
            ITEM_2_WALLET,
        ),
        (
            {'item_id': ITEM_2_CARD.item_id, 'quantity': ITEM_2_CARD.quantity},
            ITEM_1_CARD,
            ITEM_1_WALLET,
        ),
    ],
)
async def test_basic(
        grocery_payments_remove,
        transactions,
        item_to_remove,
        card_item_left,
        personal_wallet_item_left,
):
    operation_id = '12345'
    operation_version = 123456

    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']

    transactions.retrieve.mock_response(
        id=consts.ORDER_ID,
        sum_to_pay=SUM_TO_PAY,
        operation_info={'version': operation_version},
        operations=[consts.DEFAULT_OPERATION, LAST_OPERATION],
    )

    transactions.update.check(
        login_id=headers.LOGIN_ID,
        id=consts.ORDER_ID,
        operation_type='remove',
        operation_id=operation_id,
        items_by_payment_type=[
            {
                'items': models.to_operation_items(
                    [card_item_left], product_id=product_id,
                ),
                'payment_type': PAYMENT_METHOD.payment_type.value,
            },
            {
                'items': models.to_operation_items(
                    [personal_wallet_item_left], product_id=product_id,
                ),
                'payment_type': CASHBACK_PAYMENT_METHOD.payment_type.value,
            },
        ],
        version=operation_version,
    )

    response = await grocery_payments_remove(
        operation_id=operation_id, items=[item_to_remove],
    )
    assert response.status_code == 200

    assert transactions.update.times_called == 1

    assert response.json() == {
        'invoice_id': consts.ORDER_ID,
        'operation_id': operation_id,
    }


@pytest_marks.INVOICE_ORIGINATORS
async def test_originator(grocery_payments_remove, transactions, originator):
    invoice_id = originator.prefix + consts.ORDER_ID

    transactions.retrieve.mock_response(
        id=invoice_id,
        sum_to_pay=SUM_TO_PAY,
        operations=[consts.DEFAULT_OPERATION, LAST_OPERATION],
    )

    transactions.update.check(id=invoice_id)

    response = await grocery_payments_remove(
        originator=originator.request_name,
    )
    assert response.status_code == 200

    assert transactions.update.times_called == 1

    assert response.json()['invoice_id'] == invoice_id


@pytest_marks.PAYMENT_TYPES
async def test_payment_types(
        grocery_payments_remove, transactions, payment_type,
):
    operation = copy.deepcopy(LAST_OPERATION)
    operation.update(payment_type=payment_type.value)

    transactions.retrieve.mock_response(
        id=consts.ORDER_ID, sum_to_pay=SUM_TO_PAY, operations=[operation],
    )

    response = await grocery_payments_remove()
    assert response.status_code == 200


@pytest_marks.INVOICE_STATUSES_WITH_CLEARED
async def test_ignore_invoice_status(
        grocery_payments_remove, transactions, invoice_status, is_cleared,
):
    transactions.retrieve.mock_response(
        id=consts.ORDER_ID,
        sum_to_pay=SUM_TO_PAY,
        status=invoice_status,
        operations=[consts.DEFAULT_OPERATION, LAST_OPERATION],
    )

    response = await grocery_payments_remove()
    assert response.status_code == 200

    assert transactions.update.times_called == 1


@pytest_marks.INVOICE_STATUSES_WITH_CLEARED
async def test_404(
        grocery_payments_remove, transactions, invoice_status, is_cleared,
):
    transactions.retrieve.mock_response(
        sum_to_pay=SUM_TO_PAY,
        status=invoice_status,
        operations=[consts.DEFAULT_OPERATION, LAST_OPERATION],
    )

    transactions.update.status_code = 404

    response = await grocery_payments_remove()
    assert response.status_code == 404

    assert transactions.update.times_called == 1


@pytest.mark.parametrize('enable_modification', [True, False])
async def test_modification_policy(
        grocery_payments_remove,
        grocery_payments_configs,
        transactions,
        enable_modification,
):
    grocery_payments_configs.invoice_modification_policy(
        enabled=enable_modification,
    )

    transactions.retrieve.mock_response(
        id=consts.ORDER_ID,
        sum_to_pay=SUM_TO_PAY,
        operations=[consts.DEFAULT_OPERATION, LAST_OPERATION],
    )

    response = await grocery_payments_remove()

    if enable_modification:
        assert response.status_code == 200
        assert transactions.update.times_called == 1
    else:
        assert response.status_code == 400
        assert transactions.update.times_called == 0


async def test_backward_compatibility(grocery_payments_remove, transactions):
    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']

    last_operation = copy.deepcopy(LAST_OPERATION)
    delivery_item = last_operation['sum_to_pay'][0]['items'][2]
    assert delivery_item['item_id'] == 'item-2::sub0:delivery'
    delivery_item['item_id'] = 'delivery::sub0'

    card_item_left = ITEM_2_CARD.to_operation_item(product_id=product_id)
    card_item_left['item_id'] = 'delivery::sub0'

    transactions.retrieve.mock_response(
        id=consts.ORDER_ID,
        sum_to_pay=SUM_TO_PAY,
        operations=[consts.DEFAULT_OPERATION, last_operation],
    )

    transactions.update.check(
        items_by_payment_type=[
            {
                'items': [card_item_left],
                'payment_type': PAYMENT_METHOD.payment_type.value,
            },
            {
                'items': models.to_operation_items(
                    [ITEM_2_WALLET], product_id=product_id,
                ),
                'payment_type': CASHBACK_PAYMENT_METHOD.payment_type.value,
            },
        ],
    )

    response = await grocery_payments_remove()
    assert response.status_code == 200


@pytest_marks.INVOICE_ORIGINATORS
async def test_update_debt(
        grocery_payments_remove, transactions, grocery_user_debts, originator,
):
    invoice_id = originator.prefix + consts.ORDER_ID
    trust_settings = configs.trust_settings_payload(COUNTRY)
    product_id = trust_settings['product_id']
    operation_id = 'operation_id123'

    items = [
        models.OperationSum(
            [ITEM_1_CARD, ITEM_2_CARD], PAYMENT_METHOD.payment_type,
        ),
        models.OperationSum(
            [ITEM_1_WALLET, ITEM_2_WALLET],
            CASHBACK_PAYMENT_METHOD.payment_type,
        ),
    ]
    items_removed = [copy.deepcopy(it) for it in items]
    for it in items_removed:
        it.remove_item(**ITEM_TO_REMOVE)

    grocery_user_debts.retrieve.mock_response(
        debt_id=invoice_id, items=[it.to_object() for it in items],
    )

    transactions.retrieve.mock_response(
        id=invoice_id,
        sum_to_pay=SUM_TO_PAY,
        operations=[helpers.make_operation(status=consts.OPERATION_FAILED)],
    )

    grocery_user_debts.update.check(
        debt=dict(
            debt_id=invoice_id,
            idempotency_token=f'update/remove:{operation_id}',
            items=[it.to_object(product_id) for it in items_removed],
            reason_code='remove',
        ),
        operation=dict(
            operation_type='remove', operation_id=operation_id, priority=1,
        ),
        order=dict(
            order_id=consts.ORDER_ID, country_iso3=COUNTRY.country_iso3,
        ),
    )

    response = await grocery_payments_remove(
        operation_id=operation_id, originator=originator.request_name,
    )
    assert response.status_code == 200

    assert transactions.update.times_called == 1
    assert grocery_user_debts.retrieve.times_called == 1
    assert grocery_user_debts.update.times_called == 1


async def test_not_cleared_item(grocery_payments_remove, transactions):
    transactions.retrieve.mock_response(
        operations=[consts.DEFAULT_OPERATION, LAST_OPERATION],
    )

    response = await grocery_payments_remove(
        items=[{'item_id': 'bad-item-123', 'quantity': '1'}],
    )
    assert response.status_code == 400
    assert response.json()['code'] == 'item_not_payed'

    assert transactions.update.times_called == 0


# Тест эмулирует ситацию, когда был таймаут от transactions и мы делаем
# перезапрос, но среди операций уже есть наша операция.
async def test_retry_with_previous_version(
        grocery_payments_remove, transactions,
):
    item_to_remove = ITEM_2_CARD

    # У нас была успешная операция с 2-мя товарами
    last_successful_operation = helpers.make_operation(
        sum_to_pay=[
            {
                'items': models.to_operation_items([ITEM_1_CARD, ITEM_2_CARD]),
                'payment_type': 'card',
            },
        ],
        status='done',
    )

    # После предыдущего запроса создалась новая операция без товара 2
    last_operation_revision = 'last-op-id-123'
    last_operation = helpers.make_operation(
        id=f'remove:{last_operation_revision}',
        sum_to_pay=[
            {
                'items': models.to_operation_items([ITEM_1_CARD]),
                'payment_type': 'card',
            },
        ],
        status='init',
    )

    transactions.retrieve.mock_response(
        sum_to_pay=SUM_TO_PAY,
        operations=[last_successful_operation, last_operation],
    )

    response = await grocery_payments_remove(
        items=models.to_request_items([item_to_remove]),
        operation_id=last_operation_revision,
    )
    assert response.status_code == 200
    assert response.json()['operation_id'] == last_operation_revision

    assert transactions.update.times_called == 0


async def test_too_many_quantity(grocery_payments_remove, transactions):
    transactions.retrieve.mock_response(
        sum_to_pay=SUM_TO_PAY,
        operations=[consts.DEFAULT_OPERATION, LAST_OPERATION],
    )

    item_id = ITEM_1_CARD.item_id
    huge_quantity = str(Decimal(ITEM_1_CARD.quantity) + 1)

    response = await grocery_payments_remove(
        items=[{'item_id': item_id, 'quantity': huge_quantity}],
    )
    assert response.status_code == 409

    assert transactions.update.times_called == 0


async def test_idempotency(
        grocery_payments_remove, grocery_payments_db, transactions,
):
    invoice_id = consts.ORDER_ID
    operation_id = 'operation_id'

    transactions.retrieve.mock_response(
        id=invoice_id,
        sum_to_pay=SUM_TO_PAY,
        operations=[consts.DEFAULT_OPERATION, LAST_OPERATION],
    )

    for _ in range(2):
        response = await grocery_payments_remove(operation_id=operation_id)
        assert response.status_code == 200

        assert grocery_payments_db.has_invoice_operation(
            invoice_id, f'remove:{operation_id}',
        )

    assert transactions.update.times_called == 1


@pytest.mark.parametrize('operation_id', ['', ':', 'op:', ':op', 'o:p'])
async def test_wrong_operation_id(grocery_payments_remove, operation_id):
    response = await grocery_payments_remove(operation_id=operation_id)
    assert response.status_code == 400
