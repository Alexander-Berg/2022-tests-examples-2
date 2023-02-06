# pylint: disable=too-many-lines, too-many-arguments, redefined-outer-name
# pylint: disable=unused-variable, too-many-locals
import datetime
import http
import os
import tempfile

import bson
import pytest

from taxi import discovery
from taxi.clients import support_chat
from taxi.util import dates

from chatterbox import stq_task
from chatterbox.internal import tasks_manager
from test_chatterbox import plugins as conftest

NOW = datetime.datetime(2018, 6, 15, 12, 34)
SECONDS_IN_DAY = datetime.timedelta(days=1).total_seconds()


@pytest.mark.now(NOW.isoformat())
async def test_hidden_comment(cbox, mock_random_str_uuid):
    test_action_id = mock_random_str_uuid()
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a1/hidden_comment',
        data={
            'hidden_comment': 'some test inner comment',
            'themes': ['1', '2'],
            'themes_tree': ['1', '2'],
            'hidden_comment_metadata': {'field': 'value'},
        },
    )
    assert cbox.status == http.HTTPStatus.OK
    assert test_action_id.calls
    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId('5b2cae5cb2682a976914c2a1')},
    )
    assert task['inner_comments'] == [
        {
            'comment': 'some test inner comment',
            'login': 'superuser',
            'created': NOW,
            'field': 'value',
        },
    ]
    assert task['history'] == [
        {
            'action_id': 'test_uid',
            'action': 'hidden_comment',
            'created': NOW,
            'login': 'superuser',
            'line': 'first',
            'hidden_comment': 'some test inner comment',
            'in_addition': False,
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'themes',
                    'value': [1, 2],
                },
                {
                    'change_type': 'set',
                    'field_name': 'theme_name',
                    'value': 'Theme::Subtheme 1',
                },
                {
                    'change_type': 'set',
                    'field_name': 'themes_tree',
                    'value': [1, 2],
                },
            ],
            'tags_changes': [
                {'change_type': 'add', 'tag': '3'},
                {'change_type': 'add', 'tag': '4'},
            ],
        },
    ]


@pytest.mark.config(
    CHATTERBOX_EXTERNAL_SALESFORCE={
        'get_metadata': {'test_key': 'test_meta_key'},
    },
)
@pytest.mark.parametrize(
    (
        'task_id',
        'data',
        'headers',
        'chat_status',
        'expected_status',
        'expected_inner_comments',
        'expected_metadata',
        'expected_history',
    ),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {'comment': 'some external response comment'},
            {'X-API-Key': 'right_key', 'X-Client-ID': 'right_client_id'},
            None,
            http.HTTPStatus.OK,
            [
                {
                    'comment': 'some external response comment',
                    'created': NOW,
                    'login': 'superuser',
                    'type': 'external_response',
                },
            ],
            {'city': 'Moscow', 'queue': 'some_queue'},
            [
                {
                    'action': 'reopen',
                    'created': NOW,
                    'line': 'first',
                    'login': 'superuser',
                },
                {
                    'action': 'external_response',
                    'created': NOW,
                    'hidden_comment': 'some external response comment',
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                },
            ],
        ),
        (
            '5a2cae5cb2682a976914c2a1',
            {'comment': 'some external response comment'},
            {'X-API-Key': 'right_key', 'X-Client-ID': 'right_client_id'},
            None,
            http.HTTPStatus.OK,
            [
                {
                    'comment': 'some external response comment',
                    'created': NOW,
                    'login': 'superuser',
                    'type': 'external_response',
                },
            ],
            {'city': 'Moscow', 'queue': 'some_queue'},
            [
                {
                    'action': 'user_communicate',
                    'created': NOW,
                    'line': 'vip',
                    'login': 'superuser',
                },
                {
                    'action': 'external_response',
                    'created': NOW,
                    'hidden_comment': 'some external response comment',
                    'in_addition': False,
                    'line': 'vip',
                    'login': 'superuser',
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'some external response comment',
                'metadata': {
                    'test_key': 'test_value',
                    'test_key_2': 'test_value_2',
                },
            },
            {'X-API-Key': 'right_key', 'X-Client-ID': 'right_client_id'},
            None,
            http.HTTPStatus.OK,
            [
                {
                    'comment': 'some external response comment',
                    'created': NOW,
                    'login': 'superuser',
                    'type': 'external_response',
                },
            ],
            {
                'city': 'Moscow',
                'queue': 'some_queue',
                'test_meta_key': 'test_value',
            },
            [
                {
                    'action': 'reopen',
                    'created': NOW,
                    'line': 'first',
                    'login': 'superuser',
                },
                {
                    'action': 'external_response',
                    'created': NOW,
                    'hidden_comment': 'some external response comment',
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'test_meta_key',
                            'value': 'test_value',
                        },
                    ],
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'some external response comment',
                'metadata': {
                    'test_key': 'test_value',
                    'test_key_2': 'test_value_2',
                },
            },
            {'X-API-Key': 'right_key', 'X-Client-ID': 'right_client_id'},
            {'is_open': False, 'is_visible': False},
            http.HTTPStatus.GONE,
            None,
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2ab',
            {
                'comment': 'some external response comment',
                'metadata': {
                    'test_key': 'test_value',
                    'test_key_2': 'test_value_2',
                },
            },
            {'X-API-Key': 'right_key', 'X-Client-ID': 'right_client_id'},
            None,
            http.HTTPStatus.GONE,
            None,
            None,
            None,
        ),
        (
            'no_such_ticket',
            {'comment': 'some external response comment'},
            {'X-API-Key': 'right_key', 'X-Client-ID': 'right_client_id'},
            None,
            http.HTTPStatus.BAD_REQUEST,
            None,
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'some external response comment',
                'metadata': {
                    'test_key': 'test_value',
                    'test_key_2': 'test_value_2',
                },
            },
            {'X-API-Key': 'right_key_f', 'X-Client-ID': 'right_client_id_f'},
            None,
            http.HTTPStatus.FORBIDDEN,
            None,
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'some external response comment',
                'metadata': {
                    'test_key': 'test_value',
                    'test_key_2': 'test_value_2',
                },
            },
            {'X-API-Key': 'right_key'},
            None,
            http.HTTPStatus.FORBIDDEN,
            None,
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'some external response comment',
                'metadata': {
                    'test_key': 'test_value',
                    'test_key_2': 'test_value_2',
                },
            },
            {'X-Client-ID': 'right_client_id'},
            None,
            http.HTTPStatus.FORBIDDEN,
            None,
            None,
            None,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_external_response(
        cbox,
        task_id,
        data,
        headers,
        chat_status,
        expected_status,
        expected_inner_comments,
        expected_metadata,
        expected_history,
        mock_uapi_keys_auth,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_chat_search,
        mock_st_get_messages,
        mock_st_create_comment,
        mock_st_update_ticket,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        monkeypatch,
):
    mock_chat_get_history({'messages': []})
    mock_st_get_all_attachments()
    mock_st_get_comments([])
    mock_st_update_ticket('open')

    async def get_chat(*args, **kwargs):
        return {
            'id': 'chat_id',
            'type': 'client_support',
            'metadata': {'last_message_from_user': False},
            'status': chat_status or {'is_open': True, 'is_visible': True},
        }

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_chat', get_chat,
    )

    await cbox.post(
        '/v1/tasks/{}/external_response'.format(task_id),
        data=data,
        headers=headers,
    )
    assert cbox.status == expected_status

    if cbox.status == http.HTTPStatus.OK:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId(task_id)},
        )
        assert task['inner_comments'] == expected_inner_comments
        assert task['meta_info'] == expected_metadata
        assert task['history'] == expected_history


@pytest.mark.parametrize(
    (
        'task_id',
        'data',
        'expected_status',
        'expected_inner_comments',
        'expected_history',
    ),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {'hidden_comment': 'some external response comment'},
            http.HTTPStatus.OK,
            [
                {
                    'comment': 'some external response comment',
                    'created': NOW,
                    'login': 'superuser',
                },
            ],
            [
                {
                    'action': 'hidden_comment',
                    'created': NOW,
                    'hidden_comment': 'some external response comment',
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                },
            ],
        ),
        (
            '5a2cae5cb2682a976914c2a1',
            {
                'hidden_comment': 'some external response comment',
                'hidden_comment_metadata': {'from': 'eats_proactive_support'},
            },
            http.HTTPStatus.OK,
            [
                {
                    'comment': 'some external response comment',
                    'created': NOW,
                    'login': 'superuser',
                    'from': 'eats_proactive_support',
                },
            ],
            [
                {
                    'action': 'hidden_comment',
                    'created': NOW,
                    'hidden_comment': 'some external response comment',
                    'in_addition': False,
                    'line': 'vip',
                    'login': 'superuser',
                },
            ],
        ),
        (
            '5a2cae5cb2682a976914c2a5',
            {'hidden_comment': 'some external response comment'},
            http.HTTPStatus.NOT_FOUND,
            None,
            None,
        ),
        (
            'is_not_valid_task_id',
            {'hidden_comment': 'some external response comment'},
            http.HTTPStatus.BAD_REQUEST,
            None,
            None,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_hidden_comment_with_tvm(
        cbox,
        task_id,
        data,
        expected_status,
        expected_inner_comments,
        expected_history,
):
    await cbox.post(
        '/v1/tasks/{}/hidden_comment_with_tvm'.format(task_id), data=data,
    )
    assert cbox.status == expected_status

    if cbox.status == http.HTTPStatus.OK:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId(task_id)},
        )
        assert task['inner_comments'] == expected_inner_comments
        assert task['history'] == expected_history


@pytest.mark.now(NOW.isoformat())
async def test_dont_add_external_comment_id(
        cbox, patch, mock_st_create_comment,
):
    @patch(
        'chatterbox.internal.task_source._startrack.'
        'Startrack.put_hidden_comment',
    )
    async def put_hidden_comment(task, comment, comment_index, **kwargs):
        await stq_task.startrack_hidden_comment(
            cbox.app,
            task['external_id'],
            comment,
            comment_index,
            log_extra=kwargs.get('log_extra'),
            profile=kwargs.get('profile'),
        )

    @patch(
        'chatterbox.internal.tasks_manager.'
        'TasksManager.set_external_comment_id',
    )
    async def _set_external_comment_id(*args, **kwargs):
        raise Exception

    @patch('chatterbox.internal.tasks_manager.TasksManager._find_and_modify')
    async def _find_and_modify(*args, **kwargs):
        return {'inner_comments': []}

    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2b0/hidden_comment',
        data={
            'hidden_comment': 'some test inner comment',
            'themes': ['1', '2'],
            'themes_tree': ['1', '2'],
        },
    )
    assert cbox.status == http.HTTPStatus.OK
    assert not _set_external_comment_id.call


@pytest.mark.now(NOW.isoformat())
async def test_put_hidden_comment_profile(cbox, stq, mock_st_create_comment):
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2b1/hidden_comment',
        data={
            'hidden_comment': 'some test inner comment',
            'themes': ['1', '2'],
            'themes_tree': ['1', '2'],
        },
    )
    assert cbox.status == http.HTTPStatus.OK

    assert stq.startrack_hidden_comment_queue.times_called == 1

    call = stq.startrack_hidden_comment_queue.next_call()
    assert call['kwargs']['profile'] == 'support-zen'
    assert not stq.startrack_hidden_comment_queue.has_calls


class TestAddComment:
    @pytest.mark.now(NOW.isoformat())
    @pytest.mark.parametrize('handle', ['comment', 'comment_with_tvm'])
    @pytest.mark.parametrize(
        ['macro_ids', 'task_id', 'expected_line', 'external_id'],
        [
            (
                None,
                '5b2cae5cb2682a976914c2a1',
                'first',
                'some_user_chat_message_id',
            ),
            (
                None,
                '5c2cae5cb2682a976914c2a1',
                'first',
                'some_user_chat_message_id',
            ),
            (
                [],
                '5b2cae5cb2682a976914c2a1',
                'first',
                'some_user_chat_message_id',
            ),
            (
                ['macro_1'],
                '5b2cae5cb2682a976914c2a1',
                'first',
                'some_user_chat_message_id',
            ),
            (
                ['some_macro_id2', 'some_macro_id', 'macro_1'],
                '5b2cae5cb2682a976914c2a1',
                'first',
                'some_user_chat_message_id',
            ),
            (
                ['macro_1'],
                '5b2cae5cb4282a976914c2c9',
                'driver_online',
                'some_user_chat_message_id_17',
            ),
        ],
    )
    async def test_chat_task(
            self,
            macro_ids,
            task_id,
            expected_line,
            external_id,
            cbox,
            mock_chat_add_update,
            mock_chat_get_history,
            mock_random_str_uuid,
            handle,
    ):
        """
        Тест на добавление комментария в заявку из чата
        при этом external_id у комментария в истории не появляется
        """
        mock_chat_get_history({'messages': []})
        mock_random_str_uuid()

        data = {
            'comment': 'some test comment',
            'macro_id': 'macro_1',
            'themes': ['1', '2'],
        }
        if macro_ids is not None:
            data['macro_ids'] = macro_ids

        await cbox.post('/v1/tasks/{}/{}'.format(task_id, handle), data=data)

        await self.check_asserts(cbox, task_id, macro_ids, line=expected_line)
        add_update_call = mock_chat_add_update.calls.pop(0)
        # check chat_id in args
        assert add_update_call['args'] == (external_id,)
        add_update_call['kwargs'].pop('log_extra')
        add_update_call['kwargs'].pop('user_guid', None)
        assert add_update_call['kwargs'] == {
            'message_id': None,
            'message_text': 'some test comment',
            'message_sender_role': 'support',
            'message_sender_id': 'superuser',
            'message_metadata': None,
            'update_metadata': {'ticket_status': 'pending'},
        }
        async with cbox.app.pg_master_pool.acquire() as conn:
            result = await conn.fetch(
                'SELECT COUNT(*)'
                'FROM chatterbox.supporter_tasks '
                'WHERE task_id = $1',
                str(task_id),
            )
            assert len(result) == 1
            assert result[0]['count'] == 0

    @pytest.mark.config(STARTRACK_TRANSIT_TO_NEED_INFO_ON_WAITING=False)
    @pytest.mark.now(NOW.isoformat())
    async def test_startrack_task(
            self,
            cbox,
            mock_st_get_ticket,
            mock_st_get_comments,
            mock_st_create_comment,
            mock_st_get_all_attachments,
            mock_st_update_ticket,
            mock_random_str_uuid,
    ):
        """
        Тест на добавление комментария в стартекный тикет
        при этом в history в комментарий проставляется external_id
        id комментария из стартрека
        """
        mock_st_get_all_attachments()
        mock_st_get_comments([])
        mock_st_update_ticket('open')
        commend_id = 10005000
        mock_st_create_comment.set_response({'id': commend_id})
        mock_random_str_uuid()

        task_id = '5b2cae5cb2682a976914c2b0'

        await cbox.post(
            '/v1/tasks/{}/comment'.format(task_id),
            data={
                'comment': 'some test comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
            },
        )

        await self.check_asserts(cbox, task_id, external_id=str(commend_id))

        create_comment_call = mock_st_create_comment.call
        assert create_comment_call['args'] == ('some_queue-1',)  # st ticket id
        create_comment_call['kwargs'].pop('log_extra')
        assert create_comment_call['kwargs'] == {
            'email_from': 'test@support',
            'email_subject': 'Re: Zomg!',
            'email_cc': ['toert@yandex', 'i@love.memes'],
            'email_text': 'some test comment',
            'email_to': 'some@email',
            'text': 'superuser написал письмо',
            'signature_selection': True,
            'attachment_ids': None,
        }

    @pytest.mark.config(STARTRACK_TRANSIT_TO_NEED_INFO_ON_WAITING=True)
    @pytest.mark.now(NOW.isoformat())
    async def test_startrack_to_need_info(
            self,
            cbox,
            mock_st_get_ticket,
            mock_st_get_comments,
            mock_st_create_comment,
            mock_st_get_all_attachments,
            mock_st_update_ticket,
            mock_st_transition,
            mock_random_str_uuid,
    ):
        """
        Тест на переход тикета в стратреке в статус "needInfo"
        """
        mock_st_get_all_attachments()
        mock_st_get_comments([])
        mock_st_update_ticket('open')
        comment_id = 10005000
        mock_st_create_comment.set_response({'id': comment_id})
        mock_random_str_uuid()

        task_id = '5b2cae5cb2682a976914c2b0'

        await cbox.post(
            '/v1/tasks/{}/comment'.format(task_id),
            data={
                'comment': 'some test comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
            },
        )
        await self.check_asserts(cbox, task_id, external_id=str(comment_id))
        create_comment_call = mock_st_create_comment.call
        create_comment_call['kwargs'].pop('log_extra')
        assert mock_st_transition.calls

    async def check_asserts(
            self,
            cbox,
            task_id,
            macro_ids=None,
            external_id=None,
            line='first',
    ):
        if not macro_ids:
            macro_ids = []
        assert cbox.status == http.HTTPStatus.OK
        assert cbox.body_data == {}

        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId(task_id)},
        )

        history = [
            {
                'action_id': 'test_uid',
                'action': 'comment',
                'created': NOW,
                'login': 'superuser',
                'line': line,
                'comment': 'some test comment',
                'in_addition': False,
                'meta_changes': [
                    {
                        'change_type': 'set',
                        'field_name': 'macro_id',
                        'value': 'macro_1',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'currently_used_macro_ids',
                        'value': list(sorted(set(macro_ids + ['macro_1']))),
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'themes',
                        'value': [1, 2],
                    },
                ],
                'tags_changes': [
                    {'change_type': 'add', 'tag': '3'},
                    {'change_type': 'add', 'tag': '4'},
                ],
            },
        ]
        if macro_ids:
            history[0]['macro_ids'] = macro_ids
        if external_id:
            history[0]['external_id'] = external_id

        assert task['history'] == history
        assert task['status'] == 'waiting'


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'driver_phone': 'phones',
            'park_phone': 'phones',
        },
    },
)
@pytest.mark.parametrize(
    [
        'message_id',
        'comment',
        'expected_add_update_call',
        'expected_history',
        'expected_processor',
    ],
    [
        (
            '2fd2a433-92c3-4e73-a0f7-ff3452823602',
            'Промокод {{promo:200}} на {{nominal}} {{currency}}',
            {
                'message_id': None,
                'message_text': 'Промокод promo123 на 200 ₽',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': {
                    'promocodes': [{'code': 'promo123'}],
                    'reply_to': ['2fd2a433-92c3-4e73-a0f7-ff3452823602'],
                },
                'update_metadata': {'ticket_status': 'pending'},
            },
            {
                'action_id': 'test_uid',
                'comment': 'Промокод promo123 на 200 ₽',
                'in_addition': False,
                'action': 'comment',
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
                'promocodes': [{'code': 'promo123'}],
            },
            True,
        ),
        pytest.param(
            '2fd2a433-92c3-4e73-a0f7-ff3452823602',
            'Промокод {{promo:200}} на {{nominal}} {{currency}}',
            {
                'message_id': None,
                'message_text': (
                    'Промокод {{promo:200}} на {{nominal}} {{currency}}'
                ),
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': {
                    'reply_to': ['2fd2a433-92c3-4e73-a0f7-ff3452823602'],
                },
                'update_metadata': {'ticket_status': 'pending'},
            },
            {
                'action_id': 'test_uid',
                'comment': (
                    'Промокод {{promo:200}} на {{nominal}} {{currency}}'
                ),
                'in_addition': False,
                'action': 'comment',
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
            },
            False,
            marks=[
                pytest.mark.config(
                    CHATTERBOX_FORBIDDEN_EXTERNAL_REQUESTS={
                        'client': {
                            '__default__': False,
                            'comment_processor': True,
                        },
                    },
                ),
            ],
        ),
        (
            '2fd2a433-92c3-4e73-a0f7-ff3452823602',
            'Промокод %%((yandextaxi://addpromocode?'
            'code={{promo:200}} {{promo:200}}))'
            ' на {{nominal}} {{currency}}',
            {
                'message_id': None,
                'message_text': (
                    'Промокод %%((yandextaxi://addpromocode?'
                    'code=promo123 promo123)) на 200 ₽'
                ),
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': {
                    'promocodes': [{'code': 'promo123'}],
                    'reply_to': ['2fd2a433-92c3-4e73-a0f7-ff3452823602'],
                },
                'update_metadata': {'ticket_status': 'pending'},
            },
            {
                'action_id': 'test_uid',
                'comment': (
                    'Промокод %%((yandextaxi://addpromocode?'
                    'code=promo123 promo123)) на 200 ₽'
                ),
                'in_addition': False,
                'action': 'comment',
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
                'promocodes': [{'code': 'promo123'}],
            },
            True,
        ),
    ],
)
async def test_comment_with_promocode(
        cbox,
        patch,
        mock_chat_get_history,
        mock_personal,
        mock_random_str_uuid,
        message_id,
        comment,
        expected_add_update_call,
        expected_history,
        expected_processor,
):
    task_id = bson.ObjectId('5b2cae5cb2682a976914c2a4')
    mock_chat_get_history(
        {
            'messages': [
                {
                    'id': message_id,
                    'text': 'QWERTYUI',
                    'sender': {'id': 'toert', 'role': 'support'},
                },
            ],
        },
    )
    mock_random_str_uuid()

    @patch('taxi.clients.support_chat.SupportChatApiClient.add_update')
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    @patch('taxi.clients.admin.AdminApiClient.generate_promocode')
    async def _dummy_generate_promocode(*args, **kwargs):
        return {'code': 'promo123'}

    cbox.set_user('some_user')
    await cbox.post(
        '/v1/tasks/{}/comment'.format(task_id),
        data={'comment': comment, 'reply_to': [message_id]},
    )
    assert cbox.status == http.HTTPStatus.OK

    generate_promocode_calls = _dummy_generate_promocode.calls
    if expected_processor:
        assert len(generate_promocode_calls) == 1
        assert generate_promocode_calls[0]['args'] == (
            'yandex',
            'excs',
            '+71234567890',
            '5b2cae5cb2682a976914c2a4',
        )
        assert generate_promocode_calls[0]['kwargs']['cookies'] == {
            'Session_id': 'some_user_sid',
            'yandexuid': 'some_user_uid',
            'sessionid2': 'some_user_sid2',
        }
    else:
        assert not generate_promocode_calls

    add_update_call = _dummy_add_update.calls[0]
    add_update_call['kwargs'].pop('log_extra')
    assert add_update_call['kwargs'] == expected_add_update_call

    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    assert task['history'][-1] == expected_history


