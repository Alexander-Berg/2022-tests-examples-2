# pylint: disable=E0401
from grocery_mocks.models import country
import pytest

from . import consts
from . import helpers

PAYLOAD = helpers.create_payload(consts.PRODUCTS)


async def test_stq_grocery_cashback_compensation(
        run_stq_cashback_compensation,
        grocery_cashback_create_compensation,
        grocery_orders,
        grocery_payments,
        grocery_cashback_db,
        check_eats_cashback_emission,
        processing,
):
    items = helpers.make_transaction_items(consts.PRODUCTS)
    grocery_payments.add_transaction(status='clear_success', items=items)

    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID, PAYLOAD,
    )

    assert response.status_code == 200

    last_operation = {
        'operation_id': 'dummy',
        'yandex_uid': 'dummy',
        'user_ip': 'dummy',
        'wallet_id': 'dummy',
        'reward': [],
    }

    await run_stq_cashback_compensation(
        order_id=helpers.make_invoice_id(consts.COMPENSATION_ID),
        last_operation=last_operation,
    )

    compensation = grocery_cashback_db.get_compensation(consts.COMPENSATION_ID)

    assert compensation.status == 'done'

    check_eats_cashback_emission(
        times_called=1,
        stq_event_id=f'{consts.SERVICE}_'
        f'{compensation.order_id}_'
        f'{compensation.compensation_id}',
        order_id=compensation.order_id,
        last_operation=last_operation,
    )

    _check_processing_event(processing)


@pytest.mark.parametrize(
    'country_iso2, eats_cashback_emission_times_called',
    [
        (country.Country.Russia.country_iso2, 1),
        (country.Country.Israel.country_iso2, 0),
    ],
)
async def test_eats_notification(
        run_stq_cashback_compensation,
        grocery_cashback_create_compensation,
        grocery_payments,
        grocery_orders,
        check_eats_cashback_emission,
        country_iso2,
        eats_cashback_emission_times_called,
):
    grocery_orders.order.update(country_iso2=country_iso2)
    items = helpers.make_transaction_items(consts.PRODUCTS)
    grocery_payments.add_transaction(status='clear_success', items=items)

    await grocery_cashback_create_compensation(consts.COMPENSATION_ID, PAYLOAD)

    last_operation = {
        'operation_id': 'dummy',
        'yandex_uid': 'dummy',
        'user_ip': 'dummy',
        'wallet_id': 'dummy',
        'reward': [],
    }

    await run_stq_cashback_compensation(
        order_id=helpers.make_invoice_id(consts.COMPENSATION_ID),
        last_operation=last_operation,
    )

    check_eats_cashback_emission(
        times_called=eats_cashback_emission_times_called,
    )


def _check_processing_event(processing):
    events = list(processing.events(scope='grocery', queue='compensations'))

    assert len(events) == 1

    event = events[0]
    payload = event.payload

    assert payload['reason'] == 'set_compensation_state'
    assert payload['order_id'] == consts.ORDER_ID
    assert payload['compensation_id'] == consts.COMPENSATION_ID
    assert payload['state']
