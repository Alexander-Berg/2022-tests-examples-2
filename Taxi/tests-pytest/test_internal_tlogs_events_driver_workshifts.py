import datetime

import pytest

from taxi.internal import dbh
from taxi.internal.tlogs_events import processor
from taxi.internal.tlogs_events import driver_workshifts as events
from taxi.util import decimal
from taxi_maintenance import run


@pytest.mark.parametrize(
    'name,tlogs_class,last_created_at,event_handler_class,partition,'
    'expected_amount_by_order_event_ref,'
    'expected_billing_orders_status_by_id', [
        (
            'driver_workshifts',
            dbh.driver_workshifts.Doc,
            datetime.datetime(2018, 8, 6),
            events.EventHandler,
            None,
            {
                'taxi/workshift/400000005909_de257d9ca00c4155b36421b283fa2b19:12':
                    decimal.Decimal('419')
            },
            {
                'first': 'success',
            },
        ),
        (
            'driver_workshifts',
            dbh.driver_workshifts.Doc,
            datetime.datetime(2018, 8, 6),
            events.EventHandler,
            run.JobPartition(index=0, total=4),
            {
                'taxi/workshift/400000005909_de257d9ca00c4155b36421b283fa2b19:12':
                    decimal.Decimal('419')
            },
            {
                'first': 'success',
            },
        ),
    ])
@pytest.mark.config(
    TLOGS_EVENTS_SLEEP_BEFORE_SEND=0,
    TLOGS_EVENTS_SLEEP_BETWEEN_SEND=0,
    TLOGS_EVENTS_SLEEP_BETWEEN_CHUNKS=0,
)
@pytest.mark.filldb(
    driver_workshifts='for_test_events_processor',
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_events_processor(
        patch, name, tlogs_class, last_created_at, event_handler_class,
        partition,
        expected_amount_by_order_event_ref,
        expected_billing_orders_status_by_id):
    if last_created_at:
        yield processor.INFO_BY_NAME[name].event_monitor(last_created_at=last_created_at)
    actual_amount_by_order_event_ref = {}

    @patch('taxi.external.billing_orders.send_doc')
    def send_doc(kind, external_event_ref, data, **kwargs):
        assert kind == 'workshift_bought'
        amount_str = data['workshift_info']['price']
        actual_amount_by_order_event_ref[external_event_ref] = (
            decimal.Decimal(amount_str)
        )

    events_processor = processor.EventsProcessor(
        name=name,
        event_handler_class=event_handler_class,
        partition=partition,
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
