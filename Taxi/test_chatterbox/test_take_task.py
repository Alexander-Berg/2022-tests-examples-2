# pylint: disable=no-self-use, too-many-lines, too-many-arguments
import dataclasses
import datetime
import http

import bson
import pymongo
import pytest

from chatterbox import constants
from chatterbox.api import rights
from test_chatterbox import plugins as conftest


def get_db_status(current_status: str) -> tuple:
    if current_status.endswith('-in-additional'):
        in_additional = True
        db_current_status = current_status.split('-in-additional')[0]
    else:
        in_additional = False
        db_current_status = current_status
    return db_current_status, in_additional


@pytest.mark.translations(
    chatterbox={
        'buttons.nto': {'ru': '🤐 НТО', 'en': '🤐 Dismiss'},
        'buttons.urgent': {'ru': 'Ургент', 'en': 'Urgent'},
        'dropdowns.comment': {'ru': 'В ожидании', 'en': ''},
    },
)
@pytest.mark.config(
    DEFER_INTERVALS_BY_MINS={
        '__default__': [60, 720],
        'first': [1260, 1440, 2880],
    },
)
@pytest.mark.now('2018-09-06T12:43:56')
async def test_take_task(cbox, mock_chat_get_history):
    mock_chat_get_history({'messages': [{'text': 'some message'}], 'total': 1})

    awaiting_tags = {
        'in_progress_task_id': ['tag_1', 'tag_2'],
        'my_reopen_task_id': ['tag_3'],
        'another_reopen_task_id': [],
        'new_and_updated_task_id': [],
        'newer_but_not_updated_task_id': [],
        'recently_updated_forwarded_task_id': [],
    }
    awaiting_metainfo = {
        'in_progress_task_id': {},
        'my_reopen_task_id': {'status_before_assign': 'reopened'},
        'another_reopen_task_id': {'status_before_assign': 'reopened'},
        'new_and_updated_task_id': {'status_before_assign': 'new'},
        'recently_updated_forwarded_task_id': {
            'status_before_assign': 'forwarded',
        },
        'newer_but_not_updated_task_id': {
            'user_id': 'some_user_id',
            'order_id': 'some_order_id',
            'user_phone': '+79876543210',
            'ask_csat': False,
            'csat_value': 'amazing',
            'csat_reasons': ['fast answer', 'thank you'],
            'themes': ['1', '2'],
            'themes_tree': ['4', '5'],
            'ml_suggestions': [],
            'status_before_assign': 'new',
        },
    }

    for expected_id in [
            'in_progress_task_id',
            'my_reopen_task_id',
            'another_reopen_task_id',
            'recently_updated_forwarded_task_id',
            'new_and_updated_task_id',
            'newer_but_not_updated_task_id',
    ]:
        await cbox.post(
            '/v1/tasks/take/',
            data={'lines': ['first']},
            headers={'Accept-Language': 'en'},
        )
        assert cbox.status == http.HTTPStatus.OK
        task = cbox.body_data
        assert task['id'] == expected_id
        assert task['tags'] == awaiting_tags[task['id']]
        assert task['meta_info'] == awaiting_metainfo[task['id']]
        assert [action['title'] for action in task['actions']] == [
            'Выполнен',
            'В ожидании',
            'Только отправить',
            '21h',
            '24h',
            '48h',
            '🤐 НТО',
            '✍️ Ручное',
            '💣 Ургент',
            '🔑 Потеряшки',
        ]
        assert task['chat_messages'] == {
            'messages': [{'text': 'some message'}],
            'total': 1,
        }

        # double action must have same result
        await cbox.post('/v1/tasks/take/', data={})
        assert cbox.status == http.HTTPStatus.OK
        task = cbox.body_data
        assert task['id'] == expected_id

        await cbox.db.support_chatterbox.update(
            {'_id': task['id']}, {'$set': {'status': 'closed'}},
        )

    await cbox.post('/v1/tasks/take/', data={})
    assert cbox.status == http.HTTPStatus.NOT_FOUND


