# pylint: disable=no-self-use,redefined-outer-name,too-many-statements
# pylint: disable=too-many-locals,too-many-arguments,too-many-branches
# pylint: disable=too-many-lines, no-member, unused-variable
import datetime
import random

import bson
import pytest

from taxi.clients import startrack
from taxi.clients import support_chat

from chatterbox import stq_task
from chatterbox.crontasks import archive_closed_chats
from chatterbox.internal import task_source

CHATS_LAST_UPDATED = datetime.datetime(2018, 5, 7, 12, 34, 56)
NOW = datetime.datetime(2018, 5, 7, 12, 44, 56)


@pytest.mark.config(
    ZENDESK_STQ_DELAY_AFTER_TIMEOUT=321,
    STARTRACK_EXPORT_MAX_DELAY=123,
    CHATTERBOX_ZENDESK_STQ_ARCHIVE_MAX_DELAY=456,
    STARTRACK_TICKET_IMPORT=True,
    ZENDESK_COUNTRY_TO_GROUP_ID_MAP={
        'yataxi': {'rus': 123, '__default__': 456},
    },
    CHATTERBOX_FORBIDDEN_EXTERNAL_REQUESTS={
        'bank': {'__default__': False, 'archiving': True},
    },
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    (
        'enqueue_limit',
        'expected_startrack_task_ids',
        'expected_startrack_ok',
        'expected_add_update_calls',
        'expected_stq_put_delays',
    ),
    [
        # All tasks via stq
        (
            100,
            [
                'must_be_archived',
                'must_also_be_archived',
                'driver_must_be_archived',
                'yutaxi_ticket_id',
                bson.ObjectId('5b2cae5cb2682a976914c2a6'),
            ],
            [True, True, True, True, True],
            5,
            [0, 0, 0, 0, 0],
        ),
        # Low enqueue limit, via stq
        (
            2,
            ['must_be_archived', 'must_also_be_archived'],
            [True, True],
            2,
            [0, 0],
        ),
    ],
)
async def test_archive(
        cbox_context,
        monkeypatch,
        mock,
        loop,
        stq,
        mock_get_chat,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_update_ticket,
        mock_st_get_all_attachments,
        mock_st_get_attachment,
        mock_st_import_ticket,
        mock_st_import_comment,
        mock_st_import_file,
        mock_source_download_file,
        mock_dealapp_send_chat,
        mock_personal,
        mock_translate,
        patch_aiohttp_session,
        response_mock,
        enqueue_limit,
        expected_startrack_task_ids,
        expected_startrack_ok,
        expected_add_update_calls,
        expected_stq_put_delays,
):
    startrack_ticket = {
        'key': 'TESTQUEUE-1',
        'self': 'tracker/TESTQUEUE-1',
        'createdAt': '2018-05-05T12:34:56',
        'updatedAt': '2018-05-05T14:34:56',
        'status': {'key': 'open'},
    }
    mock_st_import_ticket(startrack_ticket)

    startrack_comment = {
        'id': 'some_imported_comment_id',
        'key': 'dummy',
        'self': 'tracker/TESTQUEUE-1/comments/dummy',
    }
    mock_st_import_comment(startrack_comment)
    mock_dealapp_send_chat({})
    cbox_context.data.config.CHATTERBOX_ZENDESK_STQ_ARCHIVE_ENQUEUE_LIMIT = (
        enqueue_limit
    )

    mock_st_get_comments([])
    mock_st_update_ticket('open')
    mock_st_get_all_attachments(empty=False)

    def _dummy_randint(min_value, max_value):
        return max_value

    @mock
    async def _dummy_reschedule(queue, *args, **kwargs):
        pass

    monkeypatch.setattr(random, 'randint', _dummy_randint)

    async def _dummy_get_history(self, chat_id, *args, **kwargs):
        if not chat_id.startswith('some_user_chat_message_id'):
            raise support_chat.NotFoundError
        return {
            'messages': [
                {
                    'id': 1,
                    'sender': {'id': 'user_id', 'role': 'client'},
                    'text': 'text',
                    'metadata': {
                        'created': '2018-05-05T15:34:56',
                        'attachments': [{'id': 'some_attachment_id'}],
                    },
                },
            ],
        }

    def _get_id(_id):
        if isinstance(_id, str):
            return _id
        return _id['$oid']

    @mock
    async def _dummy_add_update(*args, **kwargs):
        pass

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_history', _dummy_get_history,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    await archive_closed_chats.do_stuff(cbox_context, loop)

    assert stq.startrack_ticket_import_queue.times_called == len(
        expected_startrack_task_ids,
    )
    for task_id in expected_startrack_task_ids:
        stq_call = stq.startrack_ticket_import_queue.next_call()
        assert _get_id(stq_call['args'][0]) == str(task_id)
        assert stq_call['kwargs']['primary']

    assert stq.chatterbox_archive_autoreply_request.times_called == len(
        expected_startrack_task_ids,
    )
    for task_id in expected_startrack_task_ids:
        stq_call = stq.chatterbox_archive_autoreply_request.next_call()
        assert _get_id(stq_call['args'][0]) == str(task_id)

    for task_id, call_ok in zip(
            expected_startrack_task_ids, expected_startrack_ok,
    ):
        kwargs = {'action': 'archive'}

        if call_ok:
            await stq_task.startrack_ticket_import(
                cbox_context.data, task_id, **kwargs,
            )
            inner_comments = []
            public_messages = []
            await stq_task.startrack_comment_import(
                cbox_context.data,
                task_id,
                {'key': 'SOMEQUEUE-1'},
                inner_comments,
                public_messages,
                **kwargs,
            )
        else:
            with pytest.raises(task_source.BaseError):
                await stq_task.startrack_ticket_import(
                    cbox_context.data, task_id, **kwargs,
                )

    chats = cbox_context.data.db.support_chatterbox.find()
    chats_by_id = {chat['_id']: chat async for chat in chats}
    for chat in chats_by_id.values():
        if chat['_id'] == 'must_be_in_progress':
            assert chat['status'] == 'in_progress'
            assert chat['updated'] == CHATS_LAST_UPDATED
        elif chat['_id'] == 'is_still_archiving':
            assert chat['status'] == 'archive_in_progress'
            assert chat['updated'] == CHATS_LAST_UPDATED
        elif chat['_id'] == 'already_archived':
            assert chat['status'] == 'archived'
            assert chat['updated'] == CHATS_LAST_UPDATED
        elif chat['_id'] not in expected_startrack_task_ids:
            assert chat['updated'] < NOW
        elif chat['_id'] == 'must_be_rearchived':
            assert chat['status'] == 'archived'
            assert chat['updated'] == NOW
        elif chat['_id'] == 'must_fail_support_chat':
            assert chat['status'] == 'archive_in_progress'
            assert chat['updated'] == NOW
        elif chat['_id'] == 'yutaxi_ticket_id':
            assert chat['status'] == 'archived'
        elif chat['_id'] == 'must_not_be_archived':
            assert chat['status'] == 'ready_to_archive'
        else:
            assert chat['status'] == 'archived'
            assert chat['updated'] == NOW

    assert stq.startrack_comment_import_queue.times_called == len(
        expected_stq_put_delays,
    )
    for delay in expected_stq_put_delays:
        call = stq.startrack_comment_import_queue.next_call()
        assert max((call['eta'] - NOW).total_seconds(), 0) == delay

    assert len(_dummy_add_update.calls) == expected_add_update_calls
    download_file_calls = mock_source_download_file.calls
    assert len(download_file_calls) == len(expected_startrack_task_ids)
    for task_id, download_file_call in zip(
            expected_startrack_task_ids, download_file_calls,
    ):
        assert download_file_call['args'][1:] == (
            {'id': 'some_attachment_id'},
            'user_id',
            'client',
        )

    for task_id in expected_startrack_task_ids:
        async with cbox_context.data.pg_master_pool.acquire() as conn:
            result = await conn.fetch(
                'SELECT * FROM chatterbox.supporter_tasks WHERE task_id = $1',
                str(task_id),
            )
            assert not result


