import datetime
from typing import Dict
from typing import Optional

import bson
import pytest

from test_chatterbox import plugins as conftest


async def save_task(
        cbox: conftest.CboxWrap,
        task_id: bson.ObjectId,
        is_task_on_user: bool,
        login: Optional[str],
        status: str,
        language: Optional[str],
) -> None:
    created_delta = datetime.timedelta(minutes=40)
    updated_delta = datetime.timedelta(minutes=30)
    data = {
        'external_id': 'some_user_chat_message_id_2',
        'type': 'chat',
        'line': 'second',
        'status': status,
        'created': datetime.datetime.utcnow() - created_delta,
        'updated': datetime.datetime.utcnow() - updated_delta,
        'tags': [],
        'history': [],
    }
    if is_task_on_user:
        data['support_admin'] = login
    if language:
        data['meta_info.task_language'] = language

    result = await cbox.db.support_chatterbox.find_one_and_update(
        filter={'_id': task_id},
        update={'$set': data},
        upsert=True,
        return_document=True,
    )
    return result


@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_take_in_progress_priority(cbox: conftest.CboxWrap):
    supporter_state = await cbox.app.supporters_manager.get_supporter_state(
        login='superuser',
    )
    assigned_task = await cbox.app.tasks_manager.take(
        supporter_state, ['first'],
    )
    assert assigned_task['_id'] == bson.ObjectId('5b2cae5cb2682a976914c2a2')