@pytest.mark.filldb(support_chatterbox='by_id')
@pytest.mark.parametrize(
    'assigned,params,data,expected_code,task_id,expected_get_history_kwargs,'
    'expected_get_comments_kwargs,expected_status_before_assign',
    [
        (
            False,
            None,
            {'lines': ['first'], 'force': True},
            200,
            '5cf94043629526419e77b82d',
            {
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': None,
                'log_extra': None,
            },
            None,
            None,
        ),
        (
            False,
            None,
            {'lines': ['first'], 'force': True},
            200,
            '5df94043629526419e77b82d',
            {
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': None,
                'log_extra': None,
                'user_guid': '10000000-0000-0000-0000-000000000001',
            },
            None,
            None,
        ),
        (
            False,
            None,
            {'lines': ['first'], 'force': True},
            409,
            '5cd2946afe6b0bcb689941fa',
            None,
            None,
            None,
        ),
        (
            False,
            None,
            {'lines': ['urgent'], 'force': True},
            409,
            '5cd2946afe6b0bcb689941fa',
            None,
            None,
            None,
        ),
        (
            False,
            None,
            {'lines': ['first'], 'force': True},
            403,
            '5cf94043629526419e77b82e',
            None,
            None,
            None,
        ),
        (
            True,
            None,
            None,
            200,
            '5cf94043629526419e77b82f',
            {
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': None,
                'log_extra': None,
            },
            None,
            None,
        ),
        (
            True,
            {'last_message_id': 'some_message_id'},
            None,
            400,
            '5cf94043629526419e77b82f',
            {
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': None,
                'log_extra': None,
            },
            None,
            None,
        ),
        (
            True,
            None,
            None,
            200,
            '5b2cae5cb2682a976914c2a5',
            None,
            {'short_id': None, 'per_page': 2000},
            None,
        ),
        (
            False,
            None,
            {'lines': ['first'], 'force': True},
            200,
            '5b2cae5cb2682a976914c297',
            {
                'include_metadata': True,
                'include_participants': True,
                'message_ids_newer_than': None,
                'log_extra': None,
            },
            None,
            'forwarded',
        ),
        (
            True,
            {'last_message_id': 'some_message_id'},
            None,
            400,
            '5b2cae5cb2682a976914c2a5',
            None,
            {'short_id': None, 'per_page': 2000},
            None,
        ),
        (True, None, None, 410, '5cd2946afe6b0bcb689941fa', None, None, None),
        (True, None, None, 410, '5cf94043629526419e77b82d', None, None, None),
    ],
)
async def test_take_task_by_id(
        cbox,
        monkeypatch,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        assigned,
        params,
        data,
        expected_code,
        task_id,
        expected_get_history_kwargs,
        expected_get_comments_kwargs,
        expected_status_before_assign,
):
    mocked_chat_history = mock_chat_get_history({'messages': [], 'total': 0})
    mocked_st_comments = mock_st_get_comments([])
    mock_st_get_all_attachments()

    if assigned:
        await cbox.query(
            '/v1/tasks/{}/take'.format(task_id),
            params=params,
            headers={'Accept-Language': 'en'},
        )
    else:
        await cbox.post(
            '/v1/tasks/{}/take'.format(task_id),
            params=params,
            data=data,
            headers={'Accept-Language': 'en'},
        )

    assert cbox.status == expected_code
    if expected_code < 300:
        assert cbox.body_data['id'] == task_id
        assert cbox.body_data['next_request_timeout'] == 60
    if expected_get_history_kwargs:
        get_history_call = mocked_chat_history.calls[0]
        get_history_call['kwargs']['log_extra'] = None
        assert get_history_call['kwargs'] == expected_get_history_kwargs
    elif expected_get_comments_kwargs is not None:
        get_comments_call = mocked_st_comments.calls[0]
        assert get_comments_call['kwargs'] == expected_get_comments_kwargs
    task = await cbox.app.db.support_chatterbox.find_one(
        {'_id': bson.ObjectId(task_id)},
    )
    assert (
        task['meta_info'].get('status_before_assign')
        == expected_status_before_assign
    )


@pytest.mark.config(
    CHATTERBOX_LINES={
        'first': {'name': '1', 'autoreply': True},
        'second': {'name': '2', 'mode': 'offline'},
        'elite': {'name': '1 · Элитка', 'mode': 'online'},
    },
)
@pytest.mark.filldb(support_chatterbox='by_id')
@pytest.mark.parametrize(
    ('expected_code', 'task_id'),
    [
        (409, '5b2cae5cb2682a976914c297'),
        (409, '5b2cae5cb2682a976914c298'),
        (200, '5b2cae5cb2682a976914c299'),
        (409, '5cf94043629526419e77b82f'),
    ],
)
async def test_take_task_online_mode(
        cbox,
        monkeypatch,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        mock_chat_add_update,
        expected_code,
        task_id,
):
    mock_chat_get_history({'messages': [], 'total': 0})
    mock_st_get_comments([])
    mock_st_get_all_attachments()

    await cbox.post(
        '/v1/tasks/{}/take'.format(task_id),
        data={},
        headers={'Accept-Language': 'en'},
    )

    assert cbox.status == expected_code


