import datetime

import pytest

from taxi.internal import dbh


@pytest.mark.filldb(
    antifraud_orders_feedback='for_test_find_recent_by_statuses'
)
@pytest.mark.parametrize('statuses,min_updated,expected_ids', [
    (
            ['prepared'], datetime.datetime(2017, 12, 20),
            {'first_recent_prepared_id', 'second_recent_prepared_id'}
    ),
])
@pytest.inline_callbacks
def test_find_recent_by_statuses(statuses, min_updated, expected_ids):
    docs = yield dbh.antifraud_orders_feedback.Doc.find_recent_by_statuses(
        statuses, min_updated,
    )
    ids = set(dbh.antifraud_orders_feedback.Doc.get_ids(docs))
    assert ids == expected_ids
