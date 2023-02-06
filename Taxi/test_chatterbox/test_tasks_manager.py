# pylint: disable=invalid-name, protected-access, too-many-lines
import datetime

import pytest

from chatterbox import constants
from chatterbox.internal.tasks_manager import _constants
from chatterbox.internal.tasks_manager import _private

NOW = datetime.datetime(2018, 6, 15, 12, 34)

ALL_STATUS_EXCEPT_PREDISPATCH = (
    _constants.STATUS_NEW,
    _constants.STATUS_IN_PROGRESS,
    _constants.STATUS_REOPENED,
    _constants.STATUS_FORWARDED,
    _constants.STATUS_WAITING,
    _constants.STATUS_AUTOREPLY_IN_PROGRESS,
    _constants.STATUS_DEFERRED,
    _constants.STATUS_CLOSED,
    _constants.STATUS_READY_TO_ARCHIVE,
    _constants.STATUS_ARCHIVED,
    _constants.STATUS_ARCHIVE_IN_PROGRESS,
    _constants.STATUS_ARCHIVE_FAILED,
    _constants.STATUS_EXPORTED,
    _constants.STATUS_EXPORT_ENQUEUED,
    _constants.STATUS_EXPORT_FAILED,
)


@pytest.mark.parametrize(
    'metadata, need_update, task_statuses, right_result',
    [
        (
            {'not_empty': 'value'},
            True,
            (_constants.STATUS_PREDISPATCH,),
            (True, True),
        ),
        (
            {'not_empty': 'value'},
            False,
            (_constants.STATUS_PREDISPATCH,),
            (True, True),
        ),
        ({}, False, (_constants.STATUS_PREDISPATCH,), (True, False)),
        (
            {'not_empty': 'value'},
            True,
            ALL_STATUS_EXCEPT_PREDISPATCH,
            (True, True),
        ),
        (
            {'not_empty': 'value'},
            False,
            ALL_STATUS_EXCEPT_PREDISPATCH,
            (False, False),
        ),
        ({}, False, ALL_STATUS_EXCEPT_PREDISPATCH, (True, False)),
    ],
)
async def test_check_need_updates(
        cbox, monkeypatch, metadata, need_update, task_statuses, right_result,
):
    def dummy_check(
            task,
            meta_changes=None,
            tags_changes=None,
            card_number_fields=None,
            zendesk_fields=None,
    ):
        return need_update

    monkeypatch.setattr(_private, 'need_update_meta', dummy_check)

    for task_status in task_statuses:
        task = {'_id': 'chat_id', 'status': task_status}
        result = cbox.app.tasks_manager._check_need_updates(task, metadata)

        assert result == right_result, task_status


async def test_update_meta_and_apply_source(cbox, monkeypatch):
    call_order = []

    task = {'_id': 'task_id', 'status': 'in_progress', 'line': 'offline'}

    def dummy_check_need_updates(*args, **kwargs):
        return True, True

    monkeypatch.setattr(
        cbox.app.tasks_manager,
        '_check_need_updates',
        dummy_check_need_updates,
    )

    async def dummy_apply_source_updates(*args, **kwargs):
        call_order.append('apply_source_updates')
        return task

    monkeypatch.setattr(
        cbox.app.tasks_manager,
        '_apply_source_updates',
        dummy_apply_source_updates,
    )

    async def dummy_update_meta(*args, **kwargs):
        call_order.append('update_meta')
        return task

    monkeypatch.setattr(
        cbox.app.tasks_manager, 'update_meta', dummy_update_meta,
    )

    await cbox.app.tasks_manager._update_meta_and_apply_source(
        task,
        source={'metadata': {'last_message_from_user': False}},
        metadata={},
    )

    assert call_order == ['apply_source_updates', 'update_meta']