async def test_comment_promocode_adding(cbox, patch, mock_chat_get_history):
    mock_chat_get_history({'messages': []})

    @patch('taxi.clients.support_chat.SupportChatApiClient.add_update')
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    cbox.set_user('some_user')
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a4/comment',
        data={'comment': 'Промокод {{add_promo:promo123}}'},
    )
    assert cbox.status == http.HTTPStatus.OK

    add_update_call = _dummy_add_update.calls[0]
    add_update_call['kwargs'].pop('log_extra')
    assert add_update_call['kwargs'] == {
        'message_id': None,
        'message_text': 'Промокод promo123',
        'message_sender_role': 'support',
        'message_sender_id': 'superuser',
        'message_metadata': {'promocodes': [{'code': 'promo123'}]},
        'update_metadata': {'ticket_status': 'pending'},
    }


@pytest.mark.parametrize('handler', ['communicate', 'communicate_with_tvm'])
@pytest.mark.parametrize(
    (
        'task_id',
        'query',
        'messages',
        'expected_history',
        'expected_status',
        'expected_startrack_tags',
    ),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'some test comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
            },
            [],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'some test comment',
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'macro_1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['macro_1'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                },
            ],
            'in_progress',
            [],
        ),
        (
            '5c2cae5cb2682a976914c2a1',
            {
                'comment': 'some test comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
            },
            [],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'some test comment',
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'macro_1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['macro_1'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                },
            ],
            'in_progress',
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'hidden_comment': 'some hidden comment'},
            [],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'hidden_comment',
                    'in_addition': False,
                    'hidden_comment': 'some hidden comment',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'login': 'superuser',
                    'line': 'first',
                },
            ],
            'in_progress',
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {
                'comment': 'some test comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
            },
            [
                {
                    'sender': {'id': 'ebobo', 'role': 'client'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:35:16'},
                },
            ],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'corp',
                    'comment': 'some test comment',
                    'first_answer': 20,
                    'first_answer_in_line': 20,
                    'full_resolve': 20,
                    'in_addition': False,
                    'line_sla': False,
                    'support_sla': True,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'macro_1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['macro_1'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                },
            ],
            'in_progress',
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {
                'comment': 'some test comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
            },
            [
                {
                    'sender': {'id': 'ebobo', 'role': 'client'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:35:16'},
                },
                {
                    'sender': {'id': 'ebobo', 'role': 'client'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:35:56'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:36:16'},
                },
            ],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'corp',
                    'comment': 'some test comment',
                    'first_answer': 20,
                    'first_answer_in_line': 20,
                    'full_resolve': 40,
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'macro_1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['macro_1'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                },
            ],
            'in_progress',
            [],
        ),
        (
            '5b2cae5cb2682a976914c2b0',
            {
                'comment': 'some startrack comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
                'reply_to': ['ext_id_1', 'ext_id_2'],
            },
            [],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'external_id': '1005005505045045040',
                    'reply_to': ['ext_id_1', 'ext_id_2'],
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'some startrack comment',
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'macro_1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['macro_1'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                },
            ],
            'in_progress',
            [],
        ),
        (
            '5b2cae5cb2682a976914c2b0',
            {
                'comment': 'some startrack comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
                'selected_messages_id': ['ext_id_1', 'ext_id_2'],
            },
            [],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'external_id': '1005005505045045040',
                    'reply_to': ['ext_id_1', 'ext_id_2'],
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'some startrack comment',
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'macro_1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['macro_1'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                },
            ],
            'in_progress',
            [],
        ),
        (
            '5b2cae5cb2682a976914c2b0',
            {
                'comment': 'some startrack comment',
                'macro_ids': ['77', '1'],
                'themes': ['1', '2'],
                'selected_messages_id': ['ext_id_1', 'ext_id_2'],
                'tags': ['some_tag'],
            },
            [],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'external_id': '1005005505045045040',
                    'reply_to': ['ext_id_1', 'ext_id_2'],
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'some startrack comment',
                    'in_addition': False,
                    'macro_ids': ['77', '1'],
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['1', '77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                        {'change_type': 'add', 'tag': 'some_tag'},
                    ],
                },
            ],
            'in_progress',
            ['3', '4', 'check_macro_id_tag', 'some_tag', 'tag1', 'tag2'],
        ),
        (
            '5b2cae5cb4282a976914c2c9',
            {
                'comment': 'some test comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
            },
            [],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'driver_online',
                    'comment': 'some test comment',
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'macro_1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['macro_1'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                },
            ],
            'in_progress',
            [],
        ),
        (
            '5b2cae5cb4282a976914c2c9',
            {
                'comment': 'some test {{media_subscription_cancel:12}}comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
            },
            [],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'driver_online',
                    'comment': 'some test comment',
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'cancel_result',
                            'value': 'test',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'macro_1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['macro_1'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'succeed_operations': ['subscription_cancel'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                },
            ],
            'in_progress',
            [],
        ),
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'some test comment',
                'comment_metadata': {'encrypt_key': '123'},
                'macro_id': '77',
                'themes': ['1', '2'],
                'tags': ['extra_tag'],
            },
            [],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'some test comment',
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_added': [
                        '3',
                        '4',
                        'check_macro_id_tag',
                        'extra_tag',
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                        {'change_type': 'add', 'tag': 'extra_tag'},
                    ],
                },
            ],
            'in_progress',
            [],
            marks=[pytest.mark.config(CHATTERBOX_HISTORY_TAGS_ADDED=True)],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_communicate(
        cbox,
        handler,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_st_get_messages,
        mock_st_create_comment,
        mock_st_update_ticket,
        mock_random_str_uuid,
        task_id,
        query,
        messages,
        expected_history,
        expected_status,
        expected_startrack_tags,
        mockserver,
):
    mock_chat_get_history({'messages': messages})
    mock_st_get_messages(
        {'messages': messages, 'total': 0, 'hidden_comments': []},
    )
    st_update_ticket = mock_st_update_ticket('open')
    mock_random_str_uuid()

    @mockserver.json_handler('/music/stop-active-interval/')
    def _dummy_subscription_cancel(request):
        return {'result': 'test'}

    await cbox.post('/v1/tasks/{}/{}'.format(task_id, handler), data=query)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == {}

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )

    assert task['history'] == expected_history
    assert task['status'] == expected_status

    add_update_calls = mock_chat_add_update.calls
    if add_update_calls:
        assert add_update_calls[0]['kwargs']['update_metadata'] == {
            'ticket_status': 'open',
        }
    if expected_startrack_tags:
        assert (
            st_update_ticket.calls[0]['kwargs']['tags']
            == expected_startrack_tags
        )
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            str(task['_id']),
        )
        assert len(result) == 1
        assert result[0]['count'] == 1


@pytest.mark.parametrize('handler', ['communicate', 'comment', 'close'])
@pytest.mark.parametrize(
    (
        'task_id',
        'query',
        'messages',
        'expected_history',
        'expected_startrack_tags',
    ),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {'button_macro_id': '1337'},
            [],
            [
                {
                    'created': NOW,
                    'login': 'superuser',
                    'action_id': 'test_uid',
                    'line': 'first',
                    'comment': 'macro_1337',
                    'in_addition': False,
                    'from_button': True,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '1337',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['1337'],
                        },
                    ],
                    'tags_changes': [{'change_type': 'add', 'tag': '1337'}],
                    'query_params': {'button_macro_id': '1337'},
                },
            ],
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'button_macro_id': '1'},
            [],
            [
                {
                    'created': NOW,
                    'login': 'superuser',
                    'action_id': 'test_uid',
                    'line': 'first',
                    'comment': 'comment',
                    'in_addition': False,
                    'from_button': True,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['1'],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                    'query_params': {'button_macro_id': '1'},
                },
            ],
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {'button_macro_id': '1', 'chatterbox_button': 'button1'},
            [
                {
                    'sender': {'id': 'ebobo', 'role': 'client'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:35:16'},
                },
            ],
            [
                {
                    'created': NOW,
                    'login': 'superuser',
                    'action_id': 'test_uid',
                    'line': 'corp',
                    'comment': 'comment',
                    'from_button': True,
                    'first_answer': 20,
                    'first_answer_in_line': 20,
                    'full_resolve': 20,
                    'in_addition': False,
                    'line_sla': False,
                    'support_sla': True,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'chatterbox_button',
                            'value': 'button1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['1'],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                    'query_params': {
                        'button_macro_id': '1',
                        'chatterbox_button': 'button1',
                    },
                },
            ],
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {'button_macro_id': '1337', 'additional_tag': 'additional_tag1'},
            [
                {
                    'sender': {'id': 'ebobo', 'role': 'client'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:35:16'},
                },
                {
                    'sender': {'id': 'ebobo', 'role': 'client'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:35:56'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:36:16'},
                },
            ],
            [
                {
                    'created': NOW,
                    'login': 'superuser',
                    'action_id': 'test_uid',
                    'line': 'corp',
                    'comment': 'macro_1337',
                    'first_answer': 20,
                    'first_answer_in_line': 20,
                    'full_resolve': 40,
                    'from_button': True,
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '1337',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['1337'],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '1337'},
                        {'change_type': 'add', 'tag': 'additional_tag1'},
                    ],
                    'query_params': {
                        'button_macro_id': '1337',
                        'additional_tag': 'additional_tag1',
                    },
                },
            ],
            [],
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            {
                'button_macro_id': '1337',
                'additional_tag': 'additional_tag123',
                'chatterbox_button': 'chtb_btn123',
            },
            [
                {
                    'sender': {'id': 'ebobo', 'role': 'client'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:34:56'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:35:16'},
                },
                {
                    'sender': {'id': 'ebobo', 'role': 'client'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:35:56'},
                },
                {
                    'sender': {'id': 'some_login', 'role': 'support'},
                    'text': 'sadsda',
                    'metadata': {'created': '2018-05-05T15:36:16'},
                },
            ],
            [
                {
                    'created': NOW,
                    'login': 'superuser',
                    'action_id': 'test_uid',
                    'line': 'corp',
                    'comment': 'macro_1337',
                    'first_answer': 20,
                    'first_answer_in_line': 20,
                    'full_resolve': 40,
                    'from_button': True,
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'chatterbox_button',
                            'value': 'chtb_btn123',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '1337',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['1337'],
                        },
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '1337'},
                        {'change_type': 'add', 'tag': 'additional_tag123'},
                    ],
                    'query_params': {
                        'button_macro_id': '1337',
                        'additional_tag': 'additional_tag123',
                        'chatterbox_button': 'chtb_btn123',
                    },
                },
            ],
            [],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_macro_in_query(
        cbox,
        handler,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_st_get_messages,
        mock_st_create_comment,
        mock_st_update_ticket,
        mock_random_str_uuid,
        task_id,
        query,
        messages,
        expected_history,
        expected_startrack_tags,
):
    mock_chat_get_history({'messages': messages})
    mock_st_get_messages(
        {'messages': messages, 'total': 0, 'hidden_comments': []},
    )
    st_update_ticket = mock_st_update_ticket('open')
    mock_random_str_uuid()

    await cbox.post(
        '/v1/tasks/{}/{}'.format(task_id, handler), params=query, data={},
    )
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == {}

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )

    expected_history[0]['action'] = handler
    assert task['history'] == expected_history

    expected_status = ''
    if handler == 'communicate':
        expected_status = 'in_progress'
    elif handler == 'comment':
        expected_status = 'waiting'
    elif handler == 'close':
        expected_status = 'closed'
    assert task['status'] == expected_status

    add_update_calls = mock_chat_add_update.calls
    if add_update_calls and handler == 'communicate':
        assert add_update_calls[0]['kwargs']['update_metadata'] == {
            'ticket_status': 'open',
        }
    elif add_update_calls and handler == 'comment':
        assert add_update_calls[0]['kwargs']['update_metadata'] == {
            'ticket_status': 'pending',
        }
    elif add_update_calls and handler == 'close':
        assert add_update_calls[0]['kwargs']['update_metadata'] == {
            'ask_csat': True,
            'retry_csat_request': False,
            'ticket_status': 'solved',
        }
    if expected_startrack_tags:
        assert (
            st_update_ticket.calls[0]['kwargs']['tags']
            == expected_startrack_tags
        )
    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            str(task['_id']),
        )
        assert len(result) == 1
        if handler == 'communicate':
            assert result[0]['count'] == 1
        elif handler == 'comment':
            assert result[0]['count'] == 0
        elif handler == 'close':
            assert result[0]['count'] == 0


@pytest.mark.translations(
    chatterbox={
        'errors.support_chat_length_over_limit': {
            'ru': 'Короче потому что {reason}',
        },
    },
)
@pytest.mark.parametrize(
    ['task_id', 'query'],
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'some test comment',
                'macro_id': 'macro_1',
                'themes': ['1', '2'],
            },
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_too_large_request_error(
        cbox,
        mock_chat_add_update,
        mock_chat_add_update_raise,
        mock_chat_get_history,
        task_id,
        query,
):
    mock_chat_add_update_raise(
        support_chat.TooLargeMessageError(
            'Message limit', limit=671, reason='671 ≥ 670',
        ),
    )

    await cbox.post('/v1/tasks/{}/communicate'.format(task_id), data=query)
    assert cbox.status == http.HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    assert cbox.body_data == {
        'message': 'Короче потому что 671 ≥ 670',
        'status': 'request_error',
    }


@pytest.mark.translations(
    chatterbox={
        'errors.line_not_found': {
            'en': 'Undefined line {line}',
            'ru': 'Неизвестная линия {line}',
        },
        'errors.forwarding_different_line_modes': {
            'en': (
                'Different line modes: {line_from} is {mode_from} and '
                '{line_to} is {mode_to}'
            ),
            'ru': (
                'Различные типы линий: {line_from} типа {mode_from}, а '
                '{line_to} типа {mode_to}'
            ),
        },
        'errors.forwarding_bad_line_chat_types': {
            'en': (
                'It is forbidden to forward ticket with type {chat_type_from} '
                'to line {line_to}'
            ),
            'ru': (
                'Перенос тикета с типом {chat_type_from} в линию '
                '{line_to} запрещен'
            ),
        },
        'errors.line_not_allowed': {
            'en': (
                'It is forbidden to forward ticket from line {line_from} '
                'to line {line_to}'
            ),
            'ru': (
                'Перенос тикета из линии {line_from} '
                'в линию {line_to} запрещен'
            ),
        },
        'errors.forwarding_different_profiles': {
            'en': (
                'It is forbidden to forward ticket between profiles '
                '{line_from_profile} and {line_to_profile}'
            ),
            'ru': (
                'Перенос тикета между линиями с разными профилями '
                '{line_from_profile} и {line_to_profile} запрещен'
            ),
        },
    },
)
@pytest.mark.config(
    CHATTERBOX_CHANGE_LINE_STATUSES={'in_progress': 'forwarded'},
    CHATTERBOX_LINES={
        'second': {'types': ['client']},
        'first': {'types': ['client']},
        'corp': {'types': ['client']},
        'urgent': {'types': []},
        'vip': {'types': ['client'], 'mode': 'online'},
        'zen': {'types': ['client'], 'profile': 'support-zen'},
        'samsara': {'types': ['client']},
    },
    CHAT_LINE_TRANSITIONS={
        'first': ['second', 'samsara'],
        'corp': ['urgent', 'vip', 'undefined_line', 'zen'],
    },
    CHATTERBOX_SAMSARA_PUSH_MESSAGE_DELAY=10,
)
@pytest.mark.parametrize('handler', ['forward', 'forward_with_tvm'])
@pytest.mark.parametrize(
    (
        'ticket_id',
        'expected_from_line',
        'line',
        'locale',
        'is_available',
        'expected_error_body',
    ),
    [
        ('5b2cae5cb2682a976914c2a1', 'first', 'second', 'ru', True, None),
        ('5b2cae5cb2682a976914c2a1', 'first', 'samsara', 'ru', True, None),
        (
            # not in CHAT_LINE_TRANSITIONS
            '5b2cae5cb2682a976914c2a2',
            'corp',
            'second',
            'ru',
            False,
            {
                'status': 'request_error',
                'message': (
                    'Перенос тикета из линии corp в ' 'линию second запрещен'
                ),
            },
        ),
        (
            # urgent['types'] == []
            '5b2cae5cb2682a976914c2a2',
            'corp',
            'urgent',
            'ru',
            False,
            {
                'status': 'request_error',
                'message': (
                    'Перенос тикета с типом client ' 'в линию urgent запрещен'
                ),
            },
        ),
        (
            # vip['mode'] == online != corp['mode']
            '5b2cae5cb2682a976914c2a2',
            'corp',
            'vip',
            'ru',
            True,
            None,
        ),
        (
            # line not in CHATTERBOX_LINES
            '5b2cae5cb2682a976914c2a2',
            'corp',
            'undefined_line',
            'ru',
            False,
            {
                'status': 'request_error',
                'message': 'Неизвестная линия undefined_line',
            },
        ),
        (
            # not in CHAT_LINE_TRANSITIONS
            '5b2cae5cb2682a976914c2a2',
            'corp',
            'second',
            'en',
            False,
            {
                'status': 'request_error',
                'message': (
                    'It is forbidden to forward ticket '
                    'from line corp to line second'
                ),
            },
        ),
        (
            # urgent['types'] == []
            '5b2cae5cb2682a976914c2a2',
            'corp',
            'urgent',
            'en',
            False,
            {
                'status': 'request_error',
                'message': (
                    'It is forbidden to forward ticket with '
                    'type client to line urgent'
                ),
            },
        ),
        (
            # vip['mode'] == online != corp['mode']
            '5b2cae5cb2682a976914c2a2',
            'corp',
            'vip',
            'en',
            True,
            None,
        ),
        (
            # line not in CHATTERBOX_LINES
            '5b2cae5cb2682a976914c2a2',
            'corp',
            'undefined_line',
            'en',
            False,
            {
                'status': 'request_error',
                'message': 'Undefined line undefined_line',
            },
        ),
        (
            # lines with different profiles
            '5b2cae5cb2682a976914c2a2',
            'corp',
            'zen',
            'en',
            False,
            {
                'status': 'request_error',
                'message': (
                    'It is forbidden to forward ticket between profiles '
                    'support-taxi and support-zen'
                ),
            },
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_forward(
        cbox,
        stq,
        mock_random_str_uuid,
        ticket_id,
        handler,
        expected_from_line,
        line,
        locale,
        is_available,
        expected_error_body,
):
    mock_random_str_uuid()
    await cbox.post(
        '/v1/tasks/{0}/{1}'.format(ticket_id, handler),
        params={'line': line},
        data={
            'themes': ['2'],
            'themes_tree': ['1'],
            'hidden_comment': 'text',
            'hidden_comment_metadata': {'encrypt_key': '123'},
        },
        headers={'Accept-Language': locale},
    )
    if is_available:
        assert cbox.status == http.HTTPStatus.OK
    else:
        assert cbox.status == http.HTTPStatus.BAD_REQUEST
        assert cbox.body_data == expected_error_body

        return

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(ticket_id)},
    )
    assert task['line'] == line
    assert task['status'] == 'forwarded'
    assert task['history'] == [
        {
            'action_id': 'test_uid',
            'action': 'forward',
            'created': NOW,
            'login': 'superuser',
            'line': expected_from_line,
            'new_line': line,
            'hidden_comment': 'text',
            'in_addition': False,
            'meta_changes': [
                {'change_type': 'set', 'field_name': 'themes', 'value': [2]},
                {
                    'change_type': 'set',
                    'field_name': 'theme_name',
                    'value': 'Theme',
                },
                {
                    'change_type': 'set',
                    'field_name': 'themes_tree',
                    'value': [1],
                },
            ],
            'query_params': {'line': line},
            'tags_changes': [
                {'change_type': 'add', 'tag': '3'},
                {'change_type': 'add', 'tag': '4'},
            ],
        },
    ]
    assert task['projects'] == ['taxi']

    if line == 'samsara':
        assert stq.support_chat_send_messages_to_samsara.times_called == 1
        call = stq.support_chat_send_messages_to_samsara.next_call()
        assert call['eta'] == NOW + datetime.timedelta(seconds=10)
        assert call['args'] == [
            {'$oid': str(task['_id'])},
            task['external_id'],
        ]
        call['kwargs'].pop('log_extra')
        assert call['kwargs'] == {
            'meta': task['meta_info'],
            'hidden_comment': 'text',
            'required_msg_id': None,
        }
        assert not stq.support_chat_send_messages_to_samsara.has_calls


@pytest.mark.config(
    CHATTERBOX_CHANGE_LINE_STATUSES={'in_progress': 'forwarded'},
    CHATTERBOX_LINES={
        'second': {'types': ['client']},
        'first': {'types': ['client']},
        'corp': {'types': ['client']},
        'urgent': {'types': []},
        'vip': {'types': ['client'], 'mode': 'online'},
    },
    CHAT_LINE_TRANSITIONS={
        'first': ['second'],
        'corp': ['urgent', 'vip', 'undefined_line'],
    },
    CHATTERBOX_FORWARD_AUTOREPLY=True,
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    (
        'ticket_id',
        'line',
        'locale',
        'is_available',
        'expected_chat_history',
        'expected_autoreply',
        'expected_history',
    ),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            'second',
            'ru',
            True,
            {
                'messages': [
                    {'sender': {'role': 'client'}, 'text': 'some message'},
                ],
            },
            True,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'second',
            'ru',
            True,
            {
                'messages': [
                    {'sender': {'role': 'client'}, 'text': 'some message'},
                    {'sender': {'role': 'support'}, 'text': 'some message'},
                ],
            },
            True,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'second',
            'ru',
            True,
            {
                'messages': [
                    {'sender': {'role': 'client'}, 'text': 'some message'},
                    {'sender': {'role': 'system'}, 'text': 'some message'},
                ],
            },
            True,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a2',
            'second',
            'ru',
            False,
            {
                'messages': [
                    {'sender': {'role': 'client'}, 'text': 'some message'},
                ],
            },
            False,
            None,
        ),
        (
            '5b2cae5cb2682a976914c299',
            'second',
            'ru',
            True,
            {
                'messages': [
                    {'sender': {'role': 'client'}, 'text': 'some message'},
                    {'sender': {'role': 'client'}, 'text': 'some message 2'},
                ],
            },
            True,
            [
                {
                    'action': 'update_meta',
                    'created': datetime.datetime(2018, 5, 7, 12, 34, 56),
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'order_id',
                            'value': 'order_id_1',
                        },
                    ],
                },
                {
                    'action': 'update_meta',
                    'created': datetime.datetime(2018, 5, 7, 12, 54, 56),
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'order_id',
                            'value': 'order_id_2',
                        },
                    ],
                },
                {
                    'action': 'forward',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'new_line': 'second',
                    'query_params': {'line': 'second'},
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c297',
            'second',
            'ru',
            True,
            {
                'messages': [
                    {'sender': {'role': 'client'}, 'text': 'some message'},
                ],
            },
            False,
            None,
        ),
    ],
)
async def test_autoreply_forward(
        cbox,
        ticket_id,
        line,
        locale,
        is_available,
        expected_chat_history,
        expected_autoreply,
        expected_history,
        mock_chat_get_history,
        stq,
):
    mock_chat_get_history(expected_chat_history)

    await cbox.post(
        '/v1/tasks/{0}/forward'.format(ticket_id),
        params={'line': line},
        data={},
        headers={'Accept-Language': locale},
    )
    if is_available:
        assert cbox.status == http.HTTPStatus.OK
    else:
        assert cbox.status == http.HTTPStatus.BAD_REQUEST
        return

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(ticket_id)},
    )
    assert task['line'] == line
    assert task['status'] == 'forwarded'
    assert task['history'] == expected_history or [
        {
            'action': 'forward',
            'created': NOW,
            'login': 'superuser',
            'line': 'first',
            'new_line': line,
            'in_addition': False,
        },
    ]
    if expected_autoreply:
        call = stq.chatterbox_post_update.next_call()
        assert call['id'] == ticket_id
        assert not stq.chatterbox_post_update.has_calls
    else:
        assert not stq.chatterbox_post_update.has_calls


