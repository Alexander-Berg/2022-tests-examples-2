import datetime

import pytest

from taxi.core import db
from taxi.internal import dbh


@pytest.inline_callbacks
def test_statuses():
    ids = yield dbh.bulk_notify_tasks.Doc.get_chunk_processed_ids('foo', 0)
    assert ids == set()
    statuses = [
        {
            'id': 0,
            'text': 'foo',
        },
        {
            'id': 1,
            'text': 'bar',
        },
        {
            'id': 2,
            'text': 'maurice',
        }
    ]
    yield dbh.bulk_notify_tasks.Doc.update_chunk_statuses('foo', 0, statuses)
    doc = yield db.bulk_notify_chunks.find_one('foo-0')
    assert doc == {
        '_id': 'foo-0',
        'task_id': 'foo',
        'statuses': statuses,
    }
    ids = yield dbh.bulk_notify_tasks.Doc.get_chunk_processed_ids('foo', 0)
    assert ids == {0, 1, 2}

    yield dbh.bulk_notify_tasks.Doc.cleanup_statuses('foo')
    doc = yield db.bulk_notify_chunks.find_one('foo-0')
    assert doc is None


@pytest.inline_callbacks
def test_all_statuses():
    yield dbh.bulk_notify_tasks.Doc.update_chunk_statuses(
        'foo', 0,
        [{'id': 0}, {'id': 1}]
    )
    yield dbh.bulk_notify_tasks.Doc.update_chunk_statuses(
        'foo', 1,
        [{'id': 2}, {'id': 3}]
    )

    all_statuses = yield dbh.bulk_notify_tasks.Doc.get_statuses('foo')
    all_statuses.sort()
    assert all_statuses == [
        {'id': 0}, {'id': 1}, {'id': 2}, {'id': 3}
    ]


@pytest.mark.now('2016-10-11 13:00:00+03')
@pytest.inline_callbacks
def test_basic_workflow():
    task_id = yield dbh.bulk_notify_tasks.Doc.create_task(
        'test task', created_by='pytest', text='hello, world!')
    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    assert task.status == dbh.bulk_notify_tasks.STATUS_NEW
    assert task.name == 'test task'
    assert task.created_by == 'pytest'
    assert task.text == 'hello, world!'

    status = yield dbh.bulk_notify_tasks.Doc.attach_source_data(
        task_id, 'source-mds-path', 'original-filename'
    )
    assert status
    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    assert task.status == dbh.bulk_notify_tasks.STATUS_SOURCE_UPLOADED
    assert task.mds_source_path == 'source-mds-path'
    assert task.source_filename == 'original-filename'

    status = yield dbh.bulk_notify_tasks.Doc.attach_data(
        task_id, 'dummy-mds-path', 1000, chunks=[{
            'offset_start': 0,
            'offset_end': 100000,
        }], source_errors=123
    )
    assert status
    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    assert task.status == dbh.bulk_notify_tasks.STATUS_READY
    assert task.mds_data_path == 'dummy-mds-path'
    assert task.stat.total == 1000
    assert task.stat.source_errors == 123
    assert len(task.chunks) == 1

    status = yield dbh.bulk_notify_tasks.Doc.schedule_task(
        task_id, datetime.datetime.utcnow()
    )
    assert status
    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    assert task.status == dbh.bulk_notify_tasks.STATUS_STARTED
    assert task.start == datetime.datetime(2016, 10, 11, 10)
    assert task.mds_data_path

    status = yield dbh.bulk_notify_tasks.Doc.mark_as_running(task_id)
    assert status
    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    assert task.status == dbh.bulk_notify_tasks.STATUS_RUNNING

    status = yield dbh.bulk_notify_tasks.Doc.update_progress(
        task_id, 0, is_finished=True, processed=100, failed=3)
    assert status
    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    assert task.status == dbh.bulk_notify_tasks.STATUS_RUNNING
    assert task.stat.processed == 100
    assert task.stat.failed == 3
    assert task.chunks[0].is_finished

    status = yield dbh.bulk_notify_tasks.Doc.finish_task(
        task_id, 'mds-dummy-statuses', processed=100, failed=3)
    assert status
    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    assert task.status == dbh.bulk_notify_tasks.STATUS_FINISHED
    assert task.mds_statuses_path == 'mds-dummy-statuses'
    assert task.stat.processed == 100
    assert task.stat.failed == 3
