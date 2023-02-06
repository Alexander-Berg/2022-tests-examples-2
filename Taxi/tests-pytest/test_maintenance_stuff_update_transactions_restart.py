import pytest


from taxi.core import async
from taxi.core import db
from taxi_maintenance.stuff import update_transactions_restart


@pytest.inline_callbacks
def test_update_transactions(patch):
    py2_mock, transactions_mock = _patch_stq(patch)
    yield update_transactions_restart.update_transactions()
    count = yield db.pending_transactions.count()
    assert len(py2_mock.calls) == 3
    assert len(transactions_mock.calls) == 1
    assert count == 0


def _patch_stq(patch):
    @patch('taxi_stq.client.update_transactions_call')
    @async.inline_callbacks
    def update_transactions_call(order_id, log_extra=None):
        yield

    @patch('taxi_stq.client.transactions_events_call')
    def transactions_events_call(order_id, log_extra=None):
        yield

    return update_transactions_call, transactions_events_call