@pytest.mark.config(
    CHATTERBOX_CHANGE_LINE_STATUSES={'in_progress': 'forwarded'},
    CHATTERBOX_LINES_WITHOUT_REOPEN_DELAY=['line_without_delay'],
    CHATTERBOX_LINES={
        'line_without_delay': {'types': ['client']},
        'line_with_delay': {'types': ['client']},
    },
    CHAT_LINE_TRANSITIONS={
        'line_without_delay': ['line_with_delay'],
        'line_with_delay': ['line_without_delay'],
    },
)
@pytest.mark.parametrize(
    'ticket_id, line, login, expected_login',
    [
        (
            '5e7e0ec6779fb308e06fa3a5',
            'line_with_delay',
            'test_user',
            'superuser',
        ),
        (
            '5e7e0ec6779fb308e06fa3a6',
            'line_without_delay',
            'test_user',
            'test_user',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_forward_delay(
        cbox, ticket_id, line, login, expected_login, patch_auth,
):
    patch_auth(login=login, superuser=True)
    await cbox.post(
        '/v1/tasks/{0}/forward'.format(ticket_id),
        params={'line': line},
        data={'themes': ['1', '2'], 'themes_tree': ['1']},
    )
    assert cbox.status == http.HTTPStatus.OK
    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(ticket_id)},
    )
    assert task['support_admin'] == expected_login


@pytest.mark.parametrize(
    (
        'task_id',
        'extra_data',
        'expected_line',
        'support_chat_call',
        'expected_startrack_tags',
        'expected_support_chat_result',
        'expected_history',
    ),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {},
            'first',
            False,
            [],
            None,
            [
                {
                    'action_id': 'test_uid',
                    'action': 'defer',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'query_params': {'reopen_at': '2018-06-15T15:34:00+0000'},
                    'reopen_at': datetime.datetime(2018, 6, 15, 15, 34),
                    'tags_added': ['3', '4', 'check_macro_id_tag'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                    ],
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'comment': '   '},
            'first',
            False,
            [],
            None,
            [
                {
                    'action_id': 'test_uid',
                    'action': 'defer',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'query_params': {'reopen_at': '2018-06-15T15:34:00+0000'},
                    'reopen_at': datetime.datetime(2018, 6, 15, 15, 34),
                    'tags_added': ['3', '4', 'check_macro_id_tag'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                    ],
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': '  some awesome comment  ',
                'comment_metadata': {'encrypt_key': '123'},
                'hidden_comment': '  some awesome hidden_comment  ',
                'hidden_comment_metadata': {'encrypt_key': '321'},
            },
            'first',
            True,
            [],
            {
                'message_id': None,
                'message_text': 'some awesome comment',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': {'encrypt_key': '123'},
                'update_metadata': {'ticket_status': 'open'},
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'defer',
                    'comment': 'some awesome comment',
                    'created': NOW,
                    'hidden_comment': '  some awesome hidden_comment  ',
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'query_params': {'reopen_at': '2018-06-15T15:34:00+0000'},
                    'reopen_at': datetime.datetime(2018, 6, 15, 15, 34),
                    'tags_added': ['3', '4', 'check_macro_id_tag'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                    ],
                },
            ],
        ),
        (
            '5c2cae5cb2682a976914c2a1',
            {'comment': ' some awesome comment  ', 'macro_ids': ['5', '77']},
            'first',
            True,
            [],
            {
                'message_id': None,
                'message_text': 'some awesome comment',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'update_metadata': {'ticket_status': 'open'},
                'user_guid': '10000000-0000-0000-0000-000000000001',
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'defer',
                    'comment': 'some awesome comment',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'macro_ids': ['5', '77'],
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['5', '77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'query_params': {'reopen_at': '2018-06-15T15:34:00+0000'},
                    'reopen_at': datetime.datetime(2018, 6, 15, 15, 34),
                    'tags_added': ['3', '4', 'check_macro_id_tag'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                    ],
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'comment': 'normal comment  ', 'macro_ids': ['5', '77']},
            'first',
            True,
            [],
            {
                'message_id': None,
                'message_text': 'normal comment',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'update_metadata': {'ticket_status': 'open'},
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'defer',
                    'comment': 'normal comment',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'macro_ids': ['5', '77'],
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['5', '77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'query_params': {'reopen_at': '2018-06-15T15:34:00+0000'},
                    'reopen_at': datetime.datetime(2018, 6, 15, 15, 34),
                    'tags_added': ['3', '4', 'check_macro_id_tag'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                    ],
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2b0',
            {'comment': 'startrack comment  '},
            'first',
            False,
            ['3', '4', 'check_macro_id_tag', 'tag1', 'tag2'],
            None,
            [
                {
                    'action_id': 'test_uid',
                    'action': 'defer',
                    'comment': 'startrack comment',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'query_params': {'reopen_at': '2018-06-15T15:34:00+0000'},
                    'reopen_at': datetime.datetime(2018, 6, 15, 15, 34),
                    'tags_added': ['3', '4', 'check_macro_id_tag'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                    ],
                },
            ],
        ),
        (
            '5b2cae5cb4282a976914c2c9',
            {'comment': 'normal comment  '},
            'driver_online',
            True,
            [],
            {
                'message_id': None,
                'message_text': 'normal comment',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'update_metadata': {'ticket_status': 'open'},
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'defer',
                    'comment': 'normal comment',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'driver_online',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'query_params': {'reopen_at': '2018-06-15T15:34:00+0000'},
                    'reopen_at': datetime.datetime(2018, 6, 15, 15, 34),
                    'tags_added': ['3', '4', 'check_macro_id_tag'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                    ],
                },
            ],
        ),
        (
            '5b2cae5cb4282a976914c2c9',
            {'comment': 'normal {{media_subscription_cancel:123}}comment  '},
            'driver_online',
            True,
            [],
            {
                'message_id': None,
                'message_text': 'normal comment',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'update_metadata': {'ticket_status': 'open'},
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'defer',
                    'comment': 'normal comment',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'driver_online',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'cancel_result',
                            'value': 'wait',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'query_params': {'reopen_at': '2018-06-15T15:34:00+0000'},
                    'reopen_at': datetime.datetime(2018, 6, 15, 15, 34),
                    'succeed_operations': ['subscription_cancel'],
                    'tags_added': ['3', '4', 'check_macro_id_tag'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                    ],
                },
            ],
        ),
    ],
)
@pytest.mark.config(CHATTERBOX_HISTORY_TAGS_ADDED=True)
@pytest.mark.now(NOW.isoformat())
async def test_defer(
        cbox,
        mock,
        monkeypatch,
        task_id,
        extra_data,
        expected_line,
        support_chat_call,
        expected_startrack_tags,
        expected_support_chat_result,
        expected_history,
        mock_chat_get_history,
        mock_chat_add_update,
        mock_st_get_ticket,
        mock_st_create_comment,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        mock_st_transition,
        mock_st_update_ticket,
        mock_random_str_uuid,
        mockserver,
):
    mock_chat_get_history({'messages': []})
    mock_st_get_all_attachments()
    mock_st_get_comments([])
    st_update_ticket = mock_st_update_ticket('open')
    mock_random_str_uuid()

    @mockserver.json_handler('/music/stop-active-interval/')
    def _dummy_subscription_cancel(request):
        return {'result': 'wait'}

    data = {'macro_id': '77', 'themes': ['1', '2'], 'themes_tree': ['3']}
    if extra_data is not None:
        data.update(extra_data)

    await cbox.post(
        '/v1/tasks/{}/defer'.format(task_id),
        params={'reopen_at': '2018-06-15T15:34:00+0000'},  # NOW + 3 hours
        data=data,
    )
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )

    assert task['status'] == 'deferred'
    task['history'][0].pop('external_id', None)
    assert task['history'] == expected_history

    if support_chat_call:
        add_update_call = mock_chat_add_update.calls[0]
        assert add_update_call['args'] == (task['external_id'],)
        assert add_update_call['kwargs'].pop('log_extra')
        assert add_update_call['kwargs'] == expected_support_chat_result
    else:
        assert not mock_chat_add_update.calls

    if expected_startrack_tags:
        assert (
            st_update_ticket.calls[0]['kwargs']['tags']
            == expected_startrack_tags
        )

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            str(task_id),
        )
        assert len(result) == 1
        assert result[0]['count'] == 0


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'driver_phone': 'phones',
            'park_phone': 'phones',
        },
    },
)
async def test_defer_with_promocode(
        cbox,
        patch,
        mock_chat_get_history,
        mock_personal,
        mock_random_str_uuid,
):
    mock_chat_get_history({'messages': []})
    mock_random_str_uuid()
    task_id = bson.ObjectId('5b2cae5cb2682a976914c2a4')

    @patch('taxi.clients.support_chat.SupportChatApiClient.add_update')
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    @patch('taxi.clients.admin.AdminApiClient.generate_promocode')
    async def _dummy_generate_promocode(*args, **kwargs):
        return {'code': 'promo123'}

    cbox.set_user('some_user')
    await cbox.post(
        '/v1/tasks/{}/defer'.format(task_id),
        params={'reopen_at': '2018-06-15T15:34:00+0000'},
        data={'comment': 'Промокод {{promo:200}} на {{nominal}} {{currency}}'},
    )
    assert cbox.status == http.HTTPStatus.OK

    generate_promocode_call = _dummy_generate_promocode.calls[0]
    assert generate_promocode_call['args'] == (
        'yandex',
        'excs',
        '+71234567890',
        '5b2cae5cb2682a976914c2a4',
    )
    assert generate_promocode_call['kwargs']['cookies'] == {
        'Session_id': 'some_user_sid',
        'yandexuid': 'some_user_uid',
        'sessionid2': 'some_user_sid2',
    }

    add_update_call = _dummy_add_update.calls[0]
    assert add_update_call['kwargs'].pop('log_extra')
    assert add_update_call['kwargs'] == {
        'message_id': None,
        'message_text': 'Промокод promo123 на 200 ₽',
        'message_sender_role': 'support',
        'message_sender_id': 'superuser',
        'message_metadata': {'promocodes': [{'code': 'promo123'}]},
        'update_metadata': {'ticket_status': 'open'},
    }

    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    assert task['history'][-1] == {
        'action_id': 'test_uid',
        'action': 'defer',
        'reopen_at': datetime.datetime(2018, 6, 15, 15, 34),
        'in_addition': False,
        'comment': 'Промокод promo123 на 200 ₽',
        'promocodes': [{'code': 'promo123'}],
        'login': 'superuser',
        'query_params': {'reopen_at': '2018-06-15T15:34:00+0000'},
        'created': datetime.datetime(2018, 6, 15, 12, 34),
        'line': 'first',
    }


async def test_defer_promocode_adding(cbox, patch, mock_chat_get_history):
    mock_chat_get_history({'messages': []})

    @patch('taxi.clients.support_chat.SupportChatApiClient.add_update')
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    cbox.set_user('some_user')
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a4/defer',
        params={'reopen_at': '2018-06-15T15:34:00+0000'},
        data={'comment': 'Промокод {{add_promo:promo123}}'},
    )
    assert cbox.status == http.HTTPStatus.OK

    add_update_call = _dummy_add_update.calls[0]
    assert add_update_call['kwargs'].pop('log_extra')
    assert add_update_call['kwargs'] == {
        'message_id': None,
        'message_text': 'Промокод promo123',
        'message_sender_role': 'support',
        'message_sender_id': 'superuser',
        'message_metadata': {'promocodes': [{'code': 'promo123'}]},
        'update_metadata': {'ticket_status': 'open'},
    }


@pytest.mark.parametrize('handler', ['close', 'close_with_tvm'])
@pytest.mark.parametrize(
    'task_id_str, query, expected_history, expected_update_kwargs,'
    'expected_comment_kwargs, expected_transition_kwargs',
    [
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'chat closed',
                'comment_metadata': {'encrypt_key': '321'},
                'macro_id': '77',
                'themes': ['1', '2'],
                'tags': ['extra_tag'],
                'hidden_comment': 'hidden',
                'hidden_comment_metadata': {'encrypt_key': '123'},
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'close',
                    'created': NOW,
                    'hidden_comment': 'hidden',
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'chat closed',
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_added': [
                        '3',
                        '4',
                        'check_macro_id_tag',
                        'extra_tag',
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                        {'change_type': 'add', 'tag': 'extra_tag'},
                    ],
                },
            ],
            {
                'message_text': 'chat closed',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': {'encrypt_key': '321'},
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': True,
                    'retry_csat_request': False,
                },
            },
            None,
            None,
        ),
        pytest.param(
            '5c2cae5cb2682a976914c2a1',
            {
                'comment': 'chat closed',
                'macro_id': '77',
                'themes': ['1', '2'],
                'tags': ['extra_tag'],
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'close',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'chat closed',
                    'in_addition': False,
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': '77',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['77'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                    ],
                    'tags_added': [
                        '3',
                        '4',
                        'check_macro_id_tag',
                        'extra_tag',
                    ],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': 'check_macro_id_tag'},
                        {'change_type': 'add', 'tag': 'extra_tag'},
                    ],
                },
            ],
            {
                'message_text': 'chat closed',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': True,
                    'retry_csat_request': False,
                },
                'user_guid': '10000000-0000-0000-0000-000000000001',
            },
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'comment': 'chat closed', 'tags': ['no_csat', 'UpperКир']},
            [
                {
                    'action_id': 'test_uid',
                    'action': 'close',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'chat closed',
                    'in_addition': False,
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'no_csat'},
                        {'change_type': 'add', 'tag': 'upperкир'},
                    ],
                    'tags_added': ['upperкир', 'no_csat'],
                },
            ],
            {
                'message_text': 'chat closed',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': False,
                    'retry_csat_request': False,
                },
            },
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2b0',
            {
                'comment': 'chat closed',
                'macro_id': 'some_macro_id',
                'themes': ['1'],
                'themes_tree': ['1', '2'],
                'attachment_ids': ['12345'],
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'close',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'chat closed',
                    'in_addition': False,
                    'external_id': '1005005505045045040',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'some_macro_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['some_macro_id'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'theme_name',
                            'value': 'Theme::Subtheme 1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes_tree',
                            'value': [1, 2],
                        },
                    ],
                    'tags_added': ['3', '4'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                    ],
                },
            ],
            None,
            {
                'email_from': 'test@support',
                'email_subject': 'Re: Zomg!',
                'email_cc': ['toert@yandex', 'i@love.memes'],
                'email_text': 'chat closed',
                'email_to': 'some@email',
                'text': 'superuser написал письмо',
                'signature_selection': True,
                'attachment_ids': ['12345'],
            },
            {'data': {'resolution': 'fixed'}, 'transition': 'close'},
        ),
        (
            '5b2cae5cb2682a976914c2b0',
            {
                'comment': 'chat closed',
                'macro_id': 'some_macro_id',
                'themes_tree': [],
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'close',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'chat closed',
                    'in_addition': False,
                    'external_id': '1005005505045045040',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'some_macro_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['some_macro_id'],
                        },
                    ],
                },
            ],
            None,
            {
                'email_from': 'test@support',
                'email_subject': 'Re: Zomg!',
                'email_cc': ['toert@yandex', 'i@love.memes'],
                'email_text': 'chat closed',
                'email_to': 'some@email',
                'text': 'superuser написал письмо',
                'signature_selection': True,
                'attachment_ids': None,
            },
            {'data': {'resolution': 'fixed'}, 'transition': 'close'},
        ),
        (
            '5b2cae5cb2682a976914c2b0',
            {
                'comment': 'chat{{media_subscription_cancel:123}} closed',
                'macro_ids': ['some_macro_id_2', 'some_macro_id'],
                'themes': ['1', '2'],
                'themes_tree': ['1', '4'],
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'close',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'chat closed',
                    'in_addition': False,
                    'external_id': '1005005505045045040',
                    'macro_ids': ['some_macro_id_2', 'some_macro_id'],
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'cancel_result',
                            'value': 'cancel',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'some_macro_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['some_macro_id', 'some_macro_id_2'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'theme_name',
                            'value': 'Theme::Subtheme 2',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes_tree',
                            'value': [1, 4],
                        },
                    ],
                    'succeed_operations': ['subscription_cancel'],
                    'tags_added': ['3', '4', '5'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': '5'},
                    ],
                },
            ],
            None,
            {
                'email_from': 'test@support',
                'email_subject': 'Re: Zomg!',
                'email_cc': ['toert@yandex', 'i@love.memes'],
                'email_text': 'chat closed',
                'email_to': 'some@email',
                'text': 'superuser написал письмо',
                'signature_selection': True,
                'attachment_ids': None,
            },
            {'data': {'resolution': 'fixed'}, 'transition': 'close'},
        ),
    ],
)
@pytest.mark.config(CHATTERBOX_HISTORY_TAGS_ADDED=True)
@pytest.mark.now(NOW.isoformat())
async def test_close(
        cbox,
        handler,
        task_id_str,
        query,
        expected_history,
        expected_update_kwargs,
        expected_comment_kwargs,
        expected_transition_kwargs,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_create_comment,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        mock_st_transition,
        mock_st_update_ticket,
        mock_random_str_uuid,
        mockserver,
):
    mock_chat_get_history({'messages': []})
    task_id = bson.objectid.ObjectId(task_id_str)
    mock_st_get_comments([])
    mock_st_get_all_attachments()
    mock_st_update_ticket('close')
    mock_random_str_uuid()

    @mockserver.json_handler('/music/stop-active-interval/')
    def _dummy_subscription_cancel(request):
        return {'result': 'cancel'}

    await cbox.post('/v1/tasks/{}/{}'.format(task_id_str, handler), data=query)
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert task['status'] == 'closed'
    assert task['history'] == expected_history

    if expected_update_kwargs is not None:
        add_update_call = mock_chat_add_update.calls[0]
        assert add_update_call['args'] == (task['external_id'],)
        add_update_call['kwargs'].pop('log_extra')
        assert add_update_call['kwargs'] == expected_update_kwargs

    if expected_comment_kwargs is not None:
        create_comment_call = mock_st_create_comment.calls[0]
        assert create_comment_call['args'] == (task['external_id'],)
        create_comment_call['kwargs'].pop('log_extra')
        assert create_comment_call['kwargs'] == expected_comment_kwargs

    if expected_transition_kwargs is not None:
        execute_transition_call = mock_st_transition.calls[0]
        assert execute_transition_call['ticket'] == task['external_id']
        assert execute_transition_call['kwargs'] == expected_transition_kwargs

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            task_id_str,
        )
        assert len(result) == 1
        assert result[0]['count'] == 0


