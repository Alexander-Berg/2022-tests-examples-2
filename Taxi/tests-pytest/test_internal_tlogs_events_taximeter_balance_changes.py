import datetime

import pytest

from taxi.internal import dbh
from taxi.internal.tlogs_events import processor
from taxi.internal.tlogs_events import taximeter_balance_changes as events
from taxi.util import decimal


@pytest.mark.parametrize(
    'name,tlogs_class,last_created_at,event_handler_class,'
    'expected_amount_by_order_event_ref,'
    'expected_billing_orders_status_by_id', [
        (
            'taximeter_balance_changes',
            dbh.taximeter_balance_changes.Doc,
            datetime.datetime(2018, 8, 6),
            events.EventHandler,
            {
                'taxi/payment/card/5bc359433620c207ea14599d/1':
                    decimal.Decimal('183'),
                'taxi/payment/card/5bcf1f17910d3968f1b069db/1':
                    decimal.Decimal('1245'),
            },
            {
                'first': 'success',
                'no_contract': 'success',
            },
        ),
    ])
@pytest.mark.config(
    TLOGS_EVENTS_SLEEP_BEFORE_SEND=0,
    TLOGS_EVENTS_SLEEP_BETWEEN_SEND=0,
    TLOGS_EVENTS_SLEEP_BETWEEN_CHUNKS=0,
)
@pytest.mark.filldb(
    taximeter_balance_changes='for_test_events_processor',
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_events_processor(
        patch, name, tlogs_class, last_created_at, event_handler_class,
        expected_amount_by_order_event_ref,
        expected_billing_orders_status_by_id):
    if last_created_at:
        yield processor.INFO_BY_NAME[name].event_monitor(last_created_at=last_created_at)
    actual_amount_by_order_event_ref = {}

    @patch('taxi.external.billing_orders.send_doc')
    def send_doc(kind, external_event_ref, data, **kwargs):
        assert kind == 'order_paid'
        amount_str = data['payment_info']['ride_sum']
        actual_amount_by_order_event_ref[external_event_ref] = (
            decimal.Decimal(amount_str)
        )

    events_processor = processor.EventsProcessor(
        name=name,
        event_handler_class=event_handler_class,
    )
    yield events_processor.process_new_events()
    assert (
        actual_amount_by_order_event_ref ==
        expected_amount_by_order_event_ref
    )
    ids = list(expected_billing_orders_status_by_id)
    docs = yield tlogs_class.find_many_by_ids(ids)
    actual_billing_orders_status_by_id = {
        one_doc.pk: one_doc.billing_orders_status
        for one_doc in docs
    }
    assert (
        actual_billing_orders_status_by_id ==
        expected_billing_orders_status_by_id
    )


@pytest.mark.parametrize(
    'name,tlogs_class,last_created_at,event_handler_class,'
    'expected_flags_by_order_event_ref', [
        (
            'taximeter_balance_changes',
            dbh.taximeter_balance_changes.Doc,
            datetime.datetime(2018, 8, 6),
            events.EventHandler,
            {
                'taxi/payment/card/trust_payment_id_1/1':
                    (False, False),
                'taxi/payment/card/trust_payment_id_2/1':
                    (True, False),
                'taxi/payment/card/trust_payment_id_3/1':
                    (False, True),
                'taxi/payment/card/trust_payment_id_4/1':
                    (True, True),
            },
        ),
    ])
@pytest.mark.config(
    TLOGS_EVENTS_SLEEP_BEFORE_SEND=0,
    TLOGS_EVENTS_SLEEP_BETWEEN_SEND=0,
    TLOGS_EVENTS_SLEEP_BETWEEN_CHUNKS=0,
)
@pytest.mark.filldb(
    taximeter_balance_changes='for_test_flags',
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_flags(
        patch, name, tlogs_class, last_created_at, event_handler_class,
        expected_flags_by_order_event_ref):
    if last_created_at:
        yield processor.INFO_BY_NAME[name].event_monitor(last_created_at=last_created_at)
    actual_flags_by_order_event_ref = {}

    @patch('taxi.external.billing_orders.send_doc')
    def send_doc(kind, external_event_ref, data, **kwargs):
        assert kind == 'order_paid'
        actual_flags_by_order_event_ref[external_event_ref] = (
            data.get('write_ride_sum_fact_journal_only', False),
            data.get('write_tips_sum_fact_journal_only', False)
        )

    events_processor = processor.EventsProcessor(
        name=name,
        event_handler_class=event_handler_class,
    )
    yield events_processor.process_new_events()
    assert (
        actual_flags_by_order_event_ref ==
        expected_flags_by_order_event_ref
    )
