import datetime

import pytest

from taxi.internal import dbh


NOW = datetime.datetime(2018, 3, 25, 20, 0, 0)


@pytest.mark.parametrize(
    'task_id,from_date,to_date,metrics,expected_task_doc',
    [
        (
            'new_task',
            datetime.datetime(2018, 3, 25, 20, 3, 0),
            datetime.datetime(2018, 3, 25, 20, 4, 0),
            {'foo': 1},
            dbh.taximeter_balance_changes_update_tasks.Doc({
                '_id': 'new_task',
                'finished_at': NOW,
                'from_date': datetime.datetime(2018, 3, 25, 20, 3, 0),
                'to_date': datetime.datetime(2018, 3, 25, 20, 4, 0),
                'metrics': {'foo': 1},
            }),
        ),
    ]
)
@pytest.mark.filldb
@pytest.mark.now(NOW.isoformat())
@pytest.inline_callbacks
def test_new_task(
        patch, task_id, from_date, to_date, metrics, expected_task_doc):
    task_doc_cls = dbh.taximeter_balance_changes_update_tasks.Doc
    if expected_task_doc is None:
        with pytest.raises(
                dbh.taximeter_balance_changes_update_tasks.RaceCondition):
            yield task_doc_cls.new_task(task_id, from_date, to_date, metrics)
    else:
        task_doc = yield task_doc_cls.new_task(
            task_id, from_date, to_date, metrics)
        assert task_doc == expected_task_doc