class TestDefer:
    @pytest.mark.now(NOW.isoformat())
    async def test_chat_task(
            self, cbox, mock_chat_add_update, mock_task_manager_update_task,
    ):
        chat_task_id = '5b2cae5cb2682a976914c2a1'
        await cbox.app.tasks_manager.defer(
            task_id=chat_task_id,
            login='admin1',
            reopen_at=NOW,
            comment='new comment',
        )

        self.check_asserts(mock_task_manager_update_task)
        assert mock_chat_add_update.calls

    @pytest.mark.now(NOW.isoformat())
    async def test_startreck_task(
            self,
            cbox,
            mock_st_create_comment,
            mock_task_manager_update_task,
            mock_st_update_ticket,
    ):
        """
        Test defer startreck ticket
            in history will be write with comment id as external_id
        """
        st_comment_id = 100500
        mock_st_create_comment.set_response({'id': st_comment_id})
        mock_st_update_ticket('open')
        startreck_task_id = '5b2cae5cb2682a976914c2b0'

        await cbox.app.tasks_manager.defer(
            task_id=startreck_task_id,
            login='admin1',
            reopen_at=NOW,
            comment='new comment',
        )

        self.check_asserts(
            mock_task_manager_update_task, external_id=str(st_comment_id),
        )
        mock_st_create_comment.assert_called()

    @staticmethod
    def check_asserts(mock_task_manager_update_task, external_id=None):
        update = {
            '$push': {
                'history': {
                    'action': 'defer',
                    'comment': 'new comment',
                    'in_addition': False,
                    'reopen_at': NOW,
                },
            },
            '$set': {'reopen_at': NOW, 'status': 'deferred'},
        }
        if external_id is not None:
            update['$push']['history']['external_id'] = external_id

        call_update = mock_task_manager_update_task.call['kwargs']
        assert call_update['update'] == update


class TestClose:
    @pytest.mark.now(NOW.isoformat())
    async def test_chat_task(
            self, cbox, mock_chat_add_update, mock_task_manager_update_task,
    ):
        chat_task_id = '5b2cae5cb2682a976914c2a1'
        await cbox.app.tasks_manager.close(
            task_id=chat_task_id,
            login='admin1',
            comment='new comment',
            ticket_status=constants.TICKET_STATUS_SOLVED,
        )

        self.check_asserts(mock_task_manager_update_task)
        assert mock_chat_add_update.calls

    @pytest.mark.now(NOW.isoformat())
    async def test_startreck_task(
            self,
            cbox,
            mock_task_manager_update_task,
            mock_st_create_comment,
            mock_st_transition,
            mock_st_update_ticket,
    ):
        """
        Test close startreck ticket
            in history will be write with comment id as external_id
        """
        st_comment_id = 100500
        mock_st_create_comment.set_response({'id': st_comment_id})
        mock_st_update_ticket('close')
        startreck_task_id = '5b2cae5cb2682a976914c2b0'
        await cbox.app.tasks_manager.close(
            task_id=startreck_task_id,
            login='admin1',
            comment='new comment',
            ticket_status=constants.TICKET_STATUS_SOLVED,
        )

        self.check_asserts(
            mock_task_manager_update_task, external_id=str(st_comment_id),
        )
        mock_st_create_comment.assert_called()
        assert mock_st_transition.calls

    @staticmethod
    def check_asserts(mock_task_manager_update_task, external_id=None):
        update = {
            '$push': {
                'history': {
                    'action': 'close',
                    'comment': 'new comment',
                    'in_addition': False,
                },
            },
            '$set': {'status': 'closed'},
        }
        if external_id is not None:
            update['$push']['history']['external_id'] = external_id

        call_update = mock_task_manager_update_task.call['kwargs']
        assert call_update['update'] == update