@pytest.mark.filldb(support_chatterbox='already_failed')
@pytest.mark.config(CHATTERBOX_ZENDESK_STQ_ARCHIVE_PERCENTAGE=100)
@pytest.mark.parametrize(
    'task_id',
    ['startrack_already_failed', 'startrack_primary_already_failed'],
)
async def test_startrack_already_failed(cbox, monkeypatch, task_id):
    async def _single_request(self, *args, **kwargs):
        raise RuntimeError

    monkeypatch.setattr(
        startrack.StartrackAPIClient, '_single_request', _single_request,
    )
    await stq_task.startrack_ticket_import(cbox.app, task_id, action='archive')


@pytest.mark.filldb(support_chatterbox='twice_archived')
@pytest.mark.config(CHATTERBOX_ZENDESK_STQ_ARCHIVE_PERCENTAGE=100)
@pytest.mark.parametrize(
    'action, task_id, expected_status',
    [
        ('copy', 'startrack_twice_archived', 'archive_in_progress'),
        ('archive', 'startrack_twice_archived', 'archived'),
    ],
)
async def test_startrack_twice_archived(
        cbox, monkeypatch, action, task_id, expected_status,
):
    async def _single_request(self, *args, **kwargs):
        raise RuntimeError

    monkeypatch.setattr(
        startrack.StartrackAPIClient, '_single_request', _single_request,
    )
    await stq_task.startrack_ticket_import(cbox.app, task_id, action=action)

    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    assert task['status'] == expected_status