@pytest.mark.filldb(support_chatterbox='by_id')
@pytest.mark.parametrize(
    ('data', 'expected_code', 'task_id'),
    [
        ({'force': True}, 200, '5cf94043629526419e77b82d'),
        ({'force': False}, 409, '5cd2946afe6b0bcb689941fa'),
        ({}, 409, '5cd2946afe6b0bcb689941fa'),
        ({'force': True}, 200, '5b2cae5cb2682a976914c296'),
    ],
)
async def test_take_task_by_id_inc_call(
        cbox,
        monkeypatch,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        mock_chat_add_update,
        data,
        expected_code,
        task_id,
):
    mock_chat_get_history({'messages': [], 'total': 0})
    mock_st_get_comments([])
    mock_st_get_all_attachments()

    await cbox.post(
        '/v1/tasks/{}/take'.format(task_id),
        data=data,
        headers={'Accept-Language': 'en'},
    )

    assert cbox.status == expected_code


@pytest.mark.config(
    CHATTERBOX_LINES={
        'urgent': {
            'id': 'urgent',
            'name': 'Ургент',
            'tags': ['клиент_urgent', 'подозрение_urgent'],
            'fields': {
                'ticket_subject': [
                    'Забыл вещи в машине',
                    'Яндекс.Такси Я забыл в такси свои вещи',
                ],
            },
            'priority': 1,
            'sort_order': 1,
        },
        'corp': {
            'name': 'Корп',
            'tags': ['Корпоративный_пользователь', 'Корп_пользователь'],
            'fields': {},
            'priority': 2,
            'sort_order': 1,
        },
        'vip': {
            'name': 'ВИП',
            'tags': [],
            'fields': {'user_type': ['vip-пользователь']},
            'priority': 3,
            'sort_order': -1,
        },
        'first': {
            'name': 'Первая линия',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
        },
        'driver_first': {
            'name': 'Первая водительская линия',
            'types': ['driver'],
            'tags': [],
            'fields': {},
            'priority': 5,
            'sort_order': 1,
        },
    },
)
@pytest.mark.parametrize(
    'lines, expected_code, expected_task_id',
    [
        (['first', 'urgent'], 200, 'urgent_task_id'),
        (['first'], 200, 'my_reopen_task_id'),
        (['third'], 404, ''),
        (['urgent', 'first'], 200, 'urgent_task_id'),
        (['corp'], 200, 'another_reopen_task_id'),
        (['urgent'], 200, 'urgent_task_id'),
        (['vip', 'urgent', 'first'], 200, 'urgent_task_id'),
        (['corp', 'vip'], 200, 'another_reopen_task_id'),
        ([], 404, ''),
        (['vip'], 200, 'vip_task_id'),
        (['first', 'driver_first'], 200, 'my_reopen_task_id'),
        (['driver_first'], 200, 'driver_task_id'),
    ],
)
@pytest.mark.filldb(support_chatterbox='lines')
async def test_take_task_with_lines(
        cbox, mock_chat_get_history, lines, expected_code, expected_task_id,
):
    mock_chat_get_history({'messages': [{'text': 'some message'}], 'total': 1})
    cbox.set_user('some_user')
    await cbox.post('/v1/tasks/take/', data={'lines': lines})
    assert cbox.status == expected_code
    if cbox.status == http.HTTPStatus.OK:
        task = cbox.body_data
        assert task['id'] == expected_task_id
        assert task['chat_messages'] == {
            'messages': [{'text': 'some message'}],
            'total': 1,
        }

    # double action must have same result
    await cbox.post('/v1/tasks/take/', data={'lines': lines})
    if cbox.status == http.HTTPStatus.OK:
        task = cbox.body_data
        assert task['id'] == expected_task_id
        assert task['chat_messages'] == {
            'messages': [{'text': 'some message'}],
            'total': 1,
        }