@pytest.mark.translations(
    chatterbox={
        'lines.first': {'ru': 'Первая', 'en': 'First'},
        'lines.second': {'ru': 'Вторая', 'en': 'Second'},
        'lines.сargo': {'ru': 'Грузоперевозки/клиент', 'en': 'Cargo'},
        'dropdowns.close': {'ru': 'Выполнен', 'en': 'Close'},
        'buttons_groups.forward': {'ru': 'Передача', 'en': 'Forward'},
    },
)
@pytest.mark.config(
    CHAT_LINE_TRANSITIONS={
        'first': ['second', 'vip'],
        'second': ['vip', 'сargo', 'first_center'],
    },
    CHATTERBOX_COMMON_BUTTONS={},
    CHATTERBOX_FORWARDING_BUTTONS_ENABLED=True,
    CHATTERBOX_LINES={
        'first': {
            'fields': {},
            'name': '1 · Первая',
            'priority': 14,
            'sort_order': 1,
            'tags': [],
            'title_tanker': 'lines.first',
            'types': ['driver', 'sms'],
        },
        'first_center': {
            'fields': {},
            'name': '1 · Первая линия',
            'priority': 14,
            'sort_order': 1,
            'tags': [],
            'title_tanker': 'lines.first',
            'mode': 'online',
            'types': ['driver', 'sms', 'facebook_support'],
        },
        'second': {
            'fields': {},
            'name': '2 · Вторая',
            'priority': 21,
            'sort_order': 1,
            'tags': [],
            'title_tanker': 'lines.second',
            'types': ['driver', 'sms'],
        },
        'vip': {
            'fields': {},
            'name': '1 · Вип',
            'priority': 12,
            'sort_order': 1,
            'tags': [],
            'title_tanker': 'lines.vip',
            'types': ['driver', 'sms', 'facebook_support'],
        },
        'сargo': {
            'fields': {},
            'name': '1 Грузоперевозки/клиент',
            'priority': 4,
            'sort_order': 1,
            'tags': [],
            'title_tanker': 'lines.сargo',
            'types': ['driver', 'sms'],
        },
    },
    CHATTERBOX_ACTIONS_FIELDS={
        'forward': [
            {'id': 'hidden_comment', 'type': 'string', 'required': False},
            {'id': 'tags', 'type': 'array', 'required': False},
        ],
        'comment': [
            {'id': 'attachment_ids', 'type': 'array', 'required': False},
        ],
    },
    CHATTERBOX_LINES_ACTIONS_FIELDS={
        '__default__': {},
        'second': {'required_fields': {'tags': ['forward']}},
    },
    CHATTERBOX_FOOTER_ACTIONS_V2={
        'offline': [
            {
                'action_id': 'close',
                'title': 'Выполнен',
                'query_params': {},
                'view': {'position': 'footer', 'type': 'dropdown'},
                'title_tanker': 'dropdowns.close',
            },
            {
                'action_id': 'comment',
                'title': 'В ожидании',
                'query_params': {},
                'view': {'position': 'footer', 'type': 'dropdown'},
                'title_tanker': 'dropdowns.comment',
            },
            {
                'action_id': 'defer',
                'title': '',
                'query_params': {},
                'view': {'position': 'footer', 'type': 'dropdown'},
                'title_tanker': 'dropdowns.defer',
            },
        ],
        'online': [
            {
                'action_id': 'comment',
                'title': 'В ожидании',
                'query_params': {},
                'view': {
                    'position': 'footer',
                    'type': 'dropdown',
                    'default': True,
                },
                'title_tanker': 'dropdowns.comment',
            },
            {
                'action_id': 'dismiss',
                'title': '🤐 НТО',
                'query_params': {'chatterbox_button': 'chatterbox_nto'},
                'view': {'position': 'footer', 'type': 'dropdown'},
                'title_tanker': 'dropdowns.dismiss',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'task, lang, expected_buttons',
    [
        (
            {
                '_id': 'task_id_1',
                'line': 'first',
                'tags': [],
                'chat_type': 'sms',
            },
            'ru',
            [
                {
                    'action_id': 'close',
                    'query_params': {},
                    'title': 'Выполнен',
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
                {
                    'action_id': 'defer',
                    'title': '1h',
                    'query_params': {'reopen_at': '2018-06-15T13:34:00+0000'},
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
                {
                    'action_id': 'defer',
                    'title': '12h',
                    'query_params': {'reopen_at': '2018-06-16T00:34:00+0000'},
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
                {
                    'action_id': 'forward',
                    'query_params': {'line': 'second'},
                    'title': 'Вторая',
                    'view': {
                        'group': 'Передача',
                        'position': 'statusbar',
                        'type': 'dropdown',
                    },
                    'body_fields': [
                        {
                            'id': 'hidden_comment',
                            'type': 'string',
                            'checks': [],
                        },
                        {'id': 'tags', 'type': 'array', 'checks': []},
                    ],
                },
                {
                    'action_id': 'forward',
                    'query_params': {'line': 'vip'},
                    'title': '1 · Вип',
                    'view': {
                        'group': 'Передача',
                        'position': 'statusbar',
                        'type': 'dropdown',
                    },
                    'body_fields': [
                        {
                            'id': 'hidden_comment',
                            'type': 'string',
                            'checks': [],
                        },
                        {'id': 'tags', 'type': 'array', 'checks': []},
                    ],
                },
            ],
        ),
        (
            {
                '_id': 'task_id_1',
                'line': 'first',
                'tags': [],
                'chat_type': 'sms',
            },
            'en',
            [
                {
                    'action_id': 'close',
                    'query_params': {},
                    'title': 'Close',
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
                {
                    'action_id': 'defer',
                    'title': '1h',
                    'query_params': {'reopen_at': '2018-06-15T13:34:00+0000'},
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
                {
                    'action_id': 'defer',
                    'title': '12h',
                    'query_params': {'reopen_at': '2018-06-16T00:34:00+0000'},
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
                {
                    'action_id': 'forward',
                    'query_params': {'line': 'second'},
                    'title': 'Second',
                    'view': {
                        'group': 'Forward',
                        'position': 'statusbar',
                        'type': 'dropdown',
                    },
                    'body_fields': [
                        {
                            'id': 'hidden_comment',
                            'type': 'string',
                            'checks': [],
                        },
                        {'id': 'tags', 'type': 'array', 'checks': []},
                    ],
                },
                {
                    'action_id': 'forward',
                    'query_params': {'line': 'vip'},
                    'title': '1 · Вип',
                    'view': {
                        'group': 'Forward',
                        'position': 'statusbar',
                        'type': 'dropdown',
                    },
                    'body_fields': [
                        {
                            'id': 'hidden_comment',
                            'type': 'string',
                            'checks': [],
                        },
                        {'id': 'tags', 'type': 'array', 'checks': []},
                    ],
                },
            ],
        ),
        (
            {
                '_id': 'task_id_1',
                'line': 'first_center',
                'tags': [],
                'chat_type': 'driver',
            },
            'en',
            [
                {
                    'action_id': 'comment',
                    'title': 'В ожидании',
                    'query_params': {},
                    'body_fields': [],
                    'view': {
                        'position': 'footer',
                        'type': 'dropdown',
                        'default': True,
                    },
                },
                {
                    'action_id': 'dismiss',
                    'title': '🤐 НТО',
                    'query_params': {'chatterbox_button': 'chatterbox_nto'},
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
            ],
        ),
        (
            {
                '_id': 'task_id_1',
                'line': 'first_center',
                'tags': [],
                'chat_type': 'startrack',
            },
            'en',
            [
                {
                    'action_id': 'comment',
                    'title': 'В ожидании',
                    'query_params': {},
                    'view': {
                        'position': 'footer',
                        'type': 'dropdown',
                        'default': True,
                    },
                    'body_fields': [
                        {
                            'id': 'attachment_ids',
                            'type': 'array',
                            'checks': [],
                        },
                    ],
                },
                {
                    'action_id': 'dismiss',
                    'title': '🤐 НТО',
                    'query_params': {'chatterbox_button': 'chatterbox_nto'},
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
            ],
        ),
        (
            {
                '_id': 'task_id_1',
                'line': 'second',
                'tags': [],
                'chat_type': 'facebook_support',
            },
            'en',
            [
                {
                    'action_id': 'close',
                    'query_params': {},
                    'title': 'Close',
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
                {
                    'action_id': 'comment',
                    'query_params': {},
                    'title': 'В ожидании',
                    'body_fields': [],
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
                {
                    'action_id': 'defer',
                    'title': '1h',
                    'query_params': {'reopen_at': '2018-06-15T13:34:00+0000'},
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
                {
                    'action_id': 'defer',
                    'title': '12h',
                    'query_params': {'reopen_at': '2018-06-16T00:34:00+0000'},
                    'view': {'position': 'footer', 'type': 'dropdown'},
                },
                {
                    'action_id': 'forward',
                    'query_params': {'line': 'vip'},
                    'title': '1 · Вип',
                    'view': {
                        'group': 'Forward',
                        'position': 'statusbar',
                        'type': 'dropdown',
                    },
                    'body_fields': [
                        {
                            'id': 'hidden_comment',
                            'type': 'string',
                            'checks': [],
                        },
                        {
                            'id': 'tags',
                            'type': 'array',
                            'checks': ['not-empty'],
                        },
                    ],
                },
                {
                    'action_id': 'forward',
                    'body_fields': [
                        {
                            'checks': [],
                            'id': 'hidden_comment',
                            'type': 'string',
                        },
                        {
                            'checks': ['not-empty'],
                            'id': 'tags',
                            'type': 'array',
                        },
                    ],
                    'query_params': {'line': 'first_center'},
                    'title': 'First',
                    'view': {
                        'group': 'Forward',
                        'position': 'statusbar',
                        'type': 'dropdown',
                    },
                },
            ],
        ),
        pytest.param(
            {
                '_id': 'task_id_1',
                'line': 'first',
                'tags': [],
                'chat_type': 'startrack',
            },
            'ru',
            [
                {
                    'action_id': 'external_comment',
                    'query_params': {},
                    'title': 'Выполнен',
                    'view': {'position': 'footer', 'type': 'radio'},
                },
            ],
            marks=[
                pytest.mark.config(
                    CHATTERBOX_FOOTER_ACTIONS_V2={
                        'offline': [
                            {
                                'action_id': 'close',
                                'query_params': {},
                                'display_conditions': {'line': 'first_center'},
                                'title': 'Выполнен',
                                'title_tanker': 'dropdowns.close',
                                'view': {
                                    'position': 'footer',
                                    'type': 'radio',
                                },
                            },
                            {
                                'action_id': 'external_comment',
                                'query_params': {},
                                'display_conditions': {'line': 'first'},
                                'title': 'Выполнен',
                                'title_tanker': 'dropdowns.close',
                                'view': {
                                    'position': 'footer',
                                    'type': 'radio',
                                },
                            },
                        ],
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_forward_actions(cbox, task, lang, expected_buttons):
    buttons = cbox.app.tasks_manager.get_available_actions_for_take(task, lang)

    assert buttons == expected_buttons


async def test_set_external_comment_id(cbox):
    task = await cbox.app.db.support_chatterbox.find_one(
        {'_id': 'to_create_hidden_comment'},
    )

    external_comment_id = '100'
    comments_num = len(task['inner_comments'])
    await cbox.app.tasks_manager.set_external_comment_id(
        task['external_id'],
        task['inner_comments'][comments_num - 1]['comment'],
        comment_index=comments_num - 1,
        external_comment_id=external_comment_id,
    )

    task = await cbox.app.db.support_chatterbox.find_one(
        {'_id': 'to_create_hidden_comment'},
    )

    assert (
        task['inner_comments'][comments_num - 1]['external_comment_id']
        == external_comment_id
    )


@pytest.mark.parametrize(
    'comments,expected_comments',
    [
        (
            [
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:56+0000',
                    'comment': 'test comment',
                    'external_comment_id': '123',
                },
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:57+0000',
                    'comment': 'another comment',
                    'external_comment_id': '456',
                },
            ],
            [
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:56+0000',
                    'comment': 'test comment',
                    'external_comment_id': '123',
                },
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:57+0000',
                    'comment': 'another comment',
                    'external_comment_id': '456',
                },
            ],
        ),
        (
            [
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:56+0000',
                    'comment': 'test comment',
                    'external_comment_id': '123',
                },
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:56+0000',
                    'comment': 'test comment',
                    'external_comment_id': '123',
                },
            ],
            [
                {
                    'login': 'superuser',
                    'created': '2018-05-07T12:34:56+0000',
                    'comment': 'test comment',
                    'external_comment_id': '123',
                },
            ],
        ),
    ],
)
async def test_exclude_comments_duplicates(cbox, comments, expected_comments):
    real_comments = await cbox.app.tasks_manager._exclude_comments_duplicates(
        comments,
    )
    assert real_comments == expected_comments


@pytest.mark.parametrize(
    'minutes, expected_string', [(60, '1h'), (75, '1h15m'), (7, '7m')],
)
async def test_get_defet_time_string(cbox, minutes, expected_string):
    time_string = cbox.app.tasks_manager._get_defer_time_string(minutes)
    assert time_string == expected_string


@pytest.mark.config(
    CHATTERBOX_NEW_BUTTONS_CONFIG_ENABLED=True,
    CHATTERBOX_COMMON_BUTTONS=[
        {
            'action_id': 'dismiss',
            'title': '🤐 НТО',
            'query_params': {'chatterbox_button': 'chatterbox_nto'},
            'display_conditions': {
                'tags': 'second_tag',
                '#not': {'tags': 'random_tag'},
            },
        },
        {
            'action_id': 'export',
            'title': '✍️ Ручное',
            'query_params': {'chatterbox_button': 'chatterbox_zen'},
            'display_conditions': {'meta_info/payment_type': 'card'},
            'lines': ['first'],
        },
        {
            'action_id': 'export',
            'title': '💣 Ургент',
            'query_params': {'chatterbox_button': 'chatterbox_urgent'},
            'display_conditions': {
                'meta_info/tariff': {'#in': ['vip', 'uberblack']},
            },
        },
        {
            'action_id': 'skip',
            'title': 'Группа 1',
            'query_params': {},
            'display_conditions': {'tags': 'first_tag'},
            'group': 'group_1',
        },
        {
            'action_id': 'skip',
            'title': 'Группа 2',
            'query_params': {},
            'display_conditions': {'tags': 'second_tag'},
            'group': 'group_1',
        },
        {
            'action_id': 'skip',
            'title': 'Группа 3',
            'query_params': {},
            'display_conditions': {'tags': 'third_tag'},
            'group': 'group_2',
        },
    ],
)
@pytest.mark.parametrize(
    'task, expected_buttons',
    [
        (
            {
                '_id': 'task_id_1',
                'line': 'first',
                'chat_type': 'sms',
                'tags': ['first_tag', 'second_tag'],
            },
            [
                {
                    'action_id': 'dismiss',
                    'query_params': {'chatterbox_button': 'chatterbox_nto'},
                    'title': '🤐 НТО',
                    'view': {'position': 'statusbar', 'type': 'button'},
                },
                {
                    'action_id': 'skip',
                    'title': 'Группа 1',
                    'query_params': {},
                    'view': {
                        'position': 'statusbar',
                        'type': 'button',
                        'group': 'group_1',
                    },
                },
                {
                    'action_id': 'skip',
                    'title': 'Группа 2',
                    'query_params': {},
                    'view': {
                        'position': 'statusbar',
                        'type': 'button',
                        'group': 'group_1',
                    },
                },
            ],
        ),
        (
            {
                '_id': 'task_id_2',
                'line': 'first',
                'chat_type': 'sms',
                'tags': ['second_tag', 'third_tag', 'random_tag'],
            },
            [
                {
                    'action_id': 'skip',
                    'title': 'Группа 2',
                    'query_params': {},
                    'view': {
                        'position': 'statusbar',
                        'type': 'button',
                        'group': 'group_1',
                    },
                },
                {
                    'action_id': 'skip',
                    'title': 'Группа 3',
                    'query_params': {},
                    'view': {
                        'position': 'statusbar',
                        'type': 'button',
                        'group': 'group_2',
                    },
                },
            ],
        ),
        (
            {
                '_id': 'task_id_3',
                'line': 'first',
                'chat_type': 'sms',
                'tags': ['third_tag'],
            },
            [
                {
                    'action_id': 'skip',
                    'title': 'Группа 3',
                    'query_params': {},
                    'view': {
                        'position': 'statusbar',
                        'type': 'button',
                        'group': 'group_2',
                    },
                },
            ],
        ),
        (
            {
                '_id': 'task_id_4',
                'line': 'first',
                'chat_type': 'sms',
                'meta_info': {'payment_type': 'card'},
            },
            [
                {
                    'action_id': 'export',
                    'title': '✍️ Ручное',
                    'query_params': {'chatterbox_button': 'chatterbox_zen'},
                    'view': {'position': 'statusbar', 'type': 'button'},
                },
            ],
        ),
        (
            {
                '_id': 'task_id_5',
                'line': 'first',
                'chat_type': 'sms',
                'meta_info': {'tariff': 'uberblack'},
            },
            [
                {
                    'action_id': 'export',
                    'title': '💣 Ургент',
                    'query_params': {'chatterbox_button': 'chatterbox_urgent'},
                    'view': {'position': 'statusbar', 'type': 'button'},
                },
            ],
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_buttons_display_conditions(cbox, task, expected_buttons):
    config_buttons = cbox.app.config.CHATTERBOX_COMMON_BUTTONS
    buttons = cbox.app.tasks_manager.generate_task_buttons(
        task, config_buttons,
    )
    assert buttons == expected_buttons


@pytest.mark.filldb(support_chatterbox='change_support_admin_green')
@pytest.mark.parametrize(
    'task_id',
    [
        '5b2cae5cb2682a976914c2a1',
        '5b2cae5cb2682a976914c2b0',
        '5b2cae5cb2682a976914c2c2',
    ],
)
async def test_change_support_admin_green(cbox, cbox_context, pgsql, task_id):
    task = await cbox_context.data.db.secondary.support_chatterbox.find_one(
        {'_id': task_id},
    )
    updated = await cbox.app.tasks_manager.reset_support_admin(task=task)

    assert updated
    assert updated['support_admin'] == _constants.LOGIN_SUPERUSER
    assert (
        updated['history'][-1]['action']
        == _constants.ACTION_RESET_SUPPORT_ADMIN
    )
    assert updated['history'][-1]['old_support_admin'] == task['support_admin']

    record_in_db = (
        await cbox_context.data.db.secondary.support_chatterbox.find_one(
            {'_id': task_id},
        )
    )

    assert updated == record_in_db

    cursor = pgsql['chatterbox'].cursor()
    cursor.execute(
        """
            SELECT *
            FROM chatterbox.supporter_tasks
            WHERE task_id = %s
        """,
        (task_id,),
    )

    assert not cursor.fetchone()


@pytest.mark.parametrize(
    'task',
    [{'_id': 'unexpected', 'support_admin': 'admin1', 'line': 'first'}],
)
async def test_change_support_admin_red(cbox, cbox_context, pgsql, task):
    updated = await cbox.app.tasks_manager.reset_support_admin(task=task)

    assert not updated
