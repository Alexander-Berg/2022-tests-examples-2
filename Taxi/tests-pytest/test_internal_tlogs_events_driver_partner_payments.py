# -*- coding: utf-8 -*-

import datetime

import pytest

from taxi.core import async
from taxi.internal.tlogs_events import driver_partner_payments as events
from taxi.util import dates
from taxi.util import decimal


class DummyYtClient:
    pass


@pytest.mark.parametrize(
    'last_created_at,expected_amount_by_order_event_ref,', [
        (
                datetime.datetime(2018, 8, 6),
                {
                    'taxi/driver_partner_payment/13241/1': decimal.Decimal(
                        '3241.05'),
                    'taxi/driver_partner_payment/23789/1': decimal.Decimal(
                        '6073.05'),
                    'taxi/driver_partner_payment/23789/2': decimal.Decimal(
                        '6738.90'),
                }
        ),
    ])
@pytest.mark.config(
    TLOGS_EVENTS_SLEEP_BEFORE_SEND=0,
    TLOGS_EVENTS_SLEEP_BETWEEN_SEND=0,
    TLOGS_EVENTS_SLEEP_BETWEEN_CHUNKS=0,
)
@pytest.mark.filldb(
    dbparks='for_test_events_processor',
    dbdrivers='for_test_events_processor',
    drivers='for_test_events_processor',
)
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_events_processor(
        patch, last_created_at,
        expected_amount_by_order_event_ref):
    yield events._INFO.event_monitor(last_created_at=last_created_at)
    actual_amount_by_order_event_ref = {}

    @patch('taxi.external.yt_wrapper.get_yt_mapreduce_clients')
    @async.inline_callbacks
    def get_yt_mapreduce_clients(*args, **kwargs):
        yield
        clients = [DummyYtClient()]
        async.return_value(clients)

    # workaround nonlocal in Py2
    class Context:
        called = False

    @patch('taxi.internal.driver_partner_payments.get_rows_newer_than_item')
    @async.inline_callbacks
    def get_rows_newer_than_item(*args, **kwargs):
        yield
        rows = [
            {
                'payment_batch_id': '13241',
                'version': 1,
                'park_id': '100504',
                'created': 1530004245,
                'currency': 'RUB',
                'delta': '3241.05',
                'eventtime': 1584910800,
                'payment_batch_description': 'П/п'
            },
            {
                'payment_batch_id': '23789',
                'version': 1,
                'park_id': '100502',
                'created': 1536604245,
                'currency': 'RUB',
                'delta': '6073.05',
                'eventtime': 1584910800,
                'payment_batch_description': 'test'
            },
            {
                'payment_batch_id': '23789',
                'version': 2,
                'park_id': '100500',
                'created': 1536604245,
                'currency': 'RUB',
                'delta': '6738.90',
                'payment_batch_description': (
                    'П/п номер такой-то, расчетный счет такой-то в таком-то '
                    'банке, Иванов Иван Иванович'
                ),
                'eventtime': 1536267600,
                'bank_order_id': '75632'
            }
        ] if not Context.called else []

        Context.called = True
        async.return_value(rows)

    @patch('taxi.external.billing_orders.send_doc')
    def send_doc(kind, external_event_ref, data, **kwargs):
        assert kind == 'driver_partner_payment'
        amount_str = data['driver_partner_payment_info']['amount']
        assert len(data['drivers']) == 1
        actual_amount_by_order_event_ref[external_event_ref] = (
            decimal.Decimal(amount_str)
        )

    events_processor = events.EventsProcessor()
    yield events_processor.process_new_events()
    assert (
            actual_amount_by_order_event_ref ==
            expected_amount_by_order_event_ref
    )

    recent_event = yield events._INFO.event_monitor.get_recent()
    assert recent_event['payment_batch_id'] == '23789'
    assert recent_event['version'] == 2
    assert int(
        dates.timestamp_us(recent_event['last_created_at'])) == 1536604245


@pytest.mark.config(
    BILLING_DRIVER_PARTNER_PAYMENTS_ENABLED=True,
    BILLING_DRIVER_PARTNER_PAYMENTS_CLID_SELECTOR={
        '__default__': '2025-01-01T00:00:00+00:00',
        '100504': '2020-01-01T00:00:00+00:00',
        '100500': '2020-01-01T00:00:00+00:00'}
)
@pytest.inline_callbacks
def test_events_driver_partner_payments_processing_switcher():
    handler = events.EventHandler()
    # New processing by clid selector rule
    doc = {
        'payment_batch_id': '13241',
        'version': 1,
        'park_id': '100504',
        'created': 1530004245,
        'currency': 'RUB',
        'delta': '3241.05',
        'eventtime': 1584910800,
        'payment_batch_description': 'П/п'
    }
    result = yield handler._new_processing_for_document(doc)
    assert result is True

    # Old processing by clid selector default rule
    doc = {
        'payment_batch_id': '23789',
        'version': 1,
        'park_id': '100502',
        'created': 1536604245,
        'currency': 'RUB',
        'delta': '6073.05',
        'eventtime': 1584910800,
        'payment_batch_description': 'test'
    }
    result = yield handler._new_processing_for_document(doc)
    assert result is False

    # Old processing by clid selector rule for this clid
    doc = {
        'payment_batch_id': '23789',
        'version': 2,
        'park_id': '100500',
        'created': 1536604245,
        'currency': 'RUB',
        'delta': '6738.90',
        'payment_batch_description': (
            'П/п номер такой-то, расчетный счет такой-то в таком-то '
            'банке, Иванов Иван Иванович'
        ),
        'eventtime': 1536267600,
        'bank_order_id': '75632'
    }
    result = yield handler._new_processing_for_document(doc)
    assert result is False