@pytest.mark.now('2018-10-01T00:00:00')
@pytest.mark.filldb(support_chatterbox='reopen')
async def test_take_superuser_reopen_task(cbox):
    """
    Test that superuser reopened task ignore reopened tasks delay.
    """
    supporter_state = await cbox.app.supporters_manager.get_supporter_state(
        login='user',
    )
    supporter_state = dataclasses.replace(
        supporter_state, db_status=constants.STATUS_ONLINE,
    )
    result = await cbox.app.tasks_manager.take(
        supporter_state=supporter_state, lines=['first'],
    )
    assert result['_id'] == 'superuser_reopen_task_id'


@pytest.mark.pgsql('chatterbox', files=['take_task_in_addition_pg.sql'])
async def test_take_task_in_addition(cbox, mock_chat_get_history):
    mock_chat_get_history({'messages': [{'text': 'some message'}], 'total': 1})
    await cbox.post('/v1/tasks/take/', data={'lines': ['first']})
    task = cbox.body_data
    assert task['history'][0]['in_addition']


@pytest.mark.config(
    CHATTERBOX_TASK_ALLOW_CHANGE_FIELDS={
        'user_phone': {
            'max_tries': 2,
            'permissions': {'add': ['add_phone'], 'update': ['upd_phone']},
            'label': 'fields.user_phone',
            'type': 'input',
            'validator': 'phone',
            'default': '+79990000000',
        },
        'phone_type': {
            'max_tries': 1,
            'permissions': {'add': ['restrict'], 'update': ['upd_phone_type']},
            'label': 'fields.phone_type',
            'type': 'select',
            'default': 'yandex',
            'options': {
                'uber': 'fields.phone_type_uber',
                'yandex': 'fields.phone_type_yandex',
            },
        },
        'order_id': {
            'max_tries': 0,
            'label': 'fields.order_id',
            'type': 'input',
            'validator': 'order',
        },
    },
)
@pytest.mark.parametrize(
    'meta_info, groups, allow_meta_change',
    [
        ({'order_id': 'new_order_id'}, [], []),
        (
            {},
            ['add_phone'],
            [
                {
                    'id': 'user_phone',
                    'label': 'Телефон пользователя',
                    'type': 'input',
                    'value': '+79990000000',
                },
            ],
        ),
        ({'user_phone': '+79999999999'}, ['add_phone'], []),
        (
            {'phone_type': 'uber'},
            ['upd_phone_type'],
            [
                {
                    'id': 'phone_type',
                    'label': 'Тип телефона',
                    'options': [
                        {'label': 'Убер', 'value': 'uber'},
                        {'label': 'Яндекс', 'value': 'yandex'},
                    ],
                    'type': 'select',
                    'value': 'uber',
                },
            ],
        ),
        (
            {'user_phone': '+79999999999', 'phone_type': 'uber'},
            ['upd_phone', 'upd_phone_type'],
            [
                {
                    'id': 'user_phone',
                    'label': 'Телефон пользователя',
                    'type': 'input',
                    'value': '+79999999999',
                },
                {
                    'id': 'phone_type',
                    'label': 'Тип телефона',
                    'options': [
                        {'label': 'Убер', 'value': 'uber'},
                        {'label': 'Яндекс', 'value': 'yandex'},
                    ],
                    'type': 'select',
                    'value': 'uber',
                },
            ],
        ),
    ],
)
@pytest.mark.translations(
    chatterbox={
        'fields.user_phone': {'ru': 'Телефон пользователя'},
        'fields.phone_type': {'ru': 'Тип телефона'},
        'fields.phone_type_uber': {'ru': 'Убер'},
        'fields.phone_type_yandex': {'ru': 'Яндекс'},
    },
)
@pytest.mark.now('2018-09-06T12:43:56')
async def test_take_task_meta_add(
        cbox,
        monkeypatch,
        mock_chat_get_history,
        patch_auth,
        meta_info,
        groups,
        allow_meta_change,
):
    patch_auth(superuser=False, groups=groups + [rights.CHATTERBOX_BASIC])

    async def take(self, supporter_state, lines, log_extra=None):
        return {
            '_id': 'newer_task_id',
            'external_id': 'some_user_chat_message_id',
            'type': 'chat',
            'line': 'urgent',
            'status': 'new',
            'created': datetime.datetime.now(),
            'updated': datetime.datetime.now(),
            'tags': [],
            'meta_info': meta_info,
            'inner_comments': [],
            'history': [],
        }

    mock_chat_get_history({'messages': [{'text': 'some message'}], 'total': 1})
    monkeypatch.setattr(
        'chatterbox.internal.tasks_manager._common.TasksManager.take', take,
    )
    await cbox.post('/v1/tasks/take/', data={'lines': ['first']})
    assert cbox.status == http.HTTPStatus.OK
    assert cbox.body_data['allow_meta_change'] == allow_meta_change


