import pytest

from taxi.core import async
from taxi.internal import dbh
from taxi.internal.order_kit import event_handler


def _make_phone_doc():
    return {
        # should be the same phone_id as in
        # db_orders_for_take_feedback_test.json
        '_id': 'some_phone_id',
    }


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize(
    'has_performer,cancellable,user_cancellable,exc_expected',
    [
        (True, True, True, False),
        (True, False, True, True),
        (True, True, False, True),
        (True, False, False, True),
        (False, True, True, False),
    ]
)
@pytest.inline_callbacks
def test_check_can_cancel_order(
        monkeypatch, patch,
        has_performer, cancellable, user_cancellable, exc_expected):

    class Stub:
        order_id = 'order_id'
        user_position = object()
        driver_point = (37.6, 55.7)
        status = dbh.orders.STATUS_ASSIGNED
        taxi_status = dbh.orders.TAXI_STATUS_WAITING

        @staticmethod
        @async.inline_callbacks
        def mock_find_one_by_id(doc_id, secondary=False, fields=None):
            cls = dbh.orders.Doc
            yield
            doc = {
                cls._id: doc_id,
                cls.status: Stub.status,
                cls.taxi_status: Stub.taxi_status,
            }
            if has_performer:
                doc[cls.performer] = {
                    cls.performer.park_id.key: 'clid',
                    cls.performer.driver_uuid.key: 'uuid',
                }
            async.return_value(cls(doc))

        monkeypatch.setattr(
            dbh.orders.Doc, 'find_one_by_id', mock_find_one_by_id
        )

        @staticmethod
        @async.inline_callbacks
        def mock_proc_find_one_by_id(doc_id, secondary=False, fields=None):
            cls = dbh.order_proc.Doc
            yield
            proc = {cls._id: doc_id}
            async.return_value(cls(proc))

        monkeypatch.setattr(
            dbh.order_proc.Doc, 'find_one_by_id', mock_proc_find_one_by_id
        )

    @patch('taxi.internal.order_kit.cancel_handler.can_order_be_cancelled')
    def can_order_be_cancelled(order):
        return cancellable

    @patch('taxi.internal.order_kit.cancel_handler.can_be_cancelled_by_user')
    @async.inline_callbacks
    def can_be_cancelled_by_user(user_position, driver_point):
        yield
        assert user_position == Stub.user_position
        expected_point = Stub.driver_point if has_performer else None
        assert driver_point == expected_point
        async.return_value(user_cancellable)

    driver_point = Stub.driver_point if has_performer else None

    if exc_expected:
        with pytest.raises(event_handler.TooCloseToCancel):
            yield event_handler._check_can_cancel_order(
                Stub.order_id, Stub.user_position, driver_point
            )
    else:
        # Nothing is raised and nothing is returned
        resp = yield event_handler._check_can_cancel_order(
            Stub.order_id, Stub.user_position, driver_point
        )
        assert resp is None


@pytest.mark.filldb(_fill=False)
@pytest.inline_callbacks
def test_check_cant_cancel_cargo_order(monkeypatch):
    @staticmethod
    @async.inline_callbacks
    def mock_proc_find_one_by_id(doc_id, secondary=False, fields=None):
        order_proc = dbh.orders.Doc()
        yield
        order_proc._id = doc_id
        order_proc.order = dbh.orders.Doc()
        order_proc.order.request['cargo_ref_id'] = 'cargo_ref_id'
        async.return_value(order_proc)

    monkeypatch.setattr(
        dbh.order_proc.Doc, 'find_one_by_id', mock_proc_find_one_by_id
    )

    with pytest.raises(event_handler.CargoOrderNoCancellationByUser):
        yield event_handler._check_can_cancel_order('order_id', object(), None)
