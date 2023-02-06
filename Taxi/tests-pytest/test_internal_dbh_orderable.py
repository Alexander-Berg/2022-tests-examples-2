import pytest

from taxi.core import async
from taxi.internal import dbh


@pytest.mark.parametrize('order_id,expected_value', [
    ('some_order_id', 1.4),
])
@pytest.mark.filldb(
    orders='for_test_set_surge_price',
    order_proc='for_test_set_surge_price',
)
@pytest.inline_callbacks
def test_set_surge_price(order_id, expected_value):
    proc = yield dbh.order_proc.Doc.find_one_by_id(order_id)
    yield dbh.orderable.set_surge_price(proc, expected_value)

    order = yield _find_order(order_id)
    assert order.request.surge_price == expected_value
    proc = yield _find_proc(order_id)
    assert proc.order.request.surge_price == expected_value


@async.inline_callbacks
def _find_order(order_id_or_alias_id):
    query = {
        '$or': [
            {dbh.orders.Doc._id: order_id_or_alias_id},
            {dbh.orders.Doc.performer.taxi_alias.id: order_id_or_alias_id},
        ],
    }
    orders = yield dbh.orders.Doc.find_many(query)
    assert len(orders) == 1, query
    async.return_value(orders[0])


@async.inline_callbacks
def _find_proc(order_id_or_alias_id):
    proc_class = dbh.order_proc.Doc
    query = {
        '$or': [
            {dbh.order_proc.Doc._id: order_id_or_alias_id},
            {dbh.order_proc.Doc.aliases.id: order_id_or_alias_id},
        ],
    }
    procs = yield proc_class.find_many(query)
    assert len(procs) == 1, query
    async.return_value(procs[0])
