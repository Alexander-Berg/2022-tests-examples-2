from __future__ import unicode_literals

import pytest

from taxi.core import db
from taxi_maintenance.stuff import cleanup_minutely


@pytest.mark.now('2018-05-22T11:00:00')
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_cleanup_nothing_to_do():
    yield cleanup_minutely.do_stuff()
    orders_n = yield db.orders.count()
    assert orders_n == 2


@pytest.mark.now('2018-05-22T11:02:00')
@pytest.inline_callbacks
@pytest.mark.asyncenv('blocking')
def test_cleanup_remove_one_draft():
    draft_order = yield db.orders.find_one('order_in_draft_state')
    assert draft_order is not None

    yield cleanup_minutely.do_stuff()

    orders_n = yield db.orders.count()
    assert orders_n == 1  # 1 draft was removed

    cancelled_order = yield db.orders.find_one('cancelled_order')
    assert cancelled_order is not None

    draft_order = yield db.orders.find_one('order_in_draft_state')
    assert draft_order is None