@pytest.mark.config(
    CHATTERBOX_LINES={
        'urgent': {
            'id': 'urgent',
            'name': 'Ургент',
            'tags': [],
            'fields': {},
            'priority': 1,
            'sort_order': 1,
        },
        'corp': {
            'id': 'corp',
            'name': 'Корп',
            'tags': [],
            'fields': {},
            'priority': 1,
            'sort_order': 1,
        },
        'vip': {
            'id': 'vip',
            'name': 'ВИП',
            'tags': [],
            'fields': {},
            'priority': 1,
            'sort_order': -1,
        },
        'center': {
            'id': 'center',
            'name': 'Центр',
            'tags': [],
            'fields': {},
            'priority': 2,
            'sort_order': 1,
        },
        'regions': {
            'id': 'regions',
            'name': 'Регионы',
            'tags': [],
            'fields': {},
            'priority': 2,
            'sort_order': 1,
        },
        'not_important': {
            'id': 'not_important',
            'name': 'Неважная линия',
            'tags': [],
            'fields': {},
            'priority': 3,
            'sort_order': -1,
        },
    },
)
@pytest.mark.parametrize(
    'lines, expected_code, expected_task_id',
    [
        (['urgent', 'corp'], 200, 'corp_task_id'),
        (['urgent', 'corp', 'vip'], 200, 'corp_task_id'),
        (['urgent', 'vip'], 200, 'urgent_task_id'),
        (['vip'], 200, 'vip_task_id'),
        (['not_important'], 200, 'notimportant_task_id_1'),
        (['regions', 'center'], 200, 'center_task_id'),
        (['not_important', 'regions'], 200, 'regions_task_id'),
    ],
)
@pytest.mark.filldb(support_chatterbox='same_priority')
async def test_take_with_same_priority(
        cbox, mock_chat_get_history, lines, expected_code, expected_task_id,
):
    mock_chat_get_history({'messages': [{'text': 'some message'}], 'total': 1})
    cbox.set_user('some_user')
    await cbox.post('/v1/tasks/take/', data={'lines': lines})
    assert cbox.status == expected_code
    if cbox.status == http.HTTPStatus.OK:
        task = cbox.body_data
        assert task['id'] == expected_task_id
        assert task['chat_messages'] == {
            'messages': [{'text': 'some message'}],
            'total': 1,
        }

    # double action must have same result
    await cbox.post('/v1/tasks/take/', data={'lines': lines})
    if cbox.status == http.HTTPStatus.OK:
        task = cbox.body_data
        assert task['id'] == expected_task_id
        assert task['chat_messages'] == {
            'messages': [{'text': 'some message'}],
            'total': 1,
        }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.parametrize(
    ('login', 'config_lines', 'expected_response'),
    (
        (
            'superuser',
            [],
            {'allow_call': False, 'allow_call_any_number': False},
        ),
        (
            'superuser',
            ['first'],
            {'allow_call': True, 'allow_call_any_number': True},
        ),
        (
            'user_with_sip_permitted',
            [],
            {'allow_call': False, 'allow_call_any_number': False},
        ),
        (
            'user_with_sip_permitted',
            ['first'],
            {'allow_call': True, 'allow_call_any_number': True},
        ),
        (
            'user_with_sip_not_permitted',
            [],
            {'allow_call': False, 'allow_call_any_number': False},
        ),
        (
            'user_with_sip_not_permitted',
            ['first'],
            {'allow_call': False, 'allow_call_any_number': False},
        ),
    ),
)
async def test_take_sip(
        cbox,
        patch_auth,
        patch_support_chat_get_history,
        login,
        config_lines,
        expected_response,
):
    patch_auth(login=login)
    patch_support_chat_get_history()
    cbox.app.config.CHATTERBOX_SIP_ENABLED_LINES = config_lines

    await cbox.post('/v1/tasks/take/', data={'lines': ['first']})
    assert cbox.status == 200
    assert cbox.body_data['sip_settings'] == expected_response


