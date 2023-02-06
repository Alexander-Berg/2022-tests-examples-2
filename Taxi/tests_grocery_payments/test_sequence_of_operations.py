import pytest

from . import consts
from . import headers
from . import helpers
from . import models

PaymentType = models.PaymentType

COUNTRY = models.Country.Russia
PAYMENT_METHOD = models.PaymentMethod(
    payment_type=PaymentType.card, payment_id=consts.CARD_ID,
)

ITEM = models.Item(item_id='item-id-1', price='10', quantity='2')

ITEMS = [ITEM]


SUM_TO_PAY = [
    {
        'items': models.to_operation_items([ITEM]),
        'payment_type': PAYMENT_METHOD.payment_type.value,
    },
]


@pytest.mark.parametrize(
    'first_operation, next_operations_with_code',
    [
        (None, [('update', 400), ('remove', 400), ('append', 400)]),
        (
            'create',
            [
                ('cancel', 200),
                ('update', 200),
                ('remove', 200),
                ('append', 200),
            ],
        ),
        (
            'update',
            [
                ('cancel', 200),
                ('update', 200),
                ('remove', 200),
                ('append', 200),
            ],
        ),
        (
            'remove',
            [
                ('cancel', 200),
                ('update', 400),
                ('remove', 200),
                ('append', 200),
            ],
        ),
        (
            'append',
            [
                ('cancel', 200),
                ('update', 400),
                ('remove', 200),
                ('append', 200),
            ],
        ),
        (
            'cancel',
            [
                ('cancel', 200),
                ('update', 200),
                ('remove', 400),
                ('append', 200),
            ],
        ),
    ],
)
async def test_sequence_of_operations(
        taxi_grocery_payments,
        transactions,
        first_operation,
        next_operations_with_code,
):
    item_to_remove = {
        'item_id': ITEMS[0].item_id,
        'quantity': ITEMS[0].quantity,
    }

    operations = []

    if first_operation is not None:
        operation_id = first_operation + ':123'
        operations.append(
            helpers.make_operation(id=operation_id, sum_to_pay=SUM_TO_PAY),
        )

    transactions.retrieve.mock_response(
        status='cleared', operations=operations, sum_to_pay=SUM_TO_PAY,
    )

    for next_operation, expected_result in next_operations_with_code:
        operation = '/payments/v1/' + next_operation

        response = await taxi_grocery_payments.post(
            operation,
            json={
                'order_id': consts.ORDER_ID,
                'country': COUNTRY.name,
                'country_iso3': COUNTRY.country_iso3,
                'currency': COUNTRY.currency,
                'items_by_payment_types': [
                    {
                        'items': models.to_request_items(ITEMS),
                        'payment_method': PAYMENT_METHOD.to_request(),
                    },
                ],
                'items': [item_to_remove],
                'user_info': headers.DEFAULT_USER_INFO,
            },
        )

        assert response.status_code == expected_result
