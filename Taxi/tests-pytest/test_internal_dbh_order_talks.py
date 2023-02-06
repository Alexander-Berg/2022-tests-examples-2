import pytest

from taxi.core import async
from taxi.internal import dbh


@pytest.mark.filldb(order_talks='for_test_add_talks')
@async.inline_callbacks
def test_add_talks():
    assert (yield dbh.order_talks.Doc.add_talks(
        'forwarding-1', [{'forwarding_id': 'forwarding-1'}]))
    obj = yield dbh.order_talks.Doc.find_one_by_id('order')
    assert obj.talks[0].forwarding_id == 'forwarding-1'

    # Same talk second time
    assert (yield dbh.order_talks.Doc.add_talks(
        'forwarding-1', [{'forwarding_id': 'forwarding-1'}]))

    # Talk for forwarding that does not exist
    assert not (yield dbh.order_talks.Doc.add_talks(
        'forwarding-obsolete', [{'forwarding_id': 'forwarding-obsolete'}]))
