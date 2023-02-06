import decimal

from . import consts
from . import headers
from . import helpers

# pylint: disable=invalid-name
Decimal = decimal.Decimal


async def test_create_compensation_pg(
        grocery_cashback_create_compensation,
        grocery_cashback_db,
        grocery_payments,
):
    items = helpers.make_transaction_items(consts.PRODUCTS)
    grocery_payments.add_transaction(status='clear_success', items=items)

    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID, consts.PAYLOAD,
    )

    assert response.status_code == 200

    compensation = grocery_cashback_db.get_compensation(consts.COMPENSATION_ID)

    assert compensation.order_id == consts.ORDER_ID
    assert compensation.payload == consts.PAYLOAD
    assert compensation.compensation_type == 'support_compensation'

    assert grocery_payments.times_retrieve_called() == 1


async def test_create_compensation_stq(
        grocery_cashback_create_compensation,
        check_cashback_stq_event,
        grocery_payments,
):
    items = helpers.make_transaction_items(consts.PRODUCTS)
    grocery_payments.add_transaction(status='clear_success', items=items)

    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID, consts.PAYLOAD,
    )

    assert response.status_code == 200

    check_cashback_stq_event(
        times_called=1,
        stq_event_id=f'{consts.SERVICE}_{consts.COMPENSATION_ID}',
        order_id=consts.INVOICE_ID,
        service=consts.SERVICE,
    )

    assert grocery_payments.times_retrieve_called() == 1


async def test_create_compensation_invoice(
        grocery_cashback_create_compensation,
        check_cashback_stq_event,
        grocery_payments,
        transactions,
):
    items = helpers.make_transaction_items(consts.PRODUCTS)
    grocery_payments.add_transaction(status='clear_success', items=items)

    transactions.create.check(
        currency=consts.CURRENCY,
        id=consts.INVOICE_ID,
        yandex_uid=headers.YANDEX_UID,
        personal_phone_id='personal_phone_id',
        user_ip='user_ip',
        external_user_info={'user_id': 'taxi_user_id', 'origin': 'taxi'},
    )

    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID, consts.PAYLOAD,
    )

    assert response.status_code == 200

    assert grocery_payments.times_retrieve_called() == 1

    assert transactions.create.times_called == 1


async def test_the_same_compensation_id(
        grocery_cashback_create_compensation,
        check_cashback_stq_event,
        grocery_payments,
):
    items = helpers.make_transaction_items(consts.PRODUCTS)
    grocery_payments.add_transaction(status='clear_success', items=items)

    for iteration in range(2):
        response = await grocery_cashback_create_compensation(
            consts.COMPENSATION_ID, consts.PAYLOAD,
        )

        assert response.status_code == 200

        check_cashback_stq_event(
            times_called=(1 if iteration == 0 else 0),
            stq_event_id=f'{consts.SERVICE}_{consts.COMPENSATION_ID}',
            order_id=consts.INVOICE_ID,
            service=consts.SERVICE,
        )

        assert grocery_payments.times_retrieve_called() == 1


async def test_exceed_quantity(
        grocery_cashback_create_compensation,
        check_cashback_stq_event,
        grocery_payments,
):
    items = helpers.make_transaction_items(consts.ONE_PRODUCT)
    grocery_payments.add_transaction(status='clear_success', items=items)

    payload = helpers.create_payload(consts.ONE_PRODUCT)
    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID, payload,
    )

    assert response.status_code == 200

    check_cashback_stq_event(
        times_called=1,
        stq_event_id=f'{consts.SERVICE}_{consts.COMPENSATION_ID}',
        order_id=consts.INVOICE_ID,
        service=consts.SERVICE,
    )

    assert grocery_payments.times_retrieve_called() == 1

    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID + '_1', payload,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'quantity_excess',
        'message': (
            f'Request item: {consts.ITEM1_ID}'
            f' summary cashback quantity:'
            f' {str(Decimal(consts.ITEM1_QUANTITY)*2)}'
            f' exceeds the cleared or held quantity: {consts.ITEM1_QUANTITY}'
        ),
    }

    assert grocery_payments.times_retrieve_called() == 2


async def test_extra_product(
        grocery_cashback_create_compensation,
        check_cashback_stq_event,
        grocery_payments,
):
    items = helpers.make_transaction_items(consts.PRODUCTS)
    grocery_payments.add_transaction(status='clear_success', items=items)

    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID, consts.PAYLOAD,
    )

    assert response.status_code == 200

    check_cashback_stq_event(
        times_called=1,
        stq_event_id=f'{consts.SERVICE}_{consts.COMPENSATION_ID}',
        order_id=consts.INVOICE_ID,
        service=consts.SERVICE,
    )

    assert grocery_payments.times_retrieve_called() == 1

    payload = helpers.create_payload(consts.EXTRA_PRODUCT)
    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID + '_1', payload,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'item_is_not_paid',
        'message': (
            f'Trying to gain cashback'
            f' for item_id: {consts.ITEM3_ID} that is not cleared or held yet'
        ),
    }

    assert grocery_payments.times_retrieve_called() == 2


async def test_only_other__no_payment(
        grocery_cashback_create_compensation, grocery_payments,
):
    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID, helpers.OTHER_PAYLOAD,
    )

    assert response.status_code == 200

    assert grocery_payments.times_retrieve_called() == 0
