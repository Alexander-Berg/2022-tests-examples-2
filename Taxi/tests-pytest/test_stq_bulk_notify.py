import pytest

from taxi.core import async
from taxi.internal import dbh

from taxi_stq.tasks.bulk_notify import send_task
from taxi_stq.tasks.bulk_notify import finish_task


@pytest.mark.parametrize('task_id,chunk_id,fail_ids,failed,processed', [
    ('running', 0, {}, 0, 10000),
    ('running', 0, {13, 17, 19}, 3, 10000),
])
@pytest.inline_callbacks
def test_send_notifications_chunk(
        patch, task_id, chunk_id, fail_ids, failed, processed):
    @patch('taxi_stq.tasks.bulk_notify.send_task.mds_fetch_chunk')
    @async.inline_callbacks
    def mds_fetch_chunk(task, chunk_id, log_extra=None):
        yield
        chunk = task.chunks[chunk_id]
        result = []
        for item_id in xrange(chunk.offset_start // 100,
                              chunk.offset_end // 100):
            result.append({'id': item_id})
        async.return_value(result)

    @patch('taxi_stq.tasks.bulk_notify.send_task._send_notification')
    @async.inline_callbacks
    def send_notification(item, log_extra=None):
        yield
        if item['id'] in fail_ids:
            async.return_value({
                'status': dbh.bulk_notify_tasks.ITEM_STATUS_FAILED,
            })
        async.return_value({
            'status': dbh.bulk_notify_tasks.ITEM_STATUS_COMPLETE,
        })

    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    yield send_task._send_notifications_chunk(task, chunk_id)

    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    assert task.stat.failed == failed
    assert task.stat.processed == processed
    assert task.chunks[chunk_id].is_finished


@pytest.mark.parametrize('task_id,processed,failed', [
    ('chunks-finished', 1000, 0),
    ('chunks-finished', 1000, 3),
])
@pytest.mark.asyncenv('blocking')
@pytest.inline_callbacks
def test_finish_task(patch, task_id, processed, failed):
    @patch('taxi.internal.dbh.bulk_notify_tasks.Doc.get_statuses')
    @async.inline_callbacks
    def get_statuses(task_id, chunk_id=None):
        yield
        result = [
            {'status': dbh.bulk_notify_tasks.ITEM_STATUS_FAILED}
        ] * failed
        result += [
            {'status': dbh.bulk_notify_tasks.ITEM_STATUS_COMPLETE}
        ] * (processed - failed)
        async.return_value(result)

    @patch('taxi_stq.tasks.bulk_notify.finish_task._mds_upload_statuses')
    @async.inline_callbacks
    def mds_upload_statuses(task, statistics, log_extra=None):
        statistics.total = processed
        statistics.failed = failed
        yield
        async.return_value('statuses.csv')

    yield finish_task._task(task_id)

    task = yield dbh.bulk_notify_tasks.Doc.find_one_by_id(task_id)
    assert task.status == dbh.bulk_notify_tasks.STATUS_FINISHED
    assert task.mds_statuses_path == 'statuses.csv'
    assert task.stat.processed == processed
    assert task.stat.failed == failed


@pytest.inline_callbacks
def test_send_notification_communication(patch):
    send_calling_params = {}

    @patch('taxi.external.communications.send_user_push')
    @async.inline_callbacks
    def send_user_push(
            user, data, tvm_src_service_name, intent=None,
            confirm=False, log_extra=None
    ):
        send_calling_params['client'] = 'yauber'
        yield
        async.return_value()

    item = {
        'id': 'item_id',
        'payload': {},
        'text': 'test text',
        'user_id': 'test_user_id',
    }
    yield send_task._send_notification_communication(item)
    assert send_calling_params['client'] == 'yauber'