@pytest.mark.parametrize('handler', ['close', 'communicate', 'comment'])
@pytest.mark.parametrize(
    'task_id_str, data, expected_update_kwargs,',
    [
        pytest.param(
            '5b2cae5cb2682a976914c2a1',
            {
                'comment': 'chat message',
                'comment_metadata': {'encrypt_key': '321'},
                'macro_id': '77',
                'themes': ['1', '2'],
                'tags': ['extra_tag'],
                'hidden_comment': 'hidden',
                'hidden_comment_metadata': {'encrypt_key': '123'},
                'attachments_meta': [{'id': '12345', 'source': 'mds'}],
            },
            {
                'message_text': 'chat message',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': {
                    'encrypt_key': '321',
                    'attachments': [{'id': '12345', 'source': 'mds'}],
                },
                'message_id': None,
            },
        ),
        (
            '5b2cae5cb2683a976914c2c9',
            {
                'comment': 'chat message',
                'macro_id': 'some_macro_id',
                'themes': ['1'],
                'themes_tree': ['1', '2'],
                'attachments_meta': [{'id': '12345', 'source': 'fintech-s3'}],
            },
            {
                'message_text': 'chat message',
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': {
                    'attachments': [{'id': '12345', 'source': 'fintech-s3'}],
                },
                'message_id': None,
            },
        ),
    ],
)
@pytest.mark.config(CHATTERBOX_HISTORY_TAGS_ADDED=True)
@pytest.mark.now(NOW.isoformat())
async def test_attachments_meta(
        cbox,
        handler,
        task_id_str,
        data,
        expected_update_kwargs,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_random_str_uuid,
        mockserver,
):
    mock_chat_get_history({'messages': []})
    task_id = bson.objectid.ObjectId(task_id_str)
    mock_random_str_uuid()

    await cbox.post('/v1/tasks/{}/{}'.format(task_id_str, handler), data=data)
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})

    if handler == 'close':
        expected_update_kwargs['update_metadata'] = {
            'ticket_status': 'solved',
            'ask_csat': True,
            'retry_csat_request': False,
        }
    elif handler == 'communicate':
        expected_update_kwargs['update_metadata'] = {'ticket_status': 'open'}
    elif handler == 'comment':
        expected_update_kwargs['update_metadata'] = {
            'ticket_status': 'pending',
        }

    add_update_call = mock_chat_add_update.calls[0]
    assert add_update_call['args'] == (task['external_id'],)
    add_update_call['kwargs'].pop('log_extra')
    assert add_update_call['kwargs'] == expected_update_kwargs


@pytest.mark.parametrize(
    (
        'task_id_str',
        'handler',
        'query',
        'params',
        'expected_status',
        'expected_task_status',
    ),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            'communicate',
            {
                'hidden_comment': 'some hidden comment',
                'macro_id': 'some_macro_id',
                'themes': ['1'],
                'themes_tree': ['1', '2'],
                'attachment_ids': ['12345'],
            },
            None,
            http.HTTPStatus.BAD_REQUEST,
            'in_progress',
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'defer',
            {
                'hidden_comment': 'some hidden comment',
                'macro_id': 'some_macro_id',
                'themes': ['1'],
                'themes_tree': ['1', '2'],
                'attachment_ids': ['12345'],
            },
            {'reopen_at': '2018-06-15T15:34:00+0000'},
            http.HTTPStatus.BAD_REQUEST,
            'in_progress',
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'communicate',
            {
                'macro_id': 'some_macro_id',
                'themes': ['1'],
                'themes_tree': ['1', '2'],
            },
            None,
            http.HTTPStatus.BAD_REQUEST,
            'in_progress',
        ),
    ],
)
@pytest.mark.config(CHATTERBOX_HISTORY_TAGS_ADDED=True)
@pytest.mark.now(NOW.isoformat())
async def test_action_fields_error(
        cbox,
        task_id_str,
        handler,
        query,
        params,
        expected_status,
        expected_task_status,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_create_comment,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        mock_st_transition,
        mock_st_update_ticket,
):
    mock_chat_get_history({'messages': []})
    task_id = bson.objectid.ObjectId(task_id_str)
    mock_st_get_comments([])
    mock_st_get_all_attachments()
    mock_st_update_ticket('close')
    await cbox.post(
        '/v1/tasks/{}/{}'.format(task_id_str, handler),
        data=query,
        params=params,
    )
    assert cbox.status == expected_status

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert task['status'] == expected_task_status


@pytest.mark.parametrize(
    (
        'task_id',
        'data',
        'expected_history',
        'expected_comment_kwargs',
        'expected_transition_kwargs',
        'expected_salesforce_update',
    ),
    [
        (
            '5b2cae5cb2682a976914c2b0',
            {
                'comment': 'chat closed',
                'macro_ids': ['some_macro_id_2', 'some_macro_id'],
                'themes': ['1', '2'],
                'themes_tree': ['1', '4'],
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'external_comment',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'comment': 'chat closed',
                    'in_addition': False,
                    'external_id': '1005005505045045040',
                    'macro_ids': ['some_macro_id_2', 'some_macro_id'],
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'some_macro_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['some_macro_id', 'some_macro_id_2'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'theme_name',
                            'value': 'Theme::Subtheme 2',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes_tree',
                            'value': [1, 4],
                        },
                    ],
                    'tags_added': ['3', '4', '5'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': '5'},
                    ],
                },
            ],
            {
                'attachment_ids': None,
                'email_cc': ['toert@yandex', 'i@love.memes'],
                'email_from': 'test@support',
                'email_subject': 'Re: Zomg!',
                'email_text': 'chat closed',
                'email_to': 'some@email',
                'signature_selection': True,
                'text': 'superuser написал письмо',
            },
            {'data': {'resolution': 'fixed'}, 'transition': 'close'},
            {
                'data': {'Comments': 'chat closed'},
                'field_name': 'Partner1_Case_ID__c',
                'field_value': 'some_queue-1',
            },
        ),
    ],
)
@pytest.mark.config(
    CHATTERBOX_HISTORY_TAGS_ADDED=True,
    CHATTERBOX_EXTERNAL_SALESFORCE={'enabled': True},
)
@pytest.mark.now(NOW.isoformat())
async def test_external_comment(
        cbox,
        task_id,
        data,
        expected_history,
        expected_comment_kwargs,
        expected_transition_kwargs,
        expected_salesforce_update,
        mock_st_get_ticket,
        mock_st_create_comment,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        mock_st_transition,
        mock_st_update_ticket,
        mock_external_salesforce_auth,
        mock_external_salesforce_update,
        mockserver,
        mock_random_str_uuid,
):
    mock_st_get_comments([])
    mock_st_get_all_attachments()
    mock_st_update_ticket('close')
    mock_random_str_uuid()

    await cbox.post('/v1/tasks/{}/external_comment'.format(task_id), data=data)
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )
    assert task['status'] == 'closed'
    assert task['history'] == expected_history

    if expected_comment_kwargs is not None:
        create_comment_call = mock_st_create_comment.calls[0]
        assert create_comment_call['args'] == (task['external_id'],)
        create_comment_call['kwargs'].pop('log_extra')
        assert create_comment_call['kwargs'] == expected_comment_kwargs

    if expected_transition_kwargs is not None:
        execute_transition_call = mock_st_transition.calls[0]
        assert execute_transition_call['ticket'] == task['external_id']
        assert execute_transition_call['kwargs'] == expected_transition_kwargs

    if expected_salesforce_update is not None:
        execute_sf_call = mock_external_salesforce_update.calls[0]
        execute_sf_call['kwargs'].pop('log_extra')
        assert execute_sf_call['kwargs'] == expected_salesforce_update

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            task_id,
        )
        assert len(result) == 1
        assert result[0]['count'] == 0


@pytest.mark.parametrize(
    (
        'task_id',
        'handler',
        'data',
        'expected_status',
        'expected_task_status',
        'expected_history',
        'expected_add_update',
    ),
    [
        (
            '5b2cae5cb2682a976914c2a6',
            'close_with_tvm',
            {'comment': 'chat closed'},
            http.HTTPStatus.OK,
            'closed',
            [
                {
                    'action_id': 'test_uid',
                    'action': 'close',
                    'comment': 'chat closed',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'corp',
                    'login': 'superuser',
                },
            ],
            {
                'message_id': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'chat closed',
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': True,
                    'retry_csat_request': False,
                },
                'message_metadata': None,
            },
        ),
        (
            '5b2cae5cb2682a976914c2a9',
            'close_with_tvm',
            {'comment': 'chat closed'},
            http.HTTPStatus.OK,
            'closed',
            [
                {
                    'action_id': 'test_uid',
                    'action': 'close',
                    'comment': 'chat closed',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                },
            ],
            {
                'message_id': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'chat closed',
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': True,
                    'retry_csat_request': False,
                },
                'message_metadata': None,
            },
        ),
        (
            '5b2cae5cb2682a976914c298',
            'close_with_tvm',
            {'comment': 'chat closed'},
            http.HTTPStatus.BAD_REQUEST,
            'in_progress',
            None,
            None,
        ),
        (
            '5b2cae5db2682a976914c2a2',
            'close_with_tvm',
            {'comment': 'chat closed'},
            http.HTTPStatus.BAD_REQUEST,
            'closed',
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a6',
            'communicate_with_tvm',
            {'comment': 'chat not closed'},
            http.HTTPStatus.OK,
            'deferred',
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'comment': 'chat not closed',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'corp',
                    'login': 'superuser',
                },
            ],
            {
                'message_id': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'chat not closed',
                'update_metadata': {'ticket_status': 'open'},
                'message_metadata': None,
            },
        ),
        (
            '5b2cae5cb2682a976914c2a9',
            'communicate_with_tvm',
            {'comment': 'chat not closed'},
            http.HTTPStatus.OK,
            'reopened',
            [
                {
                    'action_id': 'test_uid',
                    'action': 'communicate',
                    'comment': 'chat not closed',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                },
            ],
            {
                'message_id': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': 'chat not closed',
                'update_metadata': {'ticket_status': 'open'},
                'message_metadata': None,
            },
        ),
        (
            '5b2cae5cb2682a976914c298',
            'communicate_with_tvm',
            {'comment': 'chat not closed'},
            http.HTTPStatus.BAD_REQUEST,
            'in_progress',
            None,
            None,
        ),
        (
            '5b2cae5db2682a976914c2a2',
            'communicate_with_tvm',
            {'comment': 'chat not closed'},
            http.HTTPStatus.BAD_REQUEST,
            'closed',
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a6',
            'dismiss_with_tvm',
            {},
            http.HTTPStatus.OK,
            'closed',
            [
                {
                    'action_id': 'test_uid',
                    'action': 'dismiss',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'corp',
                    'login': 'superuser',
                },
            ],
            {
                'message_id': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': False,
                    'retry_csat_request': False,
                },
                'message_metadata': None,
            },
        ),
        (
            '5b2cae5cb2682a976914c2a9',
            'dismiss_with_tvm',
            {},
            http.HTTPStatus.OK,
            'closed',
            [
                {
                    'action_id': 'test_uid',
                    'action': 'dismiss',
                    'created': NOW,
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                },
            ],
            {
                'message_id': None,
                'message_sender_id': 'superuser',
                'message_sender_role': 'support',
                'message_text': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': False,
                    'retry_csat_request': False,
                },
                'message_metadata': None,
            },
        ),
        (
            '5b2cae5cb2682a976914c298',
            'dismiss_with_tvm',
            {},
            http.HTTPStatus.BAD_REQUEST,
            'in_progress',
            None,
            None,
        ),
        (
            '5b2cae5db2682a976914c2a2',
            'dismiss_with_tvm',
            {},
            http.HTTPStatus.BAD_REQUEST,
            'closed',
            None,
            None,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_tvm_actions(
        cbox,
        monkeypatch,
        patch_auth,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_random_str_uuid,
        task_id,
        handler,
        data,
        expected_status,
        expected_task_status,
        expected_history,
        expected_add_update,
):
    mock_chat_get_history({'messages': []})
    patch_auth(login='test_login', superuser=False)
    mock_random_str_uuid()

    await cbox.post('/v1/tasks/{}/{}'.format(task_id, handler), data=data)
    assert cbox.status == expected_status

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )
    assert task['status'] == expected_task_status
    if expected_status == http.HTTPStatus.OK:
        assert task['history'] == expected_history
        assert task['support_admin'] == 'superuser'

    if expected_add_update is None:
        assert not mock_chat_add_update.calls
    else:
        add_update_call = mock_chat_add_update.calls[0]['kwargs']
        add_update_call.pop('log_extra')
        assert add_update_call == expected_add_update


@pytest.mark.now(NOW.isoformat())
async def test_close_on_reopen(cbox, monkeypatch, mock, mock_chat_get_history):
    mock_chat_get_history({'messages': []})

    @mock
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a3/close',
        data={'comment': 'chat closed'},
    )
    assert cbox.status == http.HTTPStatus.BAD_REQUEST

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId('5b2cae5cb2682a976914c2a3')},
    )
    assert task['status'] == 'reopened'
    assert _dummy_add_update.calls == []


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'driver_phone': 'phones',
            'park_phone': 'phones',
        },
    },
)
async def test_close_with_promocode(
        cbox,
        patch,
        mock_chat_get_history,
        mock_personal,
        mock_random_str_uuid,
):
    mock_chat_get_history({'messages': []})
    task_id = bson.ObjectId('5b2cae5cb2682a976914c2a4')
    mock_random_str_uuid()

    @patch('taxi.clients.support_chat.SupportChatApiClient.add_update')
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    @patch('taxi.clients.admin.AdminApiClient.generate_promocode')
    async def _dummy_generate_promocode(*args, **kwargs):
        return {'code': 'promo123'}

    cbox.set_user('some_user')
    await cbox.post(
        '/v1/tasks/{}/close'.format(task_id),
        data={'comment': 'Промокод {{promo:200}} на {{nominal}} {{currency}}'},
        headers={'X-Real-IP': '127.0.0.1', 'X-Forwarded-For': 'test'},
    )
    assert cbox.status == http.HTTPStatus.OK

    generate_promocode_call = _dummy_generate_promocode.calls[0]
    assert generate_promocode_call['args'] == (
        'yandex',
        'excs',
        '+71234567890',
        '5b2cae5cb2682a976914c2a4',
    )
    assert generate_promocode_call['kwargs'].pop('log_extra')
    assert generate_promocode_call['kwargs'] == {
        'cookies': {
            'Session_id': 'some_user_sid',
            'sessionid2': 'some_user_sid2',
            'yandexuid': 'some_user_uid',
        },
        'real_ip': '127.0.0.1',
        'x_forwarded_for': 'test',
        'token': None,
        'enable_csrf': True,
    }

    add_update_call = _dummy_add_update.calls[0]
    add_update_call['kwargs'].pop('log_extra')
    assert add_update_call['kwargs'] == {
        'message_text': 'Промокод promo123 на 200 ₽',
        'message_sender_role': 'support',
        'message_sender_id': 'superuser',
        'message_metadata': {'promocodes': [{'code': 'promo123'}]},
        'message_id': None,
        'update_metadata': {
            'ticket_status': 'solved',
            'ask_csat': True,
            'retry_csat_request': False,
        },
    }

    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    assert task['history'][-1] == {
        'action_id': 'test_uid',
        'action': 'close',
        'in_addition': False,
        'comment': 'Промокод promo123 на 200 ₽',
        'promocodes': [{'code': 'promo123'}],
        'login': 'superuser',
        'created': datetime.datetime(2018, 6, 15, 12, 34),
        'line': 'first',
    }


@pytest.mark.now(NOW.isoformat())
async def test_close_with_activity_amnesty(
        cbox, patch, mock_chat_get_history, mock_random_str_uuid,
):
    mock_chat_get_history({'messages': []})
    mock_random_str_uuid()
    task_id = bson.ObjectId('5b2cae5cb2682a976914c2a4')

    @patch('taxi.clients.support_chat.SupportChatApiClient.add_update')
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    @patch('taxi.clients.admin.AdminApiClient.activity_amnesty')
    async def _dummy_activity_amnesty(*args, **kwargs):
        return {}

    cbox.set_user('some_user')
    await cbox.post(
        '/v1/tasks/{}/close'.format(task_id),
        data={'comment': 'Активность восстановлена {{activity_amnesty:123}}'},
        headers={'X-Real-IP': '127.0.0.1', 'X-Forwarded-For': 'test'},
    )
    assert cbox.status == http.HTTPStatus.OK

    amnesty_call = _dummy_activity_amnesty.calls[0]
    assert amnesty_call['kwargs'].pop('log_extra')
    assert amnesty_call['kwargs']['data'].pop('idempotency_token')
    assert amnesty_call['kwargs'] == {
        'data': {'udid': None, 'mode': 'additive', 'value': 123},
        'cookies': {
            'Session_id': 'some_user_sid',
            'sessionid2': 'some_user_sid2',
            'yandexuid': 'some_user_uid',
        },
        'token': 'api_admin_py3_oauth_token',
        'real_ip': '127.0.0.1',
        'x_forwarded_for': 'test',
    }

    add_update_call = _dummy_add_update.calls[0]
    add_update_call['kwargs'].pop('log_extra')
    assert add_update_call['kwargs'] == {
        'message_text': 'Активность восстановлена ',
        'message_sender_role': 'support',
        'message_sender_id': 'superuser',
        'message_metadata': None,
        'message_id': None,
        'update_metadata': {
            'ticket_status': 'solved',
            'ask_csat': True,
            'retry_csat_request': False,
        },
    }

    task = await cbox.app.db.support_chatterbox.find_one({'_id': task_id})
    assert task['history'][-1] == {
        'action_id': 'test_uid',
        'action': 'close',
        'in_addition': False,
        'comment': 'Активность восстановлена ',
        'succeed_operations': ['activity_amnesty'],
        'login': 'superuser',
        'created': datetime.datetime(2018, 6, 15, 12, 34),
        'line': 'first',
    }