@pytest.mark.filldb(support_chatterbox='market_chat')
@pytest.mark.parametrize(
    ('expected_market_task_ids', 'expected_market_stq_queue'),
    [(['market_task_1'], 'chatterbox_send_archive_ticket_to_market')],
)
async def test_archive_market_chat_type(
        cbox_context,
        stq,
        mock,
        loop,
        expected_market_task_ids,
        expected_market_stq_queue,
):
    await archive_closed_chats.do_stuff(cbox_context, loop)

    for task_id in expected_market_task_ids:
        call = stq.chatterbox_send_archive_ticket_to_market.next_call()
        assert call['args'][0] == task_id

    assert not stq.chatterbox_send_archive_ticket_to_market.has_calls


@pytest.mark.filldb(support_chatterbox='dealapp')
@pytest.mark.config(DEALAPP_STARTRACK_QUEUES=['TEST_QUEUE'])
@pytest.mark.parametrize(
    'expected_dealapp_task_ids',
    (
        [
            'must_be_send_client_eats_app',
            'must_be_send_client_eats',
            'must_be_send_service_eats',
            'must_be_send_startrack',
        ],
    ),
)
async def test_dealapp_chats(
        cbox_context,
        stq,
        mock,
        loop,
        mock_st_get_comments,
        mock_st_update_ticket,
        mock_st_get_all_attachments,
        expected_dealapp_task_ids,
):
    mock_st_get_comments([])
    mock_st_update_ticket('open')
    mock_st_get_all_attachments(empty=False)

    await archive_closed_chats.do_stuff(cbox_context, loop)

    assert stq.chatterbox_send_to_dealapp_task.times_called == len(
        expected_dealapp_task_ids,
    )
    for task_id in expected_dealapp_task_ids:
        call = stq.chatterbox_send_to_dealapp_task.next_call()
        assert call['id'] == task_id
    assert not stq.chatterbox_send_to_dealapp_task.has_calls


@pytest.mark.filldb(support_chatterbox='different_queues')
@pytest.mark.config(
    ZENDESK_STQ_DELAY_AFTER_TIMEOUT=321,
    STARTRACK_EXPORT_MAX_DELAY=123,
    CHATTERBOX_ZENDESK_STQ_ARCHIVE_MAX_DELAY=456,
    STARTRACK_TICKET_IMPORT=True,
    STARTRACK_SUPPORT_ARCHIVE_QUEUE_BY_LINE={
        '__default__': 'YANDEXTAXI',
        'eats': 'EDASUPPORT',
    },
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ('task_id', 'expected_queue', 'expected_comment_key'),
    [
        ('first_line_task', 'YANDEXTAXI', 'YANDEXTAXI-1'),
        ('eats_line_task', 'EDASUPPORT', 'EDASUPPORT-1'),
        ('second_line_task', 'YANDEXTAXI', 'YANDEXTAXI-1'),
    ],
)
async def test_archive_different_queues(
        cbox_context,
        stq,
        monkeypatch,
        mock,
        loop,
        mock_get_chat,
        mock_st_update_ticket,
        mock_st_import_comment,
        task_id,
        expected_queue,
        expected_comment_key,
        patch_aiohttp_session,
        tracker_url,
        response_mock,
):
    startrack_ticket = {
        'key': 'TESTQUEUE-1',
        'self': 'tracker/TESTQUEUE-1',
        'createdAt': '2018-05-05T12:34:56',
        'updatedAt': '2018-05-05T14:34:56',
        'status': {'key': 'open'},
    }

    @patch_aiohttp_session(tracker_url + 'issues/_import', 'POST')
    def import_ticket(method, url, **kwargs):
        assert kwargs['json']['queue']['key'] == expected_queue
        startrack_ticket['key'] = '%s-1' % expected_queue
        return response_mock(json=startrack_ticket, status=200)

    async def _dummy_get_history(self, chat_id, *args, **kwargs):
        return {
            'messages': [
                {
                    'sender': {'id': 'user_id', 'role': 'client'},
                    'text': 'text',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
            ],
        }

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_history', _dummy_get_history,
    )

    await stq_task.startrack_ticket_import(
        cbox_context.data, task_id, action='archive',
    )

    stq_call = stq.startrack_comment_import_queue.next_call()
    assert stq_call['args'][1]['key'] == expected_comment_key
    assert not stq.startrack_comment_import_queue.has_calls
