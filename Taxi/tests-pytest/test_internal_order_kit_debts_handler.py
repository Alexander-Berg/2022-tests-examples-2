import datetime

import pytest

from taxi.core import async
from taxi.internal.order_kit import debts_handler


@pytest.mark.config(DEBTS_ENABLED_PROCESSING_PY2=False)
@pytest.inline_callbacks
def test_debt_disabled(patch):
    order_id = 'order_id'

    @patch('taxi_stq.client.debts_processing_call')
    @async.inline_callbacks
    def _debts_processing(order, event, event_time, eta=0,
                          reason_code=None, log_extra=None):
        pytest.fail('should not be called')

    yield debts_handler.record_debt(order_id)
    assert len(_debts_processing.calls) == 0


@pytest.mark.config(DEBTS_ENABLED_PROCESSING_PY2=True)
@pytest.inline_callbacks
def test_record_debt(patch):
    order_id = 'order_id'

    @patch('taxi_stq.client.debts_processing_call')
    @async.inline_callbacks
    def _debts_processing(order, event, event_time, eta=0,
                          reason_code=None, locked_phone_id=None,
                          log_extra=None):
        assert order == order_id
        assert event == 'set_debt'
        yield

    yield debts_handler.record_debt(order_id)
    assert len(_debts_processing.calls) == 1


@pytest.mark.config(DEBTS_ENABLED_PROCESSING_PY2=True)
@pytest.inline_callbacks
def test_release_debt(patch):
    order_id = 'order_id'

    @patch('taxi_stq.client.debts_processing_call')
    @async.inline_callbacks
    def _debts_processing(order, event, event_time, eta=0,
                          reason_code=None, locked_phone_id=None,
                          log_extra=None):
        assert order == order_id
        assert event == 'reset_debt'
        assert reason_code == 'moved_to_cash'
        yield

    yield debts_handler.release_debt(order_id, 'moved_to_cash')
    assert len(_debts_processing.calls) == 1


@pytest.mark.config(DEBTS_ENABLED_PROCESSING_PY2=True)
@pytest.inline_callbacks
def test_debts_processing_event_time(patch, sleep):
    order_id = 'order_id'

    class EventTimeFixture:
        last_event_time = datetime.datetime.utcnow()

    @patch('taxi_stq.client.debts_processing_call')
    @async.inline_callbacks
    def _debts_processing(order, event, event_time, eta=0,
                          reason_code=None, locked_phone_id=None,
                          log_extra=None):
        assert order == order_id
        assert EventTimeFixture.last_event_time < event_time
        EventTimeFixture.last_event_time = event_time
        yield

    yield sleep(1)
    yield debts_handler.release_debt(order_id, 'moved_to_cash')
    yield sleep(1)
    yield debts_handler.record_debt(order_id)
    yield sleep(1)
    yield debts_handler.release_debt(order_id, 'paid')
    yield sleep(1)
    yield debts_handler.record_debt(order_id)
    yield sleep(1)
    yield debts_handler.record_debt(order_id)
    yield sleep(1)
    yield debts_handler.release_debt(order_id, 'by_admin')
    yield sleep(1)
    yield debts_handler.release_debt(order_id, 'by_admin')