async def test_close_promocode_adding(cbox, patch, mock_chat_get_history):
    mock_chat_get_history({'messages': []})

    @patch('taxi.clients.support_chat.SupportChatApiClient.add_update')
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    cbox.set_user('some_user')
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a4/close',
        data={'comment': 'Промокод {{add_promo:promo123}}'},
    )
    assert cbox.status == http.HTTPStatus.OK

    add_update_call = _dummy_add_update.calls[0]
    add_update_call['kwargs'].pop('log_extra')
    assert add_update_call['kwargs'] == {
        'message_text': 'Промокод promo123',
        'message_sender_role': 'support',
        'message_sender_id': 'superuser',
        'message_metadata': {'promocodes': [{'code': 'promo123'}]},
        'message_id': None,
        'update_metadata': {
            'ask_csat': True,
            'ticket_status': 'solved',
            'retry_csat_request': False,
        },
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CRON_SERVICE_USAGE={
        'use_service_except_from_disabled': True,
        'tasks_disabled_using_service': [],
    },
    DRIVER_SUPPORT_PROMOCODE_MAPPING_BY_COUNTRY={
        'rus': {
            'series': {
                '1': {'id': '1_rus'},
                'loyalty_3': {'id': '3_rus_loyal', 'duration': 3},
                '24': {'id': '24h'},
            },
        },
    },
    USE_CSRF_FOR_PROMOCODE_TOKEN=False,
)
@pytest.mark.parametrize(
    [
        'task_id',
        'data',
        'legacy_mode',
        'expected_admin_url',
        'expected_admin_request',
        'support_chat_message',
        'expected_code',
        'expected_history',
    ],
    [
        (
            '5cb080c7779fb32f801581b8',
            {
                'comment': (
                    'Промокод {{driver_promo:loyalty_3:причина_выдачи}}'
                    ' на {{duration}} часа'
                ),
            },
            True,
            '/api/driver_promocodes/add/',
            {
                'clid': 'clid',
                'uuid': 'uuid',
                'description': 'причина выдачи',
                'series_id': '3_rus_loyal',
                'ticket_type': 'chatterbox',
                'zendesk_ticket': '5cb080c7779fb32f801581b8',
            },
            {
                'sender': {'id': 'superuser', 'role': 'support'},
                'text': 'Промокод 12345 на 3 часа',
                'metadata': {'promocodes': [{'code': '12345'}]},
            },
            200,
            {
                'action_id': 'test_uid',
                'action': 'close',
                'in_addition': False,
                'comment': 'Промокод 12345 на 3 часа',
                'succeed_operations': ['promocode'],
                'promocodes': [{'code': '12345'}],
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
            },
        ),
        (
            '5cb080c7779fb32f801581b8',
            {
                'comment': (
                    'Промокод {{driver_promo:25:причина_выдачи}} на '
                    '{{duration}} часа'
                ),
            },
            True,
            None,
            {},
            {},
            424,
            None,
        ),
        (
            '5cb080c7779fb32f801581b8',
            {
                'comment': (
                    'Промокод {{driver_promo:24:причинавыдачи}} на '
                    '{{duration}} часа'
                ),
            },
            True,
            '/api/driver_promocodes/add/',
            {
                'clid': 'clid',
                'uuid': 'uuid',
                'description': 'причинавыдачи',
                'series_id': '24h',
                'ticket_type': 'chatterbox',
                'zendesk_ticket': '5cb080c7779fb32f801581b8',
            },
            {
                'sender': {'id': 'superuser', 'role': 'support'},
                'text': 'Промокод 12345 на 24 часа',
                'metadata': {'promocodes': [{'code': '12345'}]},
            },
            200,
            {
                'action_id': 'test_uid',
                'action': 'close',
                'in_addition': False,
                'comment': 'Промокод 12345 на 24 часа',
                'succeed_operations': ['promocode'],
                'promocodes': [{'code': '12345'}],
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
            },
        ),
        (
            '5cb080c7779fb32f801581b9',
            {
                'comment': (
                    'Промокод {{driver_promo:24:причинавыдачи}} на '
                    '{{duration}} часа'
                ),
            },
            True,
            None,
            {},
            {},
            424,
            None,
        ),
        (
            '5cb080c7779fb32f801581b7',
            {
                'comment': (
                    'Промокод {{driver_promo:24:причинавыдачи}} на '
                    '{{duration}} часа'
                ),
            },
            True,
            None,
            {},
            {},
            424,
            None,
        ),
        (
            '5cb080c7779fb32f801581b8',
            {
                'comment': (
                    'Промокод {{driver_promo:loyalty_3:причина_выдачи}}'
                    ' на {{duration}} часа'
                ),
            },
            False,
            '/driver-promocodes/internal/v1/promocodes',
            {
                'entity_type': 'park_driver_profile_id',
                'entity_id': 'some_park_driver_profile_id',
                'series_name': '3_rus_loyal',
                'tickets': ['5cb080c7779fb32f801581b8'],
                'description': 'причина выдачи',
            },
            {
                'sender': {'id': 'superuser', 'role': 'support'},
                'text': 'Промокод  на 3 часа',
                'metadata': {
                    'promocodes': [{'code': 'new_driver_promocode_id'}],
                },
            },
            200,
            {
                'action_id': 'test_uid',
                'action': 'close',
                'in_addition': False,
                'comment': 'Промокод  на 3 часа',
                'succeed_operations': ['promocode'],
                'promocodes': [{'code': 'new_driver_promocode_id'}],
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
            },
        ),
        (
            '5cb080c7779fb32f801581b8',
            {
                'comment': (
                    'Промокод {{driver_promo:24:причинавыдачи}} на '
                    '{{duration}} часа'
                ),
            },
            False,
            '/driver-promocodes/internal/v1/promocodes',
            {
                'entity_type': 'park_driver_profile_id',
                'entity_id': 'some_park_driver_profile_id',
                'series_name': '24h',
                'tickets': ['5cb080c7779fb32f801581b8'],
                'description': 'причинавыдачи',
            },
            {
                'sender': {'id': 'superuser', 'role': 'support'},
                'text': 'Промокод  на 24 часа',
                'metadata': {
                    'promocodes': [{'code': 'new_driver_promocode_id'}],
                },
            },
            200,
            {
                'action_id': 'test_uid',
                'action': 'close',
                'in_addition': False,
                'comment': 'Промокод  на 24 часа',
                'succeed_operations': ['promocode'],
                'promocodes': [{'code': 'new_driver_promocode_id'}],
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
            },
        ),
        (
            '5cb080c7779fb32f801581b8',
            {
                'comment': (
                    'Промокод {{driver_promo:24:причинавыдачи}} на '
                    '{{duration}} часа'
                ),
                'request_id': 'some_request_id_123',
            },
            False,
            '/driver-promocodes/internal/v1/promocodes',
            {
                'entity_type': 'park_driver_profile_id',
                'entity_id': 'some_park_driver_profile_id',
                'series_name': '24h',
                'tickets': ['5cb080c7779fb32f801581b8'],
                'description': 'причинавыдачи',
            },
            {
                'sender': {'id': 'superuser', 'role': 'support'},
                'text': 'Промокод  на 24 часа',
                'metadata': {
                    'promocodes': [{'code': 'new_driver_promocode_id'}],
                },
            },
            200,
            {
                'action_id': 'test_uid',
                'action': 'close',
                'in_addition': False,
                'comment': 'Промокод  на 24 часа',
                'succeed_operations': ['promocode'],
                'promocodes': [{'code': 'new_driver_promocode_id'}],
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
            },
        ),
        (
            '5cb080c7779fb32f801581b8',
            {
                'comment': (
                    'Промокод {{driver_promo:loyalty_3:причина_выдачи}}'
                    ' на {{duration}} часа'
                ),
                'request_id': 'some_request_id_123',
            },
            False,
            '/driver-promocodes/internal/v1/promocodes',
            {
                'entity_type': 'park_driver_profile_id',
                'entity_id': 'some_park_driver_profile_id',
                'series_name': '3_rus_loyal',
                'tickets': ['5cb080c7779fb32f801581b8'],
                'description': 'причина выдачи',
            },
            {
                'sender': {'id': 'superuser', 'role': 'support'},
                'text': 'Промокод  на 3 часа',
                'metadata': {
                    'promocodes': [{'code': 'new_driver_promocode_id'}],
                },
            },
            200,
            {
                'action_id': 'test_uid',
                'action': 'close',
                'in_addition': False,
                'comment': 'Промокод  на 3 часа',
                'succeed_operations': ['promocode'],
                'promocodes': [{'code': 'new_driver_promocode_id'}],
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
            },
        ),
        (
            '5cb080c7779fb32f801581b8',
            {
                'comment': (
                    'Промокод {{driver_promo:24:причинавыдачи}} на '
                    '{{duration}} часа'
                ),
                'request_id': 'some_request_id_123',
            },
            False,
            '/driver-promocodes/internal/v1/promocodes',
            {
                'entity_type': 'park_driver_profile_id',
                'entity_id': 'some_park_driver_profile_id',
                'series_name': '24h',
                'tickets': ['5cb080c7779fb32f801581b8'],
                'description': 'причинавыдачи',
            },
            {
                'sender': {'id': 'superuser', 'role': 'support'},
                'text': 'Промокод  на 24 часа',
                'metadata': {
                    'promocodes': [{'code': 'new_driver_promocode_id'}],
                },
            },
            200,
            {
                'action_id': 'test_uid',
                'action': 'close',
                'in_addition': False,
                'comment': 'Промокод  на 24 часа',
                'succeed_operations': ['promocode'],
                'promocodes': [{'code': 'new_driver_promocode_id'}],
                'login': 'superuser',
                'created': datetime.datetime(2018, 6, 15, 12, 34),
                'line': 'first',
            },
        ),
        (
            '5cb080c7779fb32f801581b7',
            {
                'comment': (
                    'Промокод {{driver_promo:24:причинавыдачи}} на '
                    '{{duration}} часа'
                ),
            },
            False,
            None,
            {},
            {},
            424,
            None,
        ),
    ],
)
@pytest.mark.filldb(support_chatterbox='driver_promocode')
async def test_close_driver_promocode(
        cbox,
        task_id,
        data,
        legacy_mode,
        expected_admin_url,
        expected_admin_request,
        support_chat_message,
        expected_code,
        expected_history,
        response_mock,
        patch_aiohttp_session,
        mockserver,
        mock_random_str_uuid,
):
    mock_random_str_uuid()

    @patch_aiohttp_session(cbox.settings.TARIFF_EDITOR_URL, 'POST')
    def patch_admin_request(method, url, **kwargs):
        assert method == 'post'
        assert url == expected_admin_url
        assert kwargs['json'] == expected_admin_request
        return response_mock(json={'id': 'promocode_id', 'code': '12345'})

    @patch_aiohttp_session(discovery.find_service('support_chat').url, 'POST')
    def patch_support_chat_request(method, url, **kwargs):
        assert method == 'post'
        if 'add_update' in url:
            assert kwargs['json']['message'] == support_chat_message
            return response_mock(json={})
        return response_mock(json={'messages': []})

    @mockserver.json_handler('/driver-promocodes/internal/v1/promocodes')
    def mock_driver_promocodes(request):
        assert request.method == 'POST'
        assert request.url.endswith(expected_admin_url)
        assert request.json == expected_admin_request
        return {'id': 'new_driver_promocode_id'}

    cbox.app.config.DRIVER_SUPPORT_USE_LEGACY_PROMOCODES = legacy_mode

    await cbox.post(
        '/v1/tasks/%s/close' % task_id,
        data=data,
        headers={'Cookie': 'Test=test;'},
    )
    assert cbox.status == expected_code
    if expected_admin_url is not None:
        assert mock_driver_promocodes.has_calls != legacy_mode

    if expected_history is not None:
        task = await cbox.app.db.support_chatterbox.find_one(
            {'_id': bson.ObjectId(task_id)},
        )
        assert task['history'][-1] == expected_history


@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'driver_phone': 'phones',
            'park_phone': 'phones',
        },
    },
)
async def test_close_with_meta(
        cbox, monkeypatch, mock, mock_chat_get_history, mock_personal,
):
    mock_chat_get_history({'messages': []})

    @mock
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    cbox.set_user('some_user')
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a4/close',
        data={'comment': '{{meta:driver_phone}}, {{meta:park_phone}}'},
    )
    assert cbox.status == http.HTTPStatus.OK

    add_update_call = _dummy_add_update.calls[0]
    assert add_update_call['kwargs']['message_text'] == '+7123, +7456'


@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'driver_phone': 'phones',
            'park_phone': 'phones',
        },
    },
)
async def test_close_with_subscription_cancel(
        cbox,
        monkeypatch,
        mock,
        mock_chat_get_history,
        mock_personal,
        mockserver,
):
    mock_chat_get_history({'messages': []})

    @mockserver.json_handler('/music/stop-active-interval/')
    def _dummy_subscription_cancel(request):
        return {}

    @mock
    async def _dummy_add_update(*args, **kwargs):
        return 'dummy result'

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', _dummy_add_update,
    )

    cbox.set_user('some_user')
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a4/close',
        data={'comment': 'cancel{{media_subscription_cancel:123}}'},
    )
    assert cbox.status == http.HTTPStatus.OK

    add_update_call = _dummy_add_update.calls[0]
    assert add_update_call['kwargs']['message_text'] == 'cancel'


async def test_close_bad_macro(cbox):
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a4/close',
        data={'comment': 'bad comment {{'},
    )
    assert cbox.status == http.HTTPStatus.FAILED_DEPENDENCY


@pytest.mark.parametrize('handler', ['dismiss', 'dismiss_with_tvm'])
@pytest.mark.parametrize(
    'task_id_str, expected_update_kwargs, expected_transition_kwargs',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'message_text': None,
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': False,
                    'retry_csat_request': False,
                },
            },
            None,
        ),
        (
            '5c2cae5cb2682a976914c2a1',
            {
                'message_text': None,
                'message_sender_role': 'support',
                'message_sender_id': 'superuser',
                'message_metadata': None,
                'message_id': None,
                'update_metadata': {
                    'ticket_status': 'solved',
                    'ask_csat': False,
                    'retry_csat_request': False,
                },
                'user_guid': '10000000-0000-0000-0000-000000000001',
            },
            None,
        ),
        (
            '5b2cae5cb2682a976914c2b0',
            None,
            {'data': {'resolution': 'fixed'}, 'transition': 'close'},
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(CHATTERBOX_HISTORY_TAGS_ADDED=True)
@pytest.mark.pgsql('chatterbox', files=['test_dismiss_pg.sql'])
async def test_dismiss(
        cbox,
        handler,
        mock_chat_add_update,
        mock_st_transition,
        mock_random_str_uuid,
        task_id_str,
        expected_update_kwargs,
        expected_transition_kwargs,
):
    mock_random_str_uuid()
    await cbox.post(
        '/v1/tasks/{}/{}'.format(task_id_str, handler),
        data={
            'tags': ['double tag', 'double tag'],
            'themes': ['1', '2'],
            'hidden_comment': 'text',
            'hidden_comment_metadata': {'encrypt_key': '123'},
        },
        params={
            'chatterbox_button': 'chatterbox_nto',
            'additional_tag': 'nto_tag',
        },
    )
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id_str)},
    )
    assert task['status'] == 'closed'
    expected_history = [
        {
            'action_id': 'test_uid',
            'action': 'dismiss',
            'created': NOW,
            'login': 'superuser',
            'line': 'first',
            'in_addition': False,
            'hidden_comment': 'text',
            'meta_changes': [
                {
                    'change_type': 'set',
                    'field_name': 'chatterbox_button',
                    'value': 'chatterbox_nto',
                },
                {
                    'change_type': 'set',
                    'field_name': 'themes',
                    'value': [1, 2],
                },
            ],
            'query_params': {
                'chatterbox_button': 'chatterbox_nto',
                'additional_tag': 'nto_tag',
            },
        },
    ]
    expected_tags = ['3', '4', 'double tag', 'nto_tag', 'tag1', 'tag2']
    if handler == 'dismiss':
        expected_tags.extend(['доп', 'доп_superuser_20180615'])
        expected_history[0]['in_addition'] = True
        expected_history[0]['tags_changes'] = [
            {'change_type': 'add', 'tag': '3'},
            {'change_type': 'add', 'tag': '4'},
            {'change_type': 'add', 'tag': 'double tag'},
            {'change_type': 'add', 'tag': 'nto_tag'},
            {'change_type': 'add', 'tag': 'доп'},
            {'change_type': 'add', 'tag': 'доп_superuser_20180615'},
        ]
        expected_history[0]['tags_added'] = [
            '3',
            '4',
            'double tag',
            'nto_tag',
            'доп',
            'доп_superuser_20180615',
        ]
    else:
        expected_history[0]['tags_changes'] = [
            {'change_type': 'add', 'tag': '3'},
            {'change_type': 'add', 'tag': '4'},
            {'change_type': 'add', 'tag': 'double tag'},
            {'change_type': 'add', 'tag': 'nto_tag'},
        ]
        expected_history[0]['tags_added'] = ['3', '4', 'double tag', 'nto_tag']
    assert task['history'] == expected_history
    assert task['tags'] == expected_tags
    assert task['meta_info']['chatterbox_button'] == 'chatterbox_nto'

    if expected_update_kwargs is not None:
        add_update_call = mock_chat_add_update.calls[0]
        assert add_update_call['args'] == (task['external_id'],)
        add_update_call['kwargs'].pop('log_extra')
        assert add_update_call['kwargs'] == expected_update_kwargs

    if expected_transition_kwargs is not None:
        execute_transition_call = mock_st_transition.calls[0]
        assert execute_transition_call['ticket'] == task['external_id']
        assert execute_transition_call['kwargs'] == expected_transition_kwargs

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT COUNT(*)'
            'FROM chatterbox.supporter_tasks '
            'WHERE task_id = $1',
            task_id_str,
        )
        assert len(result) == 1
        assert result[0]['count'] == 0


@pytest.mark.parametrize(
    'task_id, expected_body_data',
    [
        (
            '5b2cae5db2682a976914c2a2',
            [
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:56+0000',
                    'comment': 'test comment',
                },
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:57+0000',
                    'comment': 'another comment',
                    'encrypt_key': '123',
                },
            ],
        ),
        (
            '7b2cae5db2682a976914c2a2',
            [
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:56+0000',
                    'comment': 'test comment',
                },
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:57+0000',
                    'comment': 'another comment',
                },
                {
                    'login': 'client',
                    'created': '2018-05-05T15:34:56+0000',
                    'comment': 'startrack comment',
                },
            ],
        ),
    ],
)
async def test_show_hidden_comments(
        cbox,
        patch,
        expected_body_data,
        patch_aiohttp_session,
        task_id,
        mock_st_get_messages,
):
    mock_st_get_messages(
        {
            'messages': [],
            'hidden_comments': [
                {
                    'login': 'client',
                    'comment': 'startrack comment',
                    'created': dates.parse_timestring(
                        '2018-05-05T15:34:56+0000',
                    ),
                },
            ],
        },
    )

    @patch(
        'chatterbox.internal.task_source._support_chat.'
        'SupportChat.get_messages',
    )
    async def _supchat_get_messages(*args, **kwargs):
        return {'hidden_comments': []}

    await cbox.post(
        '/v1/tasks/{0}/show_hidden_comments'.format(task_id), data={},
    )
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == expected_body_data


async def test_csrf_token(cbox, monkeypatch, patch):
    @patch(
        'chatterbox.internal.task_source._support_chat.'
        'SupportChat.get_messages',
    )
    async def _get_messages(*args, **kwargs):
        return {'hidden_comments': []}

    monkeypatch.setattr(cbox.app.settings, 'CSRF_VALIDATION', True)
    cbox.set_user('some_user')
    csrf_token = await cbox.get_csrf_token()
    await cbox.post(
        '/v1/tasks/5b2cae5db2682a976914c2a2/show_hidden_comments',
        data={},
        headers={'X-Csrf-Token': csrf_token},
    )
    assert cbox.status == http.HTTPStatus.OK


async def test_no_csrf_token(cbox, monkeypatch):
    monkeypatch.setattr(cbox.app.settings, 'CSRF_VALIDATION', True)
    await cbox.post(
        '/v1/tasks/5b2cae5db2682a976914c2a2/show_hidden_comments', data={},
    )
    assert cbox.status == http.HTTPStatus.FORBIDDEN