@pytest.mark.config(
    CHATTERBOX_LINES={'first': {'name': 'Первая линия', 'priority': 4}},
)
@pytest.mark.parametrize('status', tuple(constants.SUPPORT_STATUSES))
@pytest.mark.parametrize('sort_order', (pymongo.ASCENDING, pymongo.DESCENDING))
@pytest.mark.filldb(support_chatterbox='status_check')
async def test_take_order_by_status(
        cbox: conftest.CboxWrap,
        mock_chat_get_history,
        status: str,
        sort_order: int,
):
    cbox.app.config.CHATTERBOX_LINES['first']['sort_order'] = sort_order
    mock_chat_get_history({'messages': [{'text': 'some message'}]})

    db_status, in_additional = get_db_status(status)
    async with cbox.app.pg_master_pool.acquire() as conn:
        await conn.execute(
            'UPDATE chatterbox.online_supporters '
            'SET status = $1, in_additional = $2 '
            'WHERE supporter_login = $3',
            db_status,
            in_additional,
            'superuser',
        )

    await cbox.post(
        '/v1/tasks/take/',
        data={'lines': ['first']},
        headers={'Accept-Language': 'en'},
    )
    assert cbox.status == http.HTTPStatus.OK

    expected_sort_order = sort_order
    if db_status == constants.STATUS_ONLINE_REVERSED:
        expected_sort_order *= -1

    if expected_sort_order == pymongo.DESCENDING:
        assert cbox.body_data['id'] == 'new_task_in_first_line'
    else:
        assert cbox.body_data['id'] == 'old_task_in_first_line'


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
async def test_take_not_acceptable(cbox, mock_check_tasks_limits, locale):
    check_tasks_limits = mock_check_tasks_limits(10)

    await cbox.post(
        '/v1/tasks/take/',
        data={'lines': ['first']},
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
async def test_take_by_id_not_acceptable(
        cbox, mock_check_tasks_limits, locale,
):
    check_tasks_limits = mock_check_tasks_limits(10)

    await cbox.post(
        '/v1/tasks/5cf94043629526419e77b82d/take',
        data={'lines': ['first']},
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


@pytest.mark.filldb(support_chatterbox='empty_tasks')
@pytest.mark.config(CHATTERBOX_TAKE_LANG_FILTRATION_ENABLED=True)
@pytest.mark.translations(
    chatterbox={
        'errors.take_tasks_not_found': {
            'ru': 'По состоянию на {time_string} нет заданий.',
            'en': 'There are no tasks now: {time_string}.',
        },
        'errors.take_not_found_available_languages': {
            'ru': 'Доступные вам языки: {available_languages}.',
            'en': 'Languages available to you: {available_languages}.',
        },
        'errors.take_not_found_ignored_lines': {
            'ru': (
                'Некоторые линии, указанные вами, недоступны: {ignored_lines}.'
            ),
            'en': 'Some lines are not available: {ignored_lines}.',
        },
    },
)
@pytest.mark.parametrize(
    'locale, data, login, expected_body',
    [
        (
            'en',
            {'lines': ['first']},
            'superuser2',
            {
                'status': 'not_found',
                'message': (
                    'There are no tasks now: 12:30 26.07.2019.\n'
                    'Languages available to you: en, ru.'
                ),
            },
        ),
        (
            'ru',
            {'lines': ['first', 'unknown']},
            'superuser2',
            {
                'status': 'not_found',
                'message': (
                    'По состоянию на 12:30 26.07.2019 нет заданий.\n'
                    'Доступные вам языки: en, ru.\n'
                    'Некоторые линии, указанные вами, недоступны: unknown.'
                ),
            },
        ),
        (
            'ru',
            {'lines': ['first', 'unknown']},
            'superuser3',
            {
                'status': 'not_found',
                'message': (
                    'По состоянию на 12:30 26.07.2019 нет заданий.\n'
                    'Некоторые линии, указанные вами, недоступны: unknown.'
                ),
            },
        ),
        (
            'en',
            {'lines': []},
            'superuser3',
            {
                'status': 'not_found',
                'message': 'There are no tasks now: 12:30 26.07.2019.',
            },
        ),
    ],
)
@pytest.mark.now('2019-07-26T12:30:00+0')
async def test_take_not_found_message(
        cbox, patch_auth, locale, data, login, expected_body,
):
    patch_auth(login=login, superuser=True)

    await cbox.post(
        '/v1/tasks/take/', data=data, headers={'Accept-Language': locale},
    )
    assert cbox.status == http.HTTPStatus.NOT_FOUND
    assert cbox.body_data == expected_body


@pytest.mark.translations(
    chatterbox={
        'errors.compendium_take_in_additional': {
            'ru': 'Compendium заблокировал take в доп.',
        },
    },
)
async def test_take_in_additional_not_permitted(
        cbox: conftest.CboxWrap, patch_auth,
):
    patch_auth(login='user_with_in_additional_not_permitted')

    await cbox.post(
        '/v1/tasks/take/',
        data={'lines': ['first']},
        headers={'Accept-Language': 'ru'},
    )
    assert cbox.status == 403
    assert cbox.body_data == {
        'code': 'forbidden',
        'message': 'Compendium заблокировал take в доп.',
        'status': 'error',
    }


@pytest.mark.translations(
    chatterbox={
        'errors.compendium_take_in_additional': {
            'ru': 'Compendium заблокировал take в доп.',
        },
    },
)
async def test_take_in_progress_task_in_additional_not_permitted(
        cbox: conftest.CboxWrap, patch_auth, mock_chat_get_history,
):
    patch_auth(login='user_with_in_additional_not_permitted_task_assigned')
    mock_chat_get_history({'messages': [{'text': 'some message'}], 'total': 1})

    await cbox.post(
        '/v1/tasks/take/',
        data={'lines': ['first']},
        headers={'Accept-Language': 'ru'},
    )
    assert cbox.status == 200
    assert cbox.body_data['id'] == '5cf94043629526419e77b90e'


@pytest.mark.translations(
    chatterbox={
        'errors.compendium_take_off_shift': {
            'ru': 'Compendium заблокировал take вне смены',
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
async def test_take_off_shift_tickets_disabled(
        cbox: conftest.CboxWrap,
        patch_auth,
        mock_chat_get_history,
        expected_status,
):
    patch_auth(login='user_with_off_shift_tickets_disabled')
    mock_chat_get_history({'messages': [{'text': 'some message'}], 'total': 1})

    await cbox.post(
        '/v1/tasks/take/',
        data={'lines': ['first']},
        headers={'Accept-Language': 'ru'},
    )
    assert cbox.status == expected_status
    if expected_status == 403:
        assert cbox.body_data == {
            'code': 'forbidden',
            'message': 'Compendium заблокировал take вне смены',
            'status': 'error',
        }


@pytest.mark.config(
    CHATTERBOX_ACTIONS_FIELDS={
        'forward': [
            {'id': 'hidden_comment', 'type': 'string', 'required': False},
            {'id': 'tags', 'type': 'array', 'required': False},
        ],
        'close': [
            {'id': 'hidden_comment', 'type': 'string', 'required': True},
            {'id': 'tags', 'type': 'array', 'required': False},
            {'id': 'macro_id', 'type': 'array', 'required': False},
        ],
        'dismiss': [
            {'id': 'comment', 'type': 'string', 'required': True},
            {'id': 'macro_id', 'type': 'string', 'required': False},
        ],
    },
    CHATTERBOX_LINES_ACTIONS_FIELDS={
        '__default__': {'required_fields': {'macro_id': ['comment', 'close']}},
        'second': {'required_fields': {'tags': ['close']}},
    },
)
@pytest.mark.now('2018-09-06T12:43:56')
async def test_take_action_fields(
        cbox: conftest.CboxWrap, mock_chat_get_history,
):
    mock_chat_get_history({'messages': [{'text': 'some message'}], 'total': 1})

    await cbox.post(
        '/v1/tasks/take/',
        data={'lines': ['first']},
        headers={'Accept-Language': 'ru'},
    )
    assert cbox.status == 200
    assert cbox.body_data['id'] == 'in_progress_task_id'
    assert cbox.body_data['actions'] == [
        {
            'action_id': 'close',
            'title': 'Выполнен',
            'query_params': {},
            'view': {'position': 'footer', 'type': 'radio'},
            'body_fields': [
                {
                    'id': 'hidden_comment',
                    'type': 'string',
                    'checks': ['not-empty'],
                },
                {'id': 'tags', 'type': 'array', 'checks': []},
                {'id': 'macro_id', 'type': 'array', 'checks': ['not-empty']},
            ],
        },
        {
            'action_id': 'comment',
            'title': 'В ожидании',
            'query_params': {},
            'view': {'position': 'footer', 'type': 'radio'},
        },
        {
            'action_id': 'communicate',
            'query_params': {},
            'title': 'Только отправить',
            'view': {'position': 'footer', 'type': 'radio'},
        },
        {
            'action_id': 'defer',
            'title': '1h',
            'query_params': {'reopen_at': '2018-09-06T13:43:56+0000'},
            'view': {'position': 'footer', 'type': 'radio'},
        },
        {
            'action_id': 'defer',
            'title': '12h',
            'query_params': {'reopen_at': '2018-09-07T00:43:56+0000'},
            'view': {'position': 'footer', 'type': 'radio'},
        },
        {
            'action_id': 'dismiss',
            'query_params': {'chatterbox_button': 'chatterbox_nto'},
            'title': '🤐 НТО',
            'view': {'position': 'statusbar', 'type': 'button'},
            'body_fields': [
                {'id': 'comment', 'type': 'string', 'checks': ['not-empty']},
                {'id': 'macro_id', 'type': 'string', 'checks': []},
            ],
        },
        {
            'action_id': 'export',
            'query_params': {'chatterbox_button': 'chatterbox_zen'},
            'title': '✍️ Ручное',
            'view': {'position': 'statusbar', 'type': 'button'},
        },
        {
            'action_id': 'export',
            'query_params': {'chatterbox_button': 'chatterbox_urgent'},
            'title': '💣 Ургент',
            'view': {'position': 'statusbar', 'type': 'button'},
        },
        {
            'action_id': 'export',
            'query_params': {'chatterbox_button': 'chatterbox_lost'},
            'title': '🔑 Потеряшки',
            'view': {'position': 'statusbar', 'type': 'button'},
        },
    ]


@pytest.mark.filldb(support_chatterbox='by_id')
@pytest.mark.config(
    CHATTERBOX_PERSONAL={
        'enabled': True,
        'personal_fields': {
            'user_phone': 'phones',
            'user_email': 'emails',
            'driver_license': 'driver_licenses',
            'driver_phone': 'phones',
            'park_phone': 'phones',
            'park_email': 'emails',
            'num_from': 'phones',
            'num_to': 'phones',
        },
    },
)
@pytest.mark.parametrize(
    ('expected_code', 'task_id', 'expected_meta'),
    [
        (
            200,
            '5b2cae5cb2682a976914c295',
            {
                'calls': [
                    {
                        'answered_at': '2019-01-01T11:22:33Z',
                        'completed_at': None,
                        'created_at': '2018-01-01T11:22:33Z',
                        'direction': 'outgoing',
                        'error': None,
                        'hangup_disposition': None,
                        'id': 'id',
                        'is_synced': True,
                        'num_from': '+7900',
                        'num_from_pd_id': 'phone_pd_id_9',
                        'num_to': '+7901',
                        'num_to_pd_id': 'phone_pd_id_10',
                        'provider_id': 'provider_id',
                        'record_urls': [],
                        'ringing_at': '2019-01-01T11:22:33Z',
                        'status_completed': 'answered',
                        'user_id': 'user_id',
                    },
                ],
                'driver_license': 'some_driver_license',
                'driver_license_pd_id': 'driver_license_pd_id_1',
                'user_phone': '+79999999999',
                'user_phone_pd_id': 'phone_pd_id_1',
            },
        ),
    ],
)
async def test_take_task_personal_meta(
        cbox,
        monkeypatch,
        mock_chat_get_history,
        mock_st_get_ticket,
        mock_st_get_comments,
        mock_st_get_all_attachments,
        mock_chat_add_update,
        mock_personal,
        expected_code,
        task_id,
        expected_meta,
):
    mock_chat_get_history({'messages': [], 'total': 0})
    mock_st_get_comments([])
    mock_st_get_all_attachments()

    await cbox.post(
        '/v1/tasks/{}/take'.format(task_id),
        data={'force': True},
        headers={'Accept-Language': 'en'},
    )

    assert cbox.status == expected_code
    task = cbox.body_data
    assert task['meta_info'] == expected_meta
