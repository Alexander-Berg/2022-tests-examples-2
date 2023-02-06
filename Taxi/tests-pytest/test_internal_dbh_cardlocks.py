import pytest

from taxi.core import async
from taxi.internal import dbh


@pytest.inline_callbacks
def test_cardlocks():
    def acquire(order_id):
        return dbh.cardlocks.Doc.acquire(
            order_id, 'persistent_id', 100500, 1, set_unpaid=False
        )

    def release(order_id):
        return dbh.cardlocks.Doc.release_old(order_id)

    @async.inline_callbacks
    def can_make_orders():
        unpaid_orders_state = yield dbh.cardlocks.Doc.unpaid_orders_state(
            'persistent_id', 1,
        )
        async.return_value(unpaid_orders_state.can_make_credit_orders)

    yield acquire(1)
    yield acquire(2)
    yield acquire(3)
    assert (yield can_make_orders()) is True
    yield dbh.cardlocks.Doc.mark_unpaid(1, 'persistent_id')
    assert (yield can_make_orders()) is False
    with pytest.raises(dbh.cardlocks.RaceCondition):
        yield acquire(4)
    assert (yield release(1)) is False
    assert (yield can_make_orders()) is False
    with pytest.raises(dbh.cardlocks.RaceCondition):
        yield acquire(4)
    assert (yield release(2)) is False
    assert (yield release(3)) is True
    assert (yield can_make_orders()) is True
    yield acquire(4)


@pytest.inline_callbacks
def test_cardlocks_ok():
    def acquire(order_id):
        return dbh.cardlocks.Doc.acquire(
            order_id, 'persistent_id', 100500, 1, set_unpaid=False
        )

    def release(order_id):
        return dbh.cardlocks.Doc.release_old(order_id)

    yield acquire(1)
    assert (yield release(1))


@pytest.inline_callbacks
def test_cardlocks_ok_with_persitent_id():
    def acquire(order_id):
        return dbh.cardlocks.Doc.acquire(
            order_id, 'persistent_id', 100500, 1, set_unpaid=False
        )

    def release(order_id, persistent_id):
        return dbh.cardlocks.Doc.release_old(order_id, persistent_id)

    yield acquire(1)
    assert isinstance(
        (yield dbh.cardlocks.Doc.find_one_doc(1, 'persistent_id')),
        dbh.cardlocks.Doc
    )

    assert (yield release(1, 'bad_persistent_id'))
    assert isinstance(
        (yield dbh.cardlocks.Doc.find_one_doc(1, 'persistent_id')),
        dbh.cardlocks.Doc
    )

    assert (yield release(1, 'persistent_id'))
    try:
        assert isinstance(
            (yield dbh.cardlocks.Doc.find_one_doc(1, 'persistent_id')),
            dbh.cardlocks.Doc
        )
    except dbh.cardlocks.NotFound:
        assert True
    else:
        assert False


@pytest.inline_callbacks
def test_finished_unpaid_release():
    assert (yield dbh.cardlocks.Doc.release_old('non_existent')) is True
    assert (yield dbh.cardlocks.Doc.release_old('ok')) is True
    assert (yield dbh.cardlocks.Doc.release_old('broken')) is True
    ok_doc = yield dbh.cardlocks.Doc.find_one_by_id('ok_lock')
    assert ok_doc['x'] == []
    assert ok_doc['o'] == []

    broken_doc = yield dbh.cardlocks.Doc.find_one_by_id('broken_lock')
    assert broken_doc['x'] == []
    assert broken_doc['o'] == []

    assert (yield dbh.cardlocks.Doc.release_old('broken2')) is True
    broken_doc = yield dbh.cardlocks.Doc.find_one_by_id('broken_lock2')
    assert broken_doc['x'] == []
    assert broken_doc.get('o', []) == []

    assert (yield dbh.cardlocks.Doc.release_old('not_still_paid')) is False
    not_paid_doc = yield dbh.cardlocks.Doc.find_one_by_id('not_still_paid_lock')
    assert not_paid_doc['x'] == ['not_still_paid']
    assert not_paid_doc['o'] == ['1']

    assert (yield dbh.cardlocks.Doc.release_old('not_still_paid')) is False
    not_paid_doc = yield dbh.cardlocks.Doc.find_one_by_id('not_still_paid_lock')
    assert not_paid_doc['x'] == ['not_still_paid']
    assert not_paid_doc['o'] == ['1']


@pytest.inline_callbacks
@pytest.mark.filldb(cardlocks='empty')
def test_multiple_locks():
    yield dbh.cardlocks.Doc.acquire(
        'some-order-id', 'card-persistent-id-0', 100500, 1, set_unpaid=False
    )
    yield dbh.cardlocks.Doc.mark_unpaid(
        'some-order-id', 'card-persistent-id-0'
    )
    yield dbh.cardlocks.Doc.acquire(
        'some-order-id', 'card-persistent-id-1', 100500, 1, set_unpaid=False
    )
    yield dbh.cardlocks.Doc.mark_unpaid(
        'some-order-id', 'card-persistent-id-1'
    )
    assert len((yield dbh.cardlocks.Doc.find_many({
        dbh.cardlocks.Doc.unpaid_order_ids: {'$exists': True},
    }))) == 2
    assert (yield dbh.cardlocks.Doc.release_old('some-order-id')) is True
    assert len((yield dbh.cardlocks.Doc.find_many({
        ('%s.0' % dbh.cardlocks.Doc.unpaid_order_ids): {'$exists': True}
    }))) == 0
    assert len((yield dbh.cardlocks.Doc.find_many({
        ('%s.0' % dbh.cardlocks.Doc.unfinished_order_ids): {'$exists': True}
    }))) == 0