@pytest.mark.parametrize(
    ('task_id', 'data', 'meta_info', 'tags', 'history'),
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {},
            {'city': 'Moscow', 'queue': 'some_queue'},
            ['tag1', 'tag2'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'update_tags': [{'change_type': 'add', 'tag': 'tag3'}]},
            {'city': 'Moscow', 'queue': 'some_queue'},
            ['tag1', 'tag2', 'tag3'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'tags_changes': [{'change_type': 'add', 'tag': 'tag3'}],
                    'tags_added': ['tag3'],
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'update_tags': [{'change_type': 'delete', 'tag': 'tag2'}]},
            {'city': 'Moscow', 'queue': 'some_queue'},
            ['tag1'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                },
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'line': 'first',
                    'login': 'superuser',
                    'tags_changes': [{'change_type': 'delete', 'tag': 'tag2'}],
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'order_id',
                        'value': 'some_order_id',
                    },
                    {'change_type': 'delete', 'field_name': 'city'},
                    {
                        'change_type': 'delete',
                        'field_name': 'test nonexistent field',
                    },
                ],
                'update_tags': [
                    {'change_type': 'add', 'tag': 'new tag'},
                    {'change_type': 'add', 'tag': 'new tag'},
                    {'change_type': 'delete', 'tag': 'tag1'},
                    {'change_type': 'delete', 'tag': 'test nonexistent tag'},
                ],
            },
            {'order_id': 'some_order_id', 'queue': 'some_queue'},
            ['tag2', 'new tag'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'order_id',
                            'value': 'some_order_id',
                        },
                        {'change_type': 'delete', 'field_name': 'city'},
                    ],
                    'tags_changes': [{'change_type': 'add', 'tag': 'new tag'}],
                    'tags_added': ['new tag'],
                },
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'line': 'first',
                    'login': 'superuser',
                    'tags_changes': [
                        {'change_type': 'delete', 'tag': 'tag1'},
                        {
                            'change_type': 'delete',
                            'tag': 'test nonexistent tag',
                        },
                    ],
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'update_tags': [{'change_type': 'add', 'tag': 'клиент_urgent'}]},
            {'city': 'Moscow', 'queue': 'some_queue'},
            ['tag1', 'tag2', 'клиент_urgent'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'клиент_urgent'},
                    ],
                    'tags_added': ['клиент_urgent'],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'new_line': 'urgent',
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'ticket_subject',
                        'value': 'Забыл вещи в машине',
                    },
                ],
            },
            {
                'ticket_subject': 'Забыл вещи в машине',
                'city': 'Moscow',
                'queue': 'some_queue',
            },
            ['tag1', 'tag2'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'ticket_subject',
                            'value': 'Забыл вещи в машине',
                        },
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'new_line': 'urgent',
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'просто пользователь',
                    },
                ],
            },
            {
                'city': 'Moscow',
                'user_type': 'просто пользователь',
                'queue': 'some_queue',
            },
            ['tag1', 'tag2'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_type',
                            'value': 'просто пользователь',
                        },
                    ],
                },
            ],
        ),
        (
            '5c2cae5cb2682a976914c2a1',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'просто пользователь',
                    },
                ],
            },
            {
                'city': 'Moscow',
                'user_type': 'просто пользователь',
                'queue': 'some_queue',
                'user_guid': '10000000-0000-0000-0000-000000000001',
            },
            ['tag1', 'tag2'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_type',
                            'value': 'просто пользователь',
                        },
                    ],
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'vip-пользователь',
                    },
                ],
            },
            {
                'city': 'Moscow',
                'user_type': 'vip-пользователь',
                'queue': 'some_queue',
            },
            ['tag1', 'tag2'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_type',
                            'value': 'vip-пользователь',
                        },
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'new_line': 'vip',
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a8',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'vip-пользователь',
                    },
                ],
            },
            {
                'city': 'Moscow',
                'user_type': 'vip-пользователь',
                'queue': 'some_queue',
            },
            ['tag1', 'tag2'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_type',
                            'value': 'vip-пользователь',
                        },
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'new_line': 'vip',
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a9',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'vip-пользователь',
                    },
                ],
            },
            {
                'city': 'Moscow',
                'user_type': 'vip-пользователь',
                'queue': 'some_queue',
            },
            ['tag1', 'tag2'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_type',
                            'value': 'vip-пользователь',
                        },
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'in_addition': False,
                    'line': 'first',
                    'login': 'superuser',
                    'new_line': 'vip',
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c2a9',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'city',
                        'value': 'Нижний Новгород',
                    },
                ],
            },
            {'city': 'нижний_новгород', 'queue': 'some_queue'},
            ['tag1', 'tag2'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'city',
                            'value': 'нижний_новгород',
                        },
                    ],
                },
            ],
        ),
        (
            '5b2cae5cb2682a976914c3a9',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_phone',
                        'value': '+79999999999',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'driver_license',
                        'value': 'some_driver_license',
                    },
                    {'change_type': 'delete', 'field_name': 'user_email'},
                ],
            },
            {
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'city': 'Moscow',
                'queue': 'some_queue',
            },
            ['tag1', 'tag2'],
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone',
                            'value': '+79999999999',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'driver_license',
                            'value': 'some_driver_license',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'user_phone_pd_id',
                            'value': 'phone_pd_id_1',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'driver_license_pd_id',
                            'value': 'driver_license_pd_id_1',
                        },
                        {'change_type': 'delete', 'field_name': 'user_email'},
                        {
                            'change_type': 'delete',
                            'field_name': 'user_email_pd_id',
                        },
                    ],
                },
            ],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_HISTORY_TAGS_ADDED=True,
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'user_email': 'emails',
            'driver_license': 'driver_licenses',
            'driver_phone': 'phones',
            'park_phone': 'phones',
            'park_email': 'emails',
        },
    },
)
async def test_update_meta(
        cbox: conftest.CboxWrap,
        task_id,
        data,
        meta_info,
        tags,
        history,
        mock_personal,
        mock_random_str_uuid,
):
    mock_random_str_uuid()
    await cbox.post('v1/tasks/%s/update_meta' % task_id, data=data)
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )
    assert task['meta_info'] == meta_info
    assert task['tags'] == tags
    assert task['history'] == history


@pytest.mark.config(
    CHATTERBOX_CHANGE_LINE_STATUSES={
        'new': 'new',
        'in_progress': 'forwarded',
        'reopened': 'reopened',
        'waiting': 'waiting',
        'deferred': 'deferred',
    },
)
@pytest.mark.parametrize(
    'task_id,data,expected_line,new_status,history,projects',
    [
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'update_meta': [],
                'update_tags': [
                    {'change_type': 'add', 'tag': 'клиент_urgent'},
                    {
                        'change_type': 'add',
                        'tag': 'Корпоративный_пользователь',
                    },
                ],
            },
            'urgent',
            'forwarded',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'tags_changes': [
                        {
                            'change_type': 'add',
                            'tag': 'корпоративный_пользователь',
                        },
                        {'change_type': 'add', 'tag': 'клиент_urgent'},
                    ],
                    'tags_added': [
                        'корпоративный_пользователь',
                        'клиент_urgent',
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'new_line': 'urgent',
                    'in_addition': False,
                },
            ],
            ['eats'],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'vip-пользователь',
                    },
                ],
                'update_tags': [
                    {
                        'change_type': 'add',
                        'tag': 'Корпоративный_пользователь',
                    },
                ],
            },
            'corp',
            'forwarded',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_type',
                            'value': 'vip-пользователь',
                        },
                    ],
                    'tags_changes': [
                        {
                            'change_type': 'add',
                            'tag': 'корпоративный_пользователь',
                        },
                    ],
                    'tags_added': ['корпоративный_пользователь'],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'new_line': 'corp',
                    'in_addition': False,
                },
            ],
            ['taxi', 'eats'],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'vip-пользователь',
                    },
                ],
            },
            'vip',
            'forwarded',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_type',
                            'value': 'vip-пользователь',
                        },
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'new_line': 'vip',
                    'in_addition': False,
                },
            ],
            ['taxi'],
        ),
        (
            '5c2cae5cb2682a976914c2a1',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'vip-пользователь',
                    },
                ],
            },
            'vip',
            'forwarded',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_type',
                            'value': 'vip-пользователь',
                        },
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'new_line': 'vip',
                    'in_addition': False,
                },
            ],
            ['taxi'],
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {
                'update_tags': [
                    {'change_type': 'add', 'tag': 'test1'},
                    {'change_type': 'add', 'tag': 'test2'},
                ],
            },
            'first',
            'in_progress',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'test1'},
                        {'change_type': 'add', 'tag': 'test2'},
                    ],
                    'tags_added': ['test1', 'test2'],
                },
            ],
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a7',
            {
                'update_meta': [],
                'update_tags': [
                    {'change_type': 'add', 'tag': 'клиент_urgent'},
                    {
                        'change_type': 'add',
                        'tag': 'Корпоративный_пользователь',
                    },
                ],
            },
            'urgent',
            'waiting',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'vip',
                    'tags_changes': [
                        {
                            'change_type': 'add',
                            'tag': 'корпоративный_пользователь',
                        },
                        {'change_type': 'add', 'tag': 'клиент_urgent'},
                    ],
                    'tags_added': [
                        'корпоративный_пользователь',
                        'клиент_urgent',
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'vip',
                    'new_line': 'urgent',
                    'in_addition': False,
                },
            ],
            ['eats'],
        ),
        (
            '5b2cae5cb2682a976914c2a5',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'user_type',
                        'value': 'vip-пользователь',
                    },
                ],
            },
            'urgent',
            'in_progress',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'urgent',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'user_type',
                            'value': 'vip-пользователь',
                        },
                    ],
                },
            ],
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a6',
            {
                'update_meta': [
                    {
                        'change_type': 'set',
                        'field_name': 'ticket_subject',
                        'value': 'Забыл вещи в машине',
                    },
                ],
            },
            'urgent',
            'deferred',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'corp',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'ticket_subject',
                            'value': 'Забыл вещи в машине',
                        },
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'corp',
                    'new_line': 'urgent',
                    'in_addition': False,
                },
            ],
            ['eats'],
        ),
        (
            '5b2cae5cb2682a976914c2a7',
            {
                'update_meta': [],
                'update_tags': [
                    {
                        'change_type': 'add',
                        'tag': 'Корпоративный_пользователь',
                    },
                ],
            },
            'corp',
            'waiting',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'vip',
                    'tags_changes': [
                        {
                            'change_type': 'add',
                            'tag': 'корпоративный_пользователь',
                        },
                    ],
                    'tags_added': ['корпоративный_пользователь'],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'vip',
                    'new_line': 'corp',
                    'in_addition': False,
                },
            ],
            ['taxi', 'eats'],
        ),
        (
            '5b2cae5cb2682a976914c2a5',
            {
                'update_meta': [],
                'update_tags': [
                    {
                        'change_type': 'add',
                        'tag': 'Корпоративный_пользователь',
                    },
                ],
            },
            'urgent',
            'in_progress',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'urgent',
                    'tags_changes': [
                        {
                            'change_type': 'add',
                            'tag': 'корпоративный_пользователь',
                        },
                    ],
                    'tags_added': ['корпоративный_пользователь'],
                },
            ],
            None,
        ),
        (
            '5b2cae5cb2682a976914c2a8',
            {
                'update_meta': [],
                'update_tags': [
                    {
                        'change_type': 'add',
                        'tag': 'Корпоративный_пользователь',
                    },
                ],
            },
            'corp',
            'new',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'tags_changes': [
                        {
                            'change_type': 'add',
                            'tag': 'корпоративный_пользователь',
                        },
                    ],
                    'tags_added': ['корпоративный_пользователь'],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'new_line': 'corp',
                    'in_addition': False,
                },
            ],
            ['taxi', 'eats'],
        ),
        (
            '5b2cae5cb2682a976914c2a9',
            {
                'update_meta': [],
                'update_tags': [
                    {
                        'change_type': 'add',
                        'tag': 'Корпоративный_пользователь',
                    },
                ],
            },
            'corp',
            'reopened',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'tags_changes': [
                        {
                            'change_type': 'add',
                            'tag': 'корпоративный_пользователь',
                        },
                    ],
                    'tags_added': ['корпоративный_пользователь'],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'new_line': 'corp',
                    'in_addition': False,
                },
            ],
            ['taxi', 'eats'],
        ),
        (
            '5b2cae5cb2682a976914c2b9',
            {
                'update_meta': [],
                'update_tags': [{'change_type': 'add', 'tag': 'sms'}],
            },
            'sms_first',
            'reopened',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'tags_changes': [{'change_type': 'add', 'tag': 'sms'}],
                    'tags_added': ['sms'],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'forward',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'new_line': 'sms_first',
                    'in_addition': False,
                },
            ],
            ['taxi'],
        ),
        (
            '5b2cae5cb2682a976914c2c9',
            {
                'update_meta': [],
                'update_tags': [{'change_type': 'add', 'tag': 'sms'}],
            },
            'first',
            'reopened',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'tags_changes': [{'change_type': 'add', 'tag': 'sms'}],
                    'tags_added': ['sms'],
                },
            ],
            None,
        ),
        (
            '5b2cae5cb2682a976914c296',
            {
                'update_meta': [],
                'update_tags': [{'change_type': 'add', 'tag': 'online'}],
            },
            'online_line',
            'accepted',
            [
                {
                    'action': 'update_meta',
                    'created': NOW,
                    'line': 'online_line',
                    'login': 'superuser',
                    'tags_added': ['online'],
                    'tags_changes': [{'change_type': 'add', 'tag': 'online'}],
                },
            ],
            None,
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'urgent': {
            'id': 'urgent',
            'name': 'Ургент',
            'priority': 1,
            'conditions': {
                '#or': [
                    {'tags': {'#in': ['клиент_urgent', 'подозрение_urgent']}},
                    {
                        'fields/ticket_subject': {
                            '#in': [
                                'Забыл вещи в машине',
                                'Яндекс.Такси Я забыл в такси свои вещи',
                            ],
                        },
                    },
                ],
            },
            'projects': ['eats'],
        },
        'corp': {
            'name': 'Корп',
            'priority': 2,
            'conditions': {
                'tags': {
                    '#in': ['корпоративный_пользователь', 'корп_пользователь'],
                },
            },
            'projects': ['taxi', 'eats'],
        },
        'vip': {
            'name': 'ВИП',
            'priority': 3,
            'conditions': {'fields/user_type': 'vip-пользователь'},
        },
        'first': {'name': 'Первая линия', 'priority': 4},
        'sms_first': {
            'name': 'Первая линия смс',
            'priority': 1,
            'conditions': {'type': {'#in': ['client', 'sms']}, 'tags': 'sms'},
        },
        'online_line': {'name': 'online', 'priority': 3, 'mode': 'online'},
    },
    CHATTERBOX_HISTORY_TAGS_ADDED=True,
)
async def test_update_meta_change_line(
        cbox,
        task_id,
        data,
        expected_line,
        new_status,
        history,
        projects,
        mock_random_str_uuid,
):
    mock_random_str_uuid()
    await cbox.post('v1/tasks/%s/update_meta' % task_id, data=data)
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )
    assert new_status == task['status']
    assert task['line'] == expected_line
    assert task['history'] == history
    if projects is not None:
        assert task['projects'] == projects


async def test_update_urgent_gone_export(cbox, monkeypatch):
    async def task_gone(*args, **kwargs):
        raise tasks_manager.WrongTask

    monkeypatch.setattr(cbox.app.tasks_manager, 'enqueue_export', task_gone)

    task_id = '5b2cae5cb2682a976914c2a1'
    data = {'update_tags': [{'change_type': 'add', 'tag': 'клиент_urgent'}]}

    await cbox.post('v1/tasks/%s/update_meta' % task_id, data=data)
    assert cbox.status == http.HTTPStatus.OK


@pytest.mark.parametrize(
    'handler, comment, params, messages, first_answer, full_resolve',
    [
        (
            'defer',
            None,
            {'reopen_at': '2018-06-15T15:34:00+0000'},
            [],
            None,
            None,
        ),
        (
            'defer',
            'some comment',
            {'reopen_at': '2018-06-15T15:34:00+0000'},
            [
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2018-06-10T12:34:56+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2018-06-11T12:34:56+0000'},
                },
            ],
            SECONDS_IN_DAY,
            SECONDS_IN_DAY,
        ),
        (
            'close',
            'some comment',
            {},
            [
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2018-06-10T12:34:56+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2018-06-11T12:34:56+0000'},
                },
            ],
            SECONDS_IN_DAY,
            SECONDS_IN_DAY,
        ),
        (
            'close',
            'some comment',
            {},
            [
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2018-06-11T12:34:56+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2018-06-10T12:34:56+0000'},
                },
            ],
            0,
            0,
        ),
        (
            'comment',
            'some comment',
            {},
            [
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2018-06-10T12:34:56.123456+0000'},
                },
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2018-06-11T12:34:56.234567+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2018-06-12T12:34:56.345678+0000'},
                },
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2018-06-13T12:34:56+0000'},
                },
                {
                    'sender': {'role': 'client'},
                    'metadata': {'created': '2018-06-14T12:34:56+0000'},
                },
                {
                    'sender': {'role': 'support'},
                    'metadata': {'created': '2018-06-15T12:34:56+0000'},
                },
            ],
            SECONDS_IN_DAY * 2,
            SECONDS_IN_DAY * 4,
        ),
    ],
)
async def test_answer_statistics(
        cbox,
        monkeypatch,
        handler,
        comment,
        params,
        messages,
        first_answer,
        full_resolve,
):
    async def get_history(*args, **kwargs):
        return {'messages': messages}

    async def add_update(*args, **kwargs):
        return 'dummy result'

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'get_history', get_history,
    )

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', add_update,
    )

    data = {}
    if comment:
        data['comment'] = comment

    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a1/{}'.format(handler),
        params=params,
        data=data,
    )
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId('5b2cae5cb2682a976914c2a1')},
    )
    assert task.get('first_answer') == first_answer
    assert task.get('full_resolve') == full_resolve


@pytest.mark.parametrize(
    'take_after_assign,expected_response',
    [
        (False, {}),
        (
            True,
            {
                'next_frontend_action': 'take',
                'new_user_status': 'before-break',
            },
        ),
    ],
)
@pytest.mark.parametrize(
    'task_id,query_params,expected_status,expected_tag,'
    'expected_meta_field,expected_meta_value,check_correct',
    [
        ('5b2cae5cb2682a976914c2a1', None, 200, None, None, None, True),
        (
            '5b2cae5cb2682a976914c2a1',
            {'additional_tag': 'some_tag'},
            200,
            'some_tag',
            None,
            None,
            True,
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            {'chatterbox_button': 'some_button'},
            200,
            None,
            'chatterbox_button',
            'some_button',
            True,
        ),
        ('5b2cae5db2682a976914c2a2', None, 410, None, None, None, False),
        ('5b2cae5cb2682a976914c2a3', None, 200, None, None, None, True),
        (
            '5b2cae5cb2682a976914c2a3',
            {'additional_tag': 'some_tag', 'chatterbox_button': 'some_button'},
            200,
            'some_tag',
            'chatterbox_button',
            'some_button',
            True,
        ),
        ('5b2cae5db2682a976914c2af', None, 404, None, None, None, False),
    ],
)
@pytest.mark.filldb(support_chatterbox='superuser')
async def test_assign(
        cbox,
        take_after_assign,
        expected_response,
        task_id,
        query_params,
        expected_status,
        expected_tag,
        expected_meta_field,
        expected_meta_value,
        check_correct,
):
    cbox.app.config.CHATTERBOX_TAKE_AFTER_ASSIGN = take_after_assign
    await cbox.post(
        '/v1/tasks/{}/assign'.format(task_id), params=query_params, data={},
    )

    assert cbox.status == expected_status
    if cbox.status == 200:
        assert cbox.body_data == expected_response
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId(task_id)},
        )
        if expected_tag is not None:
            assert expected_tag in task['tags']
        if expected_meta_field is not None:
            assert (
                task['meta_info'][expected_meta_field] == expected_meta_value
            )
        if check_correct:
            assert task['status'] == 'in_progress'
            assert task['support_admin'] == 'superuser'
            old_task = await cbox.db.support_chatterbox.find_one(
                {'_id': bson.objectid.ObjectId('5b2cae5cb2682a976914c2a4')},
            )
            assert old_task['status'] == 'in_progress'


@pytest.mark.translations(
    chatterbox={
        'errors.assign_forbidden': {
            'ru': 'Недостаточно прав для назанчения на себя',
        },
    },
)
@pytest.mark.parametrize(
    'task_id,user_login,user_groups,expected_status, expected_body',
    [
        ('5b2cae5cb2682a976914c2a1', 'restricted_user', [], 403, None),
        (
            '5b2cae5cb2682a976914c2a1',
            'test_user',
            ['chatterbox_basic'],
            403,
            {
                'code': 'forbidden',
                'status': 'error',
                'message': 'Недостаточно прав для назанчения на себя',
            },
        ),
    ],
)
@pytest.mark.filldb(support_chatterbox='superuser')
async def test_assign_permission_denied(
        cbox,
        patch_auth,
        task_id,
        user_login,
        user_groups,
        expected_status,
        expected_body,
):
    patch_auth(login=user_login, superuser=False, groups=user_groups)

    await cbox.post('/v1/tasks/{}/assign'.format(task_id), data={})
    assert cbox.status == expected_status
    if expected_body:
        assert cbox.body_data == expected_body


@pytest.mark.translations(
    chatterbox={
        'errors.compendium_assign_in_additional': {
            'ru': 'Compendium заблокировал assign в доп.',
        },
    },
)
async def test_assign_in_additional_not_permitted(
        cbox: conftest.CboxWrap, patch_auth,
):
    patch_auth(login='user_with_in_additional_not_permitted')

    await cbox.post(
        '/v1/tasks/{}/assign'.format('5b2cae5db2682a976914c2af'),
        data={},
        headers={'Accept-Language': 'ru'},
    )
    assert cbox.status == 403
    assert cbox.body_data == {
        'code': 'forbidden',
        'message': 'Compendium заблокировал assign в доп.',
        'status': 'error',
    }


