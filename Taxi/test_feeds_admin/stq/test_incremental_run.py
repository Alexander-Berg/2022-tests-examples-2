from aiohttp import web
import pytest

from taxi.stq import async_worker_ng

from feeds_admin.db import publication_recipients
from feeds_admin.stq import feeds_admin_send
from test_feeds_admin import const


async def _run_feeds_admin_send_task(feed_id, run_id, stq3_context):
    # Can't use stq_runner.feeds_admin_send.call() here because
    # @patch will not work. Execute task manually
    task_info = async_worker_ng.TaskInfo(feed_id, 0, 0, queue='')
    await feeds_admin_send.task(
        stq3_context, task_info, feed_id=feed_id, run_id=run_id,
    )


async def _cleanup_recipients_table(feed_id, run_id, pgsql):
    # Cleanup recipients table because it will not be deleted automatically
    recipients_table = publication_recipients.get_pub_recipients_table_name(
        feed_id, run_id, publication_recipients.TableType.CUR_RECIPIENTS,
    )
    cursor = pgsql['feeds_admin'].cursor()
    cursor.execute(f'DROP TABLE {recipients_table}')


@pytest.mark.now('2022-01-01T00:00:00Z')
@pytest.mark.pgsql('feeds_admin', files=['incremental_run_yql.sql'])
async def test_compute_diff(
        stq3_context, mock_feeds, mock_publication_actions, mock_yql, pgsql,
):
    @mock_feeds('/v1/batch/create')
    async def _feeds_create(request):  # pylint: disable=W0612
        return web.json_response({'items': [], 'filtered': [], 'feed_ids': {}})

    @mock_feeds('/v1/remove_by_request_id')
    async def _feeds_remove_by_request_id(request):  # pylint: disable=W0612
        return web.json_response({})

    recipients_table = publication_recipients.get_pub_recipients_table_name(
        const.UUID_1, 1, publication_recipients.TableType.CUR_RECIPIENTS,
    )
    cursor = pgsql['feeds_admin'].cursor()

    # First run: all actions are CREATEs
    mock_yql(
        columns=['recipient_id', 'name'],
        rows=[['user1', 'name1'], ['user2', 'name2'], ['user3', 'name3']],
    )
    await _run_feeds_admin_send_task(const.UUID_1, 1, stq3_context)

    assert mock_publication_actions['create'] == [
        {'recipient_id': 'user1', 'payload_params': {'name': 'name1'}},
        {'recipient_id': 'user2', 'payload_params': {'name': 'name2'}},
        {'recipient_id': 'user3', 'payload_params': {'name': 'name3'}},
    ]
    assert mock_publication_actions['update'] == []
    assert mock_publication_actions['remove'] == []

    cursor.execute(f'SELECT count(*) FROM {recipients_table}')
    assert cursor.fetchone()[0] == 3

    # Next run: actions are CREATE, UPDATE, DELETE; user1 not changed
    mock_yql(
        columns=['recipient_id', 'name'],
        rows=[['user1', 'name1'], ['user2', 'upd'], ['user4', 'new']],
    )
    await _run_feeds_admin_send_task(const.UUID_1, 1, stq3_context)

    assert mock_publication_actions['create'] == [
        {'recipient_id': 'user4', 'payload_params': {'name': 'new'}},
    ]
    assert mock_publication_actions['update'] == [
        {'recipient_id': 'user2', 'payload_params': {'name': 'upd'}},
    ]
    assert mock_publication_actions['remove'] == [
        {'recipient_id': 'user3', 'payload_params': None},
    ]

    cursor.execute(f'SELECT count(*) FROM {recipients_table}')
    assert cursor.fetchone()[0] == 3

    await _cleanup_recipients_table(const.UUID_1, 1, pgsql)


@pytest.mark.now('2022-01-01T00:00:00Z')
@pytest.mark.pgsql('feeds_admin', files=['incremental_run_channels.sql'])
async def test_send_task(
        stq_runner, stq3_context, mock_feeds, mock_publication_actions, pgsql,
):
    @mock_feeds('/v1/batch/create')
    async def _feeds_create(request):  # pylint: disable=W0612
        return web.json_response({'items': [], 'filtered': [], 'feed_ids': {}})

    @mock_feeds('/v1/remove_by_request_id')
    async def _feeds_remove_by_request_id(request):  # pylint: disable=W0612
        return web.json_response({})

    await stq_runner.feeds_admin_send.call(
        args=(const.UUID_1,), kwargs={'run_id': 1},
    )

    feed_create_request = await _feeds_create.wait_call()
    request = feed_create_request['request'].json['items'][0]

    channels = {channel['channel'] for channel in request['channels']}
    assert channels == {'user:1', 'user:2', 'user:3'}

    await _cleanup_recipients_table(const.UUID_1, 1, pgsql)