@pytest.mark.config(
    CHATTERBOX_TAKE_LANG_FILTRATION_ENABLED=True,
    CHATTERBOX_LINES={
        'second': {
            'name': 'Вторая линия',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
            'autoreply': True,
        },
    },
)
@pytest.mark.parametrize(
    ('task_params', 'is_task_on_user', 'is_task_found_for_users'),
    (
        # Task on supporter in in_progress status
        (
            {'status': 'in_progress', 'language': 'ru'},
            True,
            {
                'user_with_ru_lang': True,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        (
            {'status': 'in_progress', 'language': 'en'},
            True,
            {
                'user_with_ru_lang': True,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        (
            {'status': 'in_progress', 'language': None},
            True,
            {
                'user_with_ru_lang': True,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        # Task on supporter in reopen status
        (
            {'status': 'reopened', 'language': 'ru'},
            True,
            {
                'user_with_ru_lang': True,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        (
            {'status': 'reopened', 'language': 'en'},
            True,
            {
                'user_with_ru_lang': True,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        (
            {'status': 'reopened', 'language': None},
            True,
            {
                'user_with_ru_lang': True,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        # Task not on supporter in reopen status
        (
            {'status': 'reopened', 'language': 'ru'},
            False,
            {
                'user_with_ru_lang': True,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        (
            {'status': 'reopened', 'language': 'en'},
            False,
            {
                'user_with_ru_lang': False,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        (
            {'status': 'reopened', 'language': None},
            False,
            {
                'user_with_ru_lang': False,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        # Task not on supporter in forwarded status
        (
            {'status': 'forwarded', 'language': 'ru'},
            False,
            {
                'user_with_ru_lang': True,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        (
            {'status': 'forwarded', 'language': 'en'},
            False,
            {
                'user_with_ru_lang': False,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        (
            {'status': 'forwarded', 'language': None},
            False,
            {
                'user_with_ru_lang': False,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        # Task not on supporter in new status
        (
            {'status': 'new', 'language': 'ru'},
            False,
            {
                'user_with_ru_lang': True,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        (
            {'status': 'new', 'language': 'en'},
            False,
            {
                'user_with_ru_lang': False,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
        (
            {'status': 'new', 'language': None},
            False,
            {
                'user_with_ru_lang': False,
                'user_with_without_lang': True,
                'user_with_none_lang': True,
                'user_without_profile': True,
            },
        ),
    ),
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_take_task_language_filter(
        cbox: conftest.CboxWrap,
        task_params: dict,
        is_task_on_user: bool,
        is_task_found_for_users: Dict[str, bool],
):
    task_id = bson.ObjectId('5b2cae5cb2682a976914c2a3')

    for user, is_found in is_task_found_for_users.items():
        await save_task(
            cbox,
            task_id=task_id,
            is_task_on_user=is_task_on_user,
            login=user,
            **task_params,
        )

        supporter_state = (
            await cbox.app.supporters_manager.get_supporter_state(login=user)
        )

        assigned_task = await cbox.app.tasks_manager.take(
            supporter_state, ['second'],
        )
        if is_found:
            assert assigned_task['_id'] == task_id
        else:
            assert assigned_task is None


@pytest.mark.config(
    CHATTERBOX_LINES={
        'second': {
            'name': 'Вторая линия',
            'types': ['client'],
            'tags': [],
            'fields': {},
            'priority': 4,
            'sort_order': 1,
            'autoreply': True,
        },
    },
)
@pytest.mark.parametrize('filter_by_lang_enabled', (True, False))
@pytest.mark.now('2019-01-01T12:00:00+0000')
async def test_take_task_language_filter_config(
        cbox: conftest.CboxWrap, filter_by_lang_enabled: bool,
):
    config = cbox.app.config
    config.CHATTERBOX_TAKE_LANG_FILTRATION_ENABLED = filter_by_lang_enabled
    task_params = {
        'task_id': bson.ObjectId('5b2cae5cb2682a976914c2a3'),
        'status': 'reopened',
        'language': 'en',
        'is_task_on_user': False,
        'login': 'user_with_ru_lang',
    }

    await save_task(cbox, **task_params)
    supporter_state = await cbox.app.supporters_manager.get_supporter_state(
        login=task_params['login'],
    )
    assigned_task = await cbox.app.tasks_manager.take(
        supporter_state, ['second'],
    )
    if filter_by_lang_enabled:
        assert assigned_task is None
    else:
        assert assigned_task['_id'] == task_params['task_id']


@pytest.mark.config(
    CHATTERBOX_LINES={
        'for_skip': {
            'name': 'Тест скипа',
            'types': ['client'],
            'priority': 4,
            'sort_order': 1,
        },
    },
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.parametrize(
    'login, no_tasks', [('skipper', True), ('not_skipper', False)],
)
async def test_dont_take_skipped(cbox, patch_auth, login, no_tasks):
    patch_auth(login=login, superuser=False)
    supporter_state = await cbox.app.supporters_manager.get_supporter_state(
        login=login,
    )
    assigned_task = await cbox.app.tasks_manager.take(
        supporter_state, ['for_skip'],
    )

    if no_tasks:
        assert not assigned_task
    else:
        assert assigned_task


@pytest.mark.config(
    CHATTERBOX_LINES_WITHOUT_REOPEN_DELAY=[
        'line_without_delay_1',
        'line_without_delay_2',
    ],
    CHATTERBOX_LINES={
        'line_without_delay_1': {
            'name': 'Without delay',
            'types': ['client'],
            'priority': 1,
            'sort_order': 1,
        },
        'line_without_delay_2': {
            'name': 'Without delay',
            'types': ['client'],
            'priority': 1,
            'sort_order': 1,
        },
        'line_with_delay_1': {
            'name': 'With delay',
            'types': ['client'],
            'priority': 1,
            'sort_order': 1,
        },
        'line_with_delay_2': {
            'name': 'With delay',
            'types': ['client'],
            'priority': 1,
            'sort_order': 1,
        },
        'line_with_delay_3': {
            'name': 'With delay',
            'types': ['client'],
            'priority': 2,
            'sort_order': 1,
        },
    },
)
@pytest.mark.now('2019-01-01T12:00:00+0000')
@pytest.mark.parametrize(
    'login, lines, expected_task_id',
    [
        (
            'user_without_delay',
            ['line_without_delay_1', 'line_without_delay_2'],
            bson.ObjectId('5e7df39e779fb308e06fa3a3'),
        ),
        (
            'user_without_delay',
            ['line_without_delay_1', 'line_with_delay_3'],
            bson.ObjectId('5e7df39e779fb308e06fa3a3'),
        ),
        (
            'user_with_delay_1',
            ['line_without_delay_1', 'line_with_delay_1'],
            None,
        ),
        ('user_with_delay_2', ['line_with_delay_2'], None),
    ],
)
async def test_take_without_delay(
        cbox, patch_auth, login, lines, expected_task_id,
):
    patch_auth(login=login, superuser=False)
    supporter_state = await cbox.app.supporters_manager.get_supporter_state(
        login=login,
    )
    assigned_task = await cbox.app.tasks_manager.take(supporter_state, lines)

    if not expected_task_id:
        assert not assigned_task
    else:
        assert assigned_task['_id'] == expected_task_id


@pytest.mark.config(
    CHATTERBOX_LINES_WITHOUT_REOPEN_DELAY=['reopen_1', 'reopen_2'],
    CHATTERBOX_TAKE_DELAY={'reopened': 5},
    CHATTERBOX_LINES={
        'reopen_1': {'name': 'reopen_1', 'priority': 1, 'sort_order': 1},
        'reopen_2': {'name': 'reopen_2', 'priority': 1, 'sort_order': 1},
    },
)
@pytest.mark.parametrize(
    'login, lines, expected_task_id',
    [
        pytest.param(
            'user',
            ['reopen_1'],
            bson.ObjectId('5e7df39e779fb308e06fa3a4'),
            marks=[pytest.mark.now('2019-01-01T11:46:00.000Z')],
        ),
        pytest.param(
            'user',
            ['reopen_1'],
            None,
            marks=[pytest.mark.now('2019-01-01T11:45:04.000Z')],
        ),
        pytest.param(
            'reopened_user',
            ['reopen_2'],
            bson.ObjectId('5e7df39e779fb308e06fa3a5'),
            marks=[pytest.mark.now('2019-01-01T11:46:00.000Z')],
        ),
        pytest.param(
            'reopened_user',
            ['reopen_2'],
            None,
            marks=[pytest.mark.now('2019-01-01T11:45:04.000Z')],
        ),
    ],
)
async def test_take_with_support_take_delay(
        cbox, patch_auth, login, lines, expected_task_id,
):
    patch_auth(login=login, superuser=False)
    supporter_state = await cbox.app.supporters_manager.get_supporter_state(
        login=login,
    )
    assigned_task = await cbox.app.tasks_manager.take(supporter_state, lines)

    if not expected_task_id:
        assert not assigned_task
    else:
        assert assigned_task['_id'] == expected_task_id


@pytest.mark.config(
    CHATTERBOX_LINES={
        'custom_sort_order': {
            'name': 'custom_sort_order',
            'priority': 1,
            'sort_order': 1,
            'sort_config': [
                {'status': 'new', 'sort_by': 'updated'},
                {'status': 'reopened', 'sort_by': 'created'},
                {'status': 'forwarded', 'sort_by': 'created'},
            ],
        },
        'default_sort_order': {
            'name': 'custom_sort_order',
            'priority': 1,
            'sort_order': 1,
        },
    },
)
@pytest.mark.parametrize(
    'login, lines, expected_task_ids',
    [
        pytest.param(
            'user',
            ['custom_sort_order'],
            [
                bson.ObjectId('60d42aceb1eca8d75c8cba5f'),
                bson.ObjectId('60d42a6babd9a2cd15936b52'),
                bson.ObjectId('60d48c631ac8bbc112f5cb63'),
                bson.ObjectId('60d42a5be83fa3186472b943'),
            ],
        ),
        pytest.param(
            'user',
            ['default_sort_order'],
            [
                bson.ObjectId('60d48418a1ce12b4ab895101'),
                bson.ObjectId('60d4840cc6cfea72da7c6a74'),
                bson.ObjectId('60d48420018e14e76464c2d4'),
            ],
        ),
    ],
)
async def test_sort_by_status(
        cbox, patch_auth, login, lines, expected_task_ids,
):
    patch_auth(login=login)
    supporter_state = await cbox.app.supporters_manager.get_supporter_state(
        login=login,
    )

    for expected_task_id in expected_task_ids:
        assigned_task = await cbox.app.tasks_manager.take(
            supporter_state, lines,
        )

        if not expected_task_id:
            assert not assigned_task
        else:
            await cbox.db.support_chatterbox.find_one_and_update(
                filter={'_id': assigned_task['_id']},
                update={'$set': {'status': 'ok'}},
                upsert=True,
                return_document=True,
            )
            assert assigned_task['_id'] == expected_task_id