@pytest.mark.translations(
    chatterbox={
        'errors.compendium_assign_off_shift': {
            'ru': 'Compendium заблокировал assign вне смены',
        },
    },
)
@pytest.mark.parametrize(
    'expected_status',
    (
        pytest.param(
            403, marks=[pytest.mark.now('2018-08-01T16:59:23.231000+00:00')],
        ),
        pytest.param(
            200, marks=[pytest.mark.now('2018-08-01T14:59:23.231000+00:00')],
        ),
    ),
)
async def test_assign_off_shift_tickets_disabled(
        cbox: conftest.CboxWrap, patch_auth, expected_status: int,
):
    patch_auth(login='user_with_off_shift_tickets_disabled')

    await cbox.post(
        '/v1/tasks/{}/assign'.format('5b2cae5cb2682a976914c2a1'),
        data={},
        headers={'Accept-Language': 'ru'},
    )
    assert cbox.status == expected_status
    if expected_status == 403:
        assert cbox.body_data == {
            'code': 'forbidden',
            'message': 'Compendium заблокировал assign вне смены',
            'status': 'error',
        }


@pytest.mark.parametrize(
    'task_id,expected_status',
    [
        ('5b2cae5cb2682a976914c2aa', 200),
        ('5b2cae5cb2682a976914c2ab', 410),
        ('5b2cae5cb2682a976914c2ac', 400),
        ('5b2cae5cb2682a976914c2ad', 404),
    ],
)
async def test_reopen(cbox, monkeypatch, task_id, expected_status):
    async def add_update(self, chat_id, *args, **kwargs):
        if str(chat_id) == '3':
            raise support_chat.ConflictError
        return {}

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', add_update,
    )

    await cbox.post('/v1/tasks/{}/reopen'.format(task_id), data={})
    assert cbox.status == expected_status


@pytest.mark.parametrize(
    'task_id,protected_statuses,expected_status',
    [
        ('5b2cae5cb2682a976914c2aa', [], 200),
        ('5b2cae5cb2682a976914c2ab', [], 410),
        ('5b2cae5cb2682a976914c2ac', [], 400),
        ('5b2cae5cb2682a976914c2ad', [], 404),
        ('5b2cae5cb2682a976914c220', ['in_progress'], 200),
    ],
)
async def test_reopen_with_tvm(
        cbox, monkeypatch, task_id, protected_statuses, expected_status,
):

    if expected_status == 200:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId(task_id)},
        )
        assert task is not None
        old_status = task['status']

    async def add_update(self, chat_id, *args, **kwargs):
        if str(chat_id) == '3':
            raise support_chat.ConflictError
        return {}

    monkeypatch.setattr(
        support_chat.SupportChatApiClient, 'add_update', add_update,
    )

    await cbox.post(
        '/v1/tasks/{}/reopen_with_tvm'.format(task_id),
        data={'protected_statuses': protected_statuses},
    )
    assert cbox.status == expected_status

    if expected_status == 200:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId(task_id)},
        )
        assert task['status'] == (
            old_status if protected_statuses else 'reopened'
        )


@pytest.mark.parametrize(
    'locale,params,data,expected_code,expected_ticket_id,expected_history,'
    'expected_create_ticket_kwargs, expected_search_kwargs',
    [
        (
            None,
            None,
            {'request_id': 'some_request_id'},
            200,
            'YANDEXTAXI-1',
            {
                'action_id': 'test_uid',
                'action': 'create_extra_ticket',
                'created': NOW,
                'login': 'superuser',
                'line': 'first',
                'in_addition': False,
                'extra_startrack_ticket': 'YANDEXTAXI-1',
            },
            {
                'queue': 'YANDEXTAXI',
                'summary': (
                    'Дополнительный тикет для таска '
                    '5b2cae5cb2682a976914c2a1 в Крутилке'
                ),
                'description': (
                    'Линк на таск: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2a1'
                ),
                'tags': None,
                'custom_fields': {'chatterboxId': '5b2cae5cb2682a976914c2a1'},
                'unique': 'some_request_id',
            },
            None,
        ),
        (
            'en',
            None,
            {'request_id': 'some_request_id'},
            200,
            'YANDEXTAXI-1',
            {
                'action_id': 'test_uid',
                'action': 'create_extra_ticket',
                'created': NOW,
                'login': 'superuser',
                'line': 'first',
                'in_addition': False,
                'extra_startrack_ticket': 'YANDEXTAXI-1',
            },
            {
                'queue': 'YANDEXTAXI',
                'summary': 'extra ticket for task ' '5b2cae5cb2682a976914c2a1',
                'description': (
                    'link: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2a1'
                ),
                'tags': None,
                'custom_fields': {'chatterboxId': '5b2cae5cb2682a976914c2a1'},
                'unique': 'some_request_id',
            },
            None,
        ),
        (
            'ru',
            {
                'additional_tag': 'some_additional_tag',
                'chatterbox_button': 'some_chatterbox_button',
                'queue': 'CHATTERBOX',
                'summary': 'some ticket summary',
                'email_from': 'some@email',
                'email_to': 'support@email',
            },
            {
                'request_id': 'some_request_id',
                'hidden_comment': 'some hidden comment',
                'tags': ['tag1', 'tag2', 'tag3'],
                'themes': ['1', '2', '3'],
            },
            200,
            'CHATTERBOX-1',
            {
                'action_id': 'test_uid',
                'action': 'create_extra_ticket',
                'created': NOW,
                'login': 'superuser',
                'line': 'first',
                'in_addition': True,
                'extra_startrack_ticket': 'CHATTERBOX-1',
                'hidden_comment': 'some hidden comment',
                'tags_changes': [
                    {'change_type': 'add', 'tag': '3'},
                    {'change_type': 'add', 'tag': '4'},
                    {'change_type': 'add', 'tag': 'some_additional_tag'},
                    {'change_type': 'add', 'tag': 'tag3'},
                    {'change_type': 'add', 'tag': 'доп'},
                    {'change_type': 'add', 'tag': 'доп_superuser_20180615'},
                ],
                'meta_changes': [
                    {
                        'change_type': 'set',
                        'field_name': 'chatterbox_button',
                        'value': 'some_chatterbox_button',
                    },
                    {
                        'change_type': 'set',
                        'field_name': 'themes',
                        'value': [1, 2, 3],
                    },
                ],
                'query_params': {
                    'additional_tag': 'some_additional_tag',
                    'chatterbox_button': 'some_chatterbox_button',
                    'queue': 'CHATTERBOX',
                    'summary': 'some ticket summary',
                    'email_from': 'some@email',
                    'email_to': 'support@email',
                },
            },
            {
                'queue': 'CHATTERBOX',
                'summary': 'some ticket summary',
                'description': (
                    'Линк на таск: '
                    'https://supchat.taxi.dev.yandex-team.ru/'
                    'chat/5b2cae5cb2682a976914c2a1'
                ),
                'tags': ['some_additional_tag'],
                'custom_fields': {
                    'chatterboxId': '5b2cae5cb2682a976914c2a1',
                    'emailFrom': 'some@email',
                    'emailTo': ['support@email'],
                    'emailCreatedBy': 'support@email',
                },
                'unique': 'some_request_id',
            },
            None,
        ),
        (
            'en',
            None,
            {'request_id': 'duplicated_request_id'},
            200,
            'YANDEXTAXI-0',
            None,
            None,
            {
                'json_filter': {
                    'queue': 'YANDEXTAXI',
                    'chatterboxId': '5b2cae5cb2682a976914c2a1',
                    'unique': 'duplicated_request_id',
                },
            },
        ),
        (
            'en',
            None,
            {'request_id': 'other_task_duplicated_request_id'},
            409,
            None,
            None,
            None,
            {
                'json_filter': {
                    'queue': 'YANDEXTAXI',
                    'chatterboxId': '5b2cae5cb2682a976914c2a1',
                    'unique': 'other_task_duplicated_request_id',
                },
            },
        ),
        (
            'en',
            {'queue': 'WRONGQUEUE'},
            {'request_id': 'some_request_id'},
            400,
            None,
            None,
            None,
            None,
        ),
        (
            None,
            {'email_from': 'some@email'},
            {'request_id': 'some_request_id'},
            400,
            None,
            None,
            None,
            None,
        ),
        (
            None,
            {'email_to': 'some@email'},
            {'request_id': 'some_request_id'},
            400,
            None,
            None,
            None,
            None,
        ),
    ],
)
@pytest.mark.translations(
    chatterbox={
        'extra_ticket.summary': {'en': 'extra ticket for task {task_id}'},
        'extra_ticket.description': {
            'en': 'link: {supchat_url}/chat/{task_id}',
        },
    },
)
@pytest.mark.config(
    STARTRACK_EXTRA_TICKET_ALLOWED_QUEUES=['YANDEXTAXI', 'CHATTERBOX'],
)
@pytest.mark.now(NOW.isoformat())
async def test_extra_ticket(
        cbox,
        mock_st_create_ticket,
        mock_st_search,
        mock_random_str_uuid,
        locale,
        params,
        data,
        expected_code,
        expected_ticket_id,
        expected_history,
        expected_create_ticket_kwargs,
        expected_search_kwargs,
        pgsql,
):
    mock_random_str_uuid()
    if expected_history:
        in_addition = expected_history['in_addition']
        cursor = pgsql['chatterbox'].cursor()
        cursor.execute(
            'UPDATE chatterbox.online_supporters os '
            'SET in_additional = %s '
            'WHERE os.supporter_login = %s',
            (in_addition, 'superuser'),
        )

    if locale is None:
        headers = None
    else:
        headers = {'Accept-Language': locale}
    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a1/create_extra_ticket',
        params=params,
        data=data,
        headers=headers,
    )
    assert cbox.status == expected_code
    if expected_code != http.HTTPStatus.OK:
        return

    assert cbox.body_data == {
        'next_frontend_action': 'open_url',
        'url': 'https://tracker.yandex.ru/{}'.format(expected_ticket_id),
    }

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId('5b2cae5cb2682a976914c2a1')},
    )
    assert task['extra_startrack_tickets'] == [expected_ticket_id]

    if expected_history is not None:
        assert task['history'] == [expected_history]

    if expected_create_ticket_kwargs is not None:
        create_ticket_call = mock_st_create_ticket.calls[0]
        assert create_ticket_call['kwargs'] == expected_create_ticket_kwargs

    if expected_search_kwargs is not None:
        search_call = mock_st_search.calls[0]
        assert search_call['kwargs'] == expected_search_kwargs


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'macro_id,ml_result,task_id',
    [
        ('1', True, '5b2cae5cb2682a976914c220'),
        ('10', False, '5b2cae5cb2682a976914c220'),
        ('1', False, '5b2cae5cb2682a976914c229'),
        ('10', False, '5b2cae5cb2682a976914c229'),
    ],
)
async def test_suggestions(
        cbox,
        macro_id,
        task_id,
        ml_result,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_create_comment,
):
    mock_chat_get_history({'messages': []})
    ml_suggest = [1, 2, 3]
    if task_id == '5b2cae5cb2682a976914c229':
        ml_suggest = '1,2,3'
    task_id = bson.objectid.ObjectId(task_id)
    mock_st_get_comments([])
    await cbox.post(
        '/v1/tasks/{}/comment'.format(task_id),
        data={'comment': 'some test comment', 'macro_id': macro_id},
    )
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert task['meta_info'] == {
        'city': 'Moscow',
        'macro_id': macro_id,
        'currently_used_macro_ids': [macro_id],
        'ml_suggestion_success': ml_result,
        'ml_suggestions': ml_suggest,
        'queue': 'some_queue',
    }


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'request_comment, expected_comment, succeed_operations, new_sum',
    [
        (
            'refund {{refund:100:REASON}} {{refund_currency}}',
            'refund 100 ₽',
            ['refund'],
            100,
        ),
        ('refund {{refund:100:REASON}} ', 'refund 100 ', ['refund'], 100),
        (
            'refund {{refund:100.5:REASON}} ',
            'refund 100.5 ',
            ['refund'],
            100.5,
        ),
        (
            'refund {{refund:100,5:REASON}} ',
            'refund 100.5 ',
            ['refund'],
            100.5,
        ),
        (
            'refund {{refund_hide:100:REASON}} {{refund_currency}}',
            'refund  ',
            ['refund'],
            100,
        ),
        ('refund {{refund_hide:100:REASON}} ', 'refund  ', ['refund'], 100),
        (
            'refund {{refund_hide:100.5:REASON}} ',
            'refund  ',
            ['refund'],
            100.5,
        ),
        (
            'refund {{refund_hide:100,5:REASON}} ',
            'refund  ',
            ['refund'],
            100.5,
        ),
        (
            'compensation {{park_compensation:100}} '
            '{{park_compensation_currency}}',
            'compensation 100 ₽',
            ['compensation'],
            100,
        ),
        (
            'compensation {{park_compensation:100:cashrunner}} '
            '{{park_compensation_currency}}',
            'compensation 100 ₽',
            ['compensation'],
            100,
        ),
        (
            'compensation {{park_compensation:100:dryclean}} ',
            'compensation 100 ',
            ['compensation'],
            100,
        ),
        (
            'compensation {{park_compensation:100.5}} '
            '{{park_compensation_currency}}',
            'compensation 100.5 ₽',
            ['compensation'],
            100.5,
        ),
        (
            'compensation {{park_compensation:100,5}} '
            '{{park_compensation_currency}}',
            'compensation 100.5 ₽',
            ['compensation'],
            100.5,
        ),
        (
            'compensation {{park_compensation_hide:100}} '
            '{{park_compensation_currency}}',
            'compensation  ',
            ['compensation'],
            100,
        ),
        (
            'compensation {{park_compensation_hide:100:cashrunner}} '
            '{{park_compensation_currency}}',
            'compensation  ',
            ['compensation'],
            100,
        ),
        (
            'compensation {{park_compensation_hide:100:dryclean}} ',
            'compensation  ',
            ['compensation'],
            100,
        ),
        (
            'compensation {{park_compensation_hide:100.5}} '
            '{{park_compensation_currency}}',
            'compensation  ',
            ['compensation'],
            100.5,
        ),
        (
            'compensation {{park_compensation_hide:100,5}} '
            '{{park_compensation_currency}}',
            'compensation  ',
            ['compensation'],
            100.5,
        ),
        (
            'refund {{refund:100:REASON}} {{refund_currency}} '
            'compensation {{park_compensation:100:dryclean}}',
            'refund 100 ₽ compensation 100',
            ['compensation', 'refund'],
            100,
        ),
        (
            'refund {{refund_hide:100:REASON}} {{refund_currency}} '
            'compensation {{park_compensation_hide:100:cashrunner}}',
            'refund   compensation ',
            ['compensation', 'refund'],
            100,
        ),
    ],
)
async def test_refunds_and_compensations(
        cbox,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_create_comment,
        patch_aiohttp_session,
        response_mock,
        request_comment,
        expected_comment,
        succeed_operations,
        new_sum,
):
    # pylint: disable=unused-variable

    mock_chat_get_history({'messages': []})
    task_id = bson.objectid.ObjectId('5b2cae5cb2682a976914c221')
    mock_st_get_comments([])
    support_info_url = discovery.find_service('support_info').url

    str_cookie = 'Session_id=user_sid; sessionid2=user_sid2'

    @patch_aiohttp_session(
        support_info_url + '/v1/payments/update_order_ride_sum', 'POST',
    )
    def process_refund(*args, **kwargs):
        assert kwargs['headers']['Cookie'] == str_cookie
        assert kwargs['json'] == {
            'new_sum': new_sum,
            'order_id': 'order_id',
            'ticket': '5b2cae5cb2682a976914c221',
            'ticket_type': 'chatterbox',
            'reason_code': 'REASON',
            'real_ip': '127.0.0.1',
            'x_forwarded_for': 'test',
        }
        return response_mock(json={'currency': 'RUB', 'new_sum': new_sum})

    @patch_aiohttp_session(
        support_info_url + '/v1/payments/process_compensation', 'POST',
    )
    def process_compensation(*args, **kwargs):
        assert kwargs['headers']['Cookie'] == str_cookie
        expected_json = {
            'compensation_sum': new_sum,
            'order_id': 'order_id',
            'ticket': '5b2cae5cb2682a976914c221',
            'ticket_type': 'chatterbox',
            'real_ip': '127.0.0.1',
            'x_forwarded_for': 'test',
        }
        if 'reason' in kwargs['json']:
            assert kwargs['json']['reason'] in ('cashrunner', 'dryclean')
            kwargs['json'].pop('reason')

        assert kwargs['json'] == expected_json
        return response_mock(
            json={'currency': 'RUB', 'compensation_sum': new_sum},
        )

    await cbox.post(
        '/v1/tasks/{}/comment'.format(task_id),
        data={'comment': request_comment},
        headers={
            'Cookie': str_cookie,
            'X-Real-Ip': '127.0.0.1',
            'X-Forwarded-For': 'test',
        },
    )
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert task['history'][0]['comment'] == expected_comment
    assert task['history'][0]['succeed_operations'] == succeed_operations


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    'request_comment, refund_status, compensation_status, expected_response',
    [
        (
            'refund {{refund:100:REASON}}',
            400,
            200,
            {
                'message': 'Operations log:\n' 'Refund processing error',
                'status': 'comment processing error',
            },
        ),
        (
            'compensation {{park_compensation:100:dryclean}} '
            '{{park_compensation_currency}}',
            200,
            400,
            {
                'message': 'Operations log:\n' 'Compensation processing error',
                'status': 'comment processing error',
            },
        ),
        (
            'refund {{refund:100:REASON}} '
            'compensation {{park_compensation:100:dryclean}} ',
            200,
            400,
            {
                'message': (
                    'Operations log:\n'
                    'Refund processed\n'
                    'Compensation processing error'
                ),
                'status': 'comment processing error',
            },
        ),
        (
            'refund {{refund:100:REASON}} '
            'compensation {{park_compensation:100:dryclean}} ',
            400,
            400,
            {
                'message': 'Operations log:\n' 'Refund processing error',
                'status': 'comment processing error',
            },
        ),
        (
            'refund {{refund:100:REASON}} '
            'compensation {{park_compensation:100:dryclean}} }}',
            200,
            200,
            {
                'message': (
                    'Operations log:\n'
                    'Refund processed\n'
                    'Compensation processed\n'
                    'Cant apply macro: unknown templates'
                ),
                'status': 'comment processing error',
            },
        ),
    ],
)
# pylint: disable=invalid-name
async def test_refunds_and_compensations_error(
        cbox,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_create_comment,
        mock_random_str_uuid,
        patch_aiohttp_session,
        response_mock,
        request_comment,
        refund_status,
        compensation_status,
        expected_response,
):
    # pylint: disable=unused-variable
    mock_chat_get_history({'messages': []})
    task_id = bson.objectid.ObjectId('5b2cae5cb2682a976914c221')
    mock_st_get_comments([])
    support_info_url = discovery.find_service('support_info').url
    mock_random_str_uuid()

    @patch_aiohttp_session(
        support_info_url + '/v1/payments/update_order_ride_sum', 'POST',
    )
    def process_refund(*args, **kwargs):
        if refund_status == 200:
            return response_mock(json={'currency': 'RUB', 'new_sum': 100.0})
        return response_mock(
            json={'status': 'request_error', 'message': 'Admin request error'},
            status=refund_status,
        )

    @patch_aiohttp_session(
        support_info_url + '/v1/payments/process_compensation', 'POST',
    )
    def process_compensation(*args, **kwargs):
        if refund_status == compensation_status:
            return response_mock(
                json={'currency': 'rus', 'compensation_sum': 100.0},
            )
        return response_mock(
            json={'status': 'request_error', 'message': 'Admin request error'},
            status=compensation_status,
        )

    await cbox.post(
        '/v1/tasks/{}/comment'.format(task_id),
        data={'comment': request_comment},
    )
    assert cbox.status == http.HTTPStatus.FAILED_DEPENDENCY
    assert cbox.body_data == expected_response

    task = await cbox.db.support_chatterbox.find_one({'_id': task_id})
    assert task['history'][0] == {
        'action_id': 'test_uid',
        'action': 'macro_processing_fail',
        'created': NOW,
        'hidden_comment': expected_response['message'],
        'in_addition': False,
        'line': 'first',
        'login': 'superuser',
    }


@pytest.mark.parametrize(
    (
        'profile',
        'summary_tanker_key',
        'description_tanker_key',
        'queue',
        'additional_tag',
        'expected_status',
        'expected_response',
        'expected_history',
    ),
    [
        (
            'yandex-team',
            'some_summary_key',
            'some_description_key',
            'TAXIBUGPOLICE',
            'не_в_крутилку',
            200,
            {
                'next_frontend_action': 'open_url',
                'url': (
                    'https://st.yandex-team.ru/createTicket?'
                    'summary=some%20summary%20at%202018-05-07&'
                    'description=some%20description%20'
                    'of%205b2cae5cb2682a976914c2a1%20Moscow&queue='
                    'TAXIBUGPOLICE&tags=%D0%BD%D0%B5_%D0%B2_'
                    '%D0%BA%D1%80%D1%83%D1%82%D0%B8%D0%BB%D0%BA%D1%83'
                ),
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'generate_extra_ticket_link',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'in_addition': False,
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'не_в_крутилку'},
                    ],
                    'url': (
                        'https://st.yandex-team.ru/createTicket?'
                        'summary=some%20summary%20at%202018-05-07&'
                        'description=some%20description%20'
                        'of%205b2cae5cb2682a976914c2a1%20Moscow&queue='
                        'TAXIBUGPOLICE&tags=%D0%BD%D0%B5_%D0%B2_'
                        '%D0%BA%D1%80%D1%83%D1%82%D0%B8%D0%BB%D0%BA%D1%83'
                    ),
                    'query_params': {
                        'profile': 'yandex-team',
                        'queue': 'TAXIBUGPOLICE',
                        'summary_tanker_key': 'some_summary_key',
                        'description_tanker_key': 'some_description_key',
                        'additional_tag': 'не_в_крутилку',
                    },
                },
            ],
        ),
        (
            'yandex-team',
            'some_summary_key',
            'some_description_key',
            'TAXIBUGPOLICE',
            None,
            200,
            {
                'next_frontend_action': 'open_url',
                'url': (
                    'https://st.yandex-team.ru/createTicket?'
                    'summary=some%20summary%20at%202018-05-07&'
                    'description=some%20description%20'
                    'of%205b2cae5cb2682a976914c2a1%20Moscow&queue='
                    'TAXIBUGPOLICE'
                ),
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'generate_extra_ticket_link',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'in_addition': False,
                    'url': (
                        'https://st.yandex-team.ru/createTicket?'
                        'summary=some%20summary%20at%202018-05-07&'
                        'description=some%20description%20'
                        'of%205b2cae5cb2682a976914c2a1%20Moscow&queue='
                        'TAXIBUGPOLICE'
                    ),
                    'query_params': {
                        'profile': 'yandex-team',
                        'queue': 'TAXIBUGPOLICE',
                        'summary_tanker_key': 'some_summary_key',
                        'description_tanker_key': 'some_description_key',
                    },
                },
            ],
        ),
        (
            'yandex-team',
            'bad_summary_key',
            'some_description_key',
            'TAXIBUGPOLICE',
            None,
            400,
            {
                'message': 'Bad tanker key: bad_summary_key',
                'status': 'bad_tanker_key',
            },
            None,
        ),
        (
            'yandex-team',
            'some_summary_key',
            'bad_description_key',
            'TAXIBUGPOLICE',
            None,
            400,
            {
                'message': 'Bad tanker key: bad_description_key',
                'status': 'bad_tanker_key',
            },
            None,
        ),
        (
            'yandex-team',
            'some_summary_key',
            'extra_data_description_key',
            'TAXIBUGPOLICE',
            'english_text_*+&%@',
            200,
            {
                'next_frontend_action': 'open_url',
                'url': (
                    'https://st.yandex-team.ru/createTicket?'
                    'summary=some%20summary%20at%202018-05-07&'
                    'description=some%20description%20'
                    'with%20&queue=TAXIBUGPOLICE&'
                    'tags=english_text_%2A%2B%26%25%40'
                ),
            },
            [
                {
                    'action_id': 'test_uid',
                    'action': 'generate_extra_ticket_link',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'in_addition': False,
                    'tags_changes': [
                        {'change_type': 'add', 'tag': 'english_text_*+&%@'},
                    ],
                    'url': (
                        'https://st.yandex-team.ru/createTicket?'
                        'summary=some%20summary%20at%202018-05-07&'
                        'description=some%20description%20'
                        'with%20&queue=TAXIBUGPOLICE&'
                        'tags=english_text_%2A%2B%26%25%40'
                    ),
                    'query_params': {
                        'profile': 'yandex-team',
                        'queue': 'TAXIBUGPOLICE',
                        'summary_tanker_key': 'some_summary_key',
                        'description_tanker_key': 'extra_data_description_key',
                        'additional_tag': 'english_text_*+&%@',
                    },
                },
            ],
        ),
        (
            'yandex-team',
            'some_summary_key',
            'some_description_key',
            'BADQUEUE',
            None,
            400,
            {
                'message': (
                    'Tickets in queue BADQUEUE not allowed '
                    'for profile yandex-team'
                ),
                'status': 'queue_not_allowed',
            },
            None,
        ),
        (
            'badprofile',
            'some_summary_key',
            'some_description_key',
            'TAXIBUGPOLICE',
            None,
            400,
            {
                'message': 'Wrong profile badprofile',
                'status': 'bad_startrack_profile',
            },
            None,
        ),
    ],
)
@pytest.mark.translations(
    chatterbox={
        'some_summary_key': {'ru': 'some summary at {date_created}'},
        'some_description_key': {'ru': 'some description of {task_id} {city}'},
        'extra_data_description_key': {
            'ru': 'some description with {extra_data}',
        },
    },
)
@pytest.mark.now(NOW.isoformat())
async def test_extra_ticket_link(
        cbox,
        mock_random_str_uuid,
        profile,
        summary_tanker_key,
        description_tanker_key,
        queue,
        additional_tag,
        expected_status,
        expected_response,
        expected_history,
):
    mock_random_str_uuid()
    params = {
        'profile': profile,
        'queue': queue,
        'summary_tanker_key': summary_tanker_key,
        'description_tanker_key': description_tanker_key,
    }
    if additional_tag:
        params['additional_tag'] = additional_tag

    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a1/generate_extra_ticket_link',
        params=params,
        data={},
    )
    assert cbox.status == expected_status
    assert cbox.body_data == expected_response

    if expected_history is not None:
        task = await cbox.db.support_chatterbox.find_one(
            {'_id': bson.objectid.ObjectId('5b2cae5cb2682a976914c2a1')},
        )
        assert task['history'] == expected_history


@pytest.mark.parametrize(
    'task_id, query, messages, expected_history, expected_status',
    [
        (
            '5b2cae5cb2682a976914c2b0',
            {'hidden_comment': 'some hidden comment'},
            [],
            [
                {
                    'action_id': 'test_uid',
                    'action': 'hidden_comment',
                    'in_addition': False,
                    'hidden_comment': 'some hidden comment',
                    'created': dates.timestring(NOW, timezone='UTC'),
                    'login': 'superuser',
                    'line': 'first',
                },
            ],
            'in_progress',
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_pull_startrack_comments(
        cbox,
        mock_chat_add_update,
        mock_chat_get_history,
        mock_random_str_uuid,
        task_id,
        query,
        messages,
        expected_history,
        expected_status,
        mock_st_get_messages,
        patch,
        mock_st_create_comment,
):
    mock_chat_get_history({'messages': messages})
    mock_random_str_uuid()

    expected_comment = {
        'login': 'superuser',
        'comment': 'some hidden comment',
        'created': NOW,
        'external_comment_id': '1005005505045045040',
    }
    mock_st_get_messages(
        {'messages': [], 'total': 0, 'hidden_comments': [expected_comment]},
    )

    @patch(
        'chatterbox.internal.task_source._startrack.'
        'Startrack.put_hidden_comment',
    )
    async def put_hidden_comment(task, comment, comment_index, **kwargs):
        await stq_task.startrack_hidden_comment(
            cbox.app,
            task['external_id'],
            comment,
            comment_index,
            log_extra=kwargs.get('log_extra'),
            profile=kwargs.get('profile'),
        )

    await cbox.post('/v1/tasks/{}/communicate'.format(task_id), data=query)
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data == {}

    result = await cbox.query('/v1/tasks/{}'.format(task_id))

    task = await result.json()
    assert task['history'] == expected_history
    assert task['status'] == expected_status
    assert len(task['hidden_comments']) == 1

    expected_comment['created'] = dates.timestring(
        expected_comment['created'], timezone='UTC',
    )
    assert task['hidden_comments'][0] == expected_comment


@pytest.mark.translations(
    chatterbox={
        'errors.max_tickets_per_shift_exceed': {
            'ru': (
                'Вы уже выполнили максимальное количество '
                '({max_tickets_count}) тикетов за эту смену'
            ),
            'en': (
                'You have already completed the maximum number of tickets'
                ' ({max_tickets_count}) for this workday'
            ),
        },
    },
)
@pytest.mark.parametrize('locale', ['en', 'ru', 'uk'])
async def test_assign_task_not_acceptable(
        cbox, mock_check_tasks_limits, locale,
):
    check_tasks_limits = mock_check_tasks_limits(10)

    await cbox.post(
        '/v1/tasks/5b2cae5cb2682a976914c2a3/assign',
        data={},
        headers={'Accept-Language': locale},
    )
    assert cbox.status == http.HTTPStatus.NOT_ACCEPTABLE
    assert check_tasks_limits.calls

    if locale == 'ru':
        assert cbox.body_data == {
            'status': 'request_error',
            'message': (
                'Вы уже выполнили максимальное количество '
                '(10) тикетов за эту смену'
            ),
        }
    elif locale == 'en':
        assert cbox.body_data == {
            'status': 'request_error',
            'message': (
                'You have already completed the maximum number of '
                'tickets (10) for this workday'
            ),
        }
    else:
        assert cbox.body_data == {
            'status': 'request_error',
            'message': 'errors.max_tickets_per_shift_exceed',
        }


@pytest.mark.config(
    CHATTERBOX_ATTACHMENT_ALLOWED_MIMETYPES={
        'support-taxi': ['text/plain'],
        'client': ['image/jpeg'],
        'messenger': ['image/jpeg'],
        'driver': ['text/plain'],
    },
)
@pytest.mark.parametrize('handler', ['attachment', 'attachment_with_tvm'])
@pytest.mark.parametrize(
    ('task_id', 'content_type', 'expected_code', 'expected_chat_attach'),
    [
        ('5b2cae5cb2682a976914c2b0', 'text/plain', 200, False),
        ('5b2cae5cb2682a976914c2a1', 'image/jpeg', 200, True),
        ('5c2cae5cb2682a976914c2a1', 'image/jpeg', 200, True),
        ('5b2cae5cb2682a976914c2c9', 'image/jpeg', 400, False),
    ],
)
async def test_upload_attachment(
        cbox,
        handler,
        mock_st_upload_attachment,
        mock_chat_attachment,
        mock_magic,
        task_id,
        content_type,
        expected_code,
        expected_chat_attach,
):
    mock_magic(content_type)
    attachment_id = '123456'
    mock_st_upload_attachment(attachment_id)
    chat_attach = mock_chat_attachment(attachment_id)
    tmp = tempfile.NamedTemporaryFile(delete=False)
    try:
        with open(tmp.name, 'w') as tmpf:
            tmpf.write('some text')

        with open(tmp.name, 'rb') as tmpf:
            await cbox.post(
                '/v1/tasks/{}/{}'.format(task_id, handler),
                params={'filename': 'test_file.txt'},
                raw_data=tmpf,
            )
    finally:
        os.remove(tmp.name)

    assert cbox.status == expected_code
    if expected_code == 200:
        assert cbox.body_data == {'id': attachment_id}

    if expected_chat_attach:
        calls_data = chat_attach.calls
        assert len(calls_data) == 1
        if 'sender_role' in calls_data[0]['kwargs']:
            assert calls_data[0]['kwargs']['sender_role'] == 'support'
        assert calls_data[0]['kwargs']['content_type'] == content_type
    else:
        assert not chat_attach.calls


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    CHATTERBOX_LINES={
        'second': {'types': ['client']},
        'first': {'types': ['client']},
    },
    CHATTERBOX_OKTELL_ACTIONS={
        'export': {'action_tag': 'export_test_tag', 'action': 'export'},
        'close': {
            'action_tag': 'close_test_tag',
            'action': 'close',
            'macro_id': 1,
        },
        'dismiss': {'action_tag': 'dismiss_test_tag', 'action': 'dismiss'},
        'communicate': {
            'action_tag': 'communicate_tag',
            'action': 'communicate',
            'macro_id': 1,
        },
        'forward': {
            'action_tag': 'next_test_tag',
            'action': 'forward',
            'line': 'second',
        },
    },
)
@pytest.mark.parametrize(
    ('call_status', 'expected_status'),
    [
        ('export', 'export_enqueued'),
        ('close', 'closed'),
        ('dismiss', 'closed'),
        ('communicate', 'new'),
        ('forward', 'reopened'),
    ],
)
async def test_oktell_action(
        cbox,
        cbox_context,
        loop,
        monkeypatch,
        mock_chat_add_update,
        mock_chat_get_history,
        call_status,
        expected_status,
):
    mock_chat_get_history({'messages': []})
    cbox.app.secdist['settings_override']['ADMIN_ROBOT_LOGIN_BY_TOKEN'] = {
        'some_token': 'robot-chatterbox',
    }

    task_id = '5b2cae5cb2682a976914c2a8'
    await cbox.post(
        '/v1/tasks/{}/oktell_action'.format(task_id),
        data={'call_status': call_status},
        headers={'YaTaxi-Api-Key': 'some_oktell_token'},
    )
    assert cbox.status == http.HTTPStatus.OK

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )
    assert task['status'] == expected_status


@pytest.mark.parametrize(
    (
        'task_id',
        'data',
        'query',
        'custom_create_response',
        'expected_code',
        'expected_history',
        'expected_hidden_comment_put_calls',
        'expected_send_macros_put_calls',
        'expected_salesforce_create',
        'expected_salesforce_update',
    ),
    [
        (
            '5b2cae5cb2682a976914c2b0',
            {
                'comment': 'external comment',
                'macro_ids': ['some_macro_id_2', 'some_macro_id'],
                'themes': ['1', '2'],
                'themes_tree': ['1', '4'],
            },
            {'subject': 'test subject'},
            None,
            http.HTTPStatus.OK,
            [
                {
                    'action': 'update_meta',
                    'created': datetime.datetime(2018, 6, 15, 12, 34),
                    'line': 'first',
                    'login': 'superuser',
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'agent_ticket_id',
                            'value': 'sf_id',
                        },
                    ],
                },
                {
                    'action_id': 'test_uid',
                    'action': 'external_request',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'hidden_comment': 'external comment',
                    'in_addition': False,
                    'macro_ids': ['some_macro_id_2', 'some_macro_id'],
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'some_macro_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['some_macro_id', 'some_macro_id_2'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'theme_name',
                            'value': 'Theme::Subtheme 2',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes_tree',
                            'value': [1, 4],
                        },
                    ],
                    'query_params': {'subject': 'test subject'},
                    'reopen_at': datetime.datetime(2018, 6, 15, 14, 34),
                    'tags_added': ['3', '4', '5'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': '5'},
                    ],
                },
            ],
            [['some_queue-1', 'external comment', 0]],
            [
                [
                    {'$oid': '5b2cae5cb2682a976914c2b0'},
                    ['some_macro_id_2', 'some_macro_id'],
                ],
            ],
            {
                'data': {
                    'CRM_Source__c': 'Partner1',
                    'Case_Type__c': 'Partner',
                    'Description': 'external comment',
                    'Partner1_Case_ID__c': '5b2cae5cb2682a976914c2b0',
                    'Partner_Ride_Order_ID__c': 'order_12345',
                    'Region__c': 'RU',
                    'Ride_ID__c': 'agent_order_12345',
                    'Status': 'New',
                    'Sub_Type__c': 'Partner',
                    'Subject': 'test subject',
                    'partners_metadata': 'our_test_data',
                },
            },
            None,
        ),
        (
            '5b2cae5cb2682a976914c2b0',
            {
                'comment': 'external comment',
                'macro_ids': ['some_macro_id_2', 'some_macro_id'],
                'themes': ['1', '2'],
                'themes_tree': ['1', '4'],
            },
            {'subject': 'test subject'},
            {},
            http.HTTPStatus.FAILED_DEPENDENCY,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c223',
            {'comment': 'external comment'},
            {'subject': 'test subject'},
            None,
            http.HTTPStatus.OK,
            [
                {
                    'action_id': 'test_uid',
                    'action': 'external_request',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'hidden_comment': 'external comment',
                    'in_addition': False,
                    'query_params': {'subject': 'test subject'},
                    'reopen_at': datetime.datetime(2018, 6, 15, 14, 34),
                },
            ],
            [['some_queue-2', 'external comment', 0]],
            None,
            None,
            {
                'data': {'Comments': 'external comment'},
                'field_name': 'Partner1_Case_ID__c',
                'field_value': '5b2cae5cb2682a976914c223',
            },
        ),
        (
            '5b2cae5cb2682a976914c221',
            {'comment': 'external comment'},
            {'subject': 'test subject'},
            None,
            http.HTTPStatus.FAILED_DEPENDENCY,
            None,
            None,
            None,
            None,
            None,
        ),
        (
            '5b2cae5cb2682a976914c222',
            {
                'comment': 'external comment',
                'macro_ids': ['some_macro_id_2', 'some_macro_id'],
                'themes': ['1', '2'],
                'themes_tree': ['1', '4'],
            },
            {},
            None,
            http.HTTPStatus.OK,
            [
                {
                    'action_id': 'test_uid',
                    'action': 'external_request',
                    'created': NOW,
                    'login': 'superuser',
                    'line': 'first',
                    'hidden_comment': 'external comment',
                    'in_addition': False,
                    'macro_ids': ['some_macro_id_2', 'some_macro_id'],
                    'meta_changes': [
                        {
                            'change_type': 'set',
                            'field_name': 'macro_id',
                            'value': 'some_macro_id',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'currently_used_macro_ids',
                            'value': ['some_macro_id', 'some_macro_id_2'],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes',
                            'value': [1, 2],
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'theme_name',
                            'value': 'Theme::Subtheme 2',
                        },
                        {
                            'change_type': 'set',
                            'field_name': 'themes_tree',
                            'value': [1, 4],
                        },
                    ],
                    'reopen_at': datetime.datetime(2018, 6, 15, 14, 34),
                    'tags_added': ['3', '4', '5'],
                    'tags_changes': [
                        {'change_type': 'add', 'tag': '3'},
                        {'change_type': 'add', 'tag': '4'},
                        {'change_type': 'add', 'tag': '5'},
                    ],
                },
            ],
            None,
            None,
            None,
            {
                'data': {'Comments': 'external comment'},
                'field_name': 'Partner1_Case_ID__c',
                'field_value': '5b2cae5cb2682a976914c222',
            },
        ),
    ],
)
@pytest.mark.config(
    CHATTERBOX_HISTORY_TAGS_ADDED=True,
    CHATTERBOX_EXTERNAL_SALESFORCE={
        'enabled': True,
        'reopen_delay': 120,
        'send_metadata': {'our_metadata': 'partners_metadata'},
    },
)
@pytest.mark.now(NOW.isoformat())
async def test_external_request(
        cbox,
        stq,
        task_id,
        data,
        query,
        custom_create_response,
        expected_code,
        expected_history,
        expected_hidden_comment_put_calls,
        expected_send_macros_put_calls,
        expected_salesforce_create,
        expected_salesforce_update,
        mock_st_get_ticket,
        mock_st_create_comment,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        mock_st_transition,
        mock_st_update_ticket,
        mock_chat_get_history,
        mock_chat_add_update,
        mock_external_salesforce_create,
        mock_external_salesforce_update,
        mock_external_salesforce_auth,
        mock_random_str_uuid,
):
    if custom_create_response is None:
        custom_create_response = {'id': 'sf_id'}
    create_mock = mock_external_salesforce_create(custom_create_response)
    mock_chat_get_history({'messages': []})
    mock_st_get_all_attachments()
    mock_st_get_comments([])
    mock_st_update_ticket('open')
    mock_random_str_uuid()

    await cbox.post(
        '/v1/tasks/{}/external_request'.format(task_id),
        data=data,
        params=query,
    )
    assert cbox.status == expected_code

    if cbox.status != http.HTTPStatus.OK:
        return

    task = await cbox.db.support_chatterbox.find_one(
        {'_id': bson.objectid.ObjectId(task_id)},
    )
    assert task['status'] == 'deferred'
    task['history'][0].pop('external_id', None)
    assert task['history'] == expected_history

    assert not mock_chat_add_update.calls
    assert not mock_st_create_comment.calls

    if expected_hidden_comment_put_calls is not None:
        for call in expected_hidden_comment_put_calls:
            assert (
                stq.startrack_hidden_comment_queue.next_call()['args'] == call
            )
        assert not stq.startrack_hidden_comment_queue.has_calls
    if expected_send_macros_put_calls is not None:
        for call in expected_send_macros_put_calls:
            assert (
                stq.chatterbox_send_macros_to_support_tags.next_call()['args']
                == call
            )
        assert not stq.chatterbox_send_macros_to_support_tags.has_calls

    if expected_salesforce_update is not None:
        execute_sf_call = mock_external_salesforce_update.calls[0]
        execute_sf_call['kwargs'].pop('log_extra')
        assert execute_sf_call['kwargs'] == expected_salesforce_update

    if expected_salesforce_create is not None:
        execute_sf_call = create_mock.calls[0]
        execute_sf_call['kwargs'].pop('log_extra')
        assert execute_sf_call['kwargs'] == expected_salesforce_create

    assert task['inner_comments'] == [
        {
            'comment': 'external comment',
            'login': 'superuser',
            'created': NOW,
            'type': 'external_request',
        },
    ]
