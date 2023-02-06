# pylint: disable=too-many-lines, too-many-arguments, redefined-outer-name
# pylint: disable=unused-variable, too-many-locals
import datetime
import http

import pytest
import pytz

from chatterbox.internal.tasks_manager import _private

NOW = datetime.datetime(2019, 8, 14, 10, tzinfo=pytz.utc)
LAST_UPDATED = datetime.datetime(2019, 8, 13, 11, 49, 25, tzinfo=pytz.utc)


@pytest.fixture(autouse=True)
def set_test_user(patch_auth):
    patch_auth(login='test_user')


@pytest.mark.config(
    CHATTERBOX_CHANGE_LINE_STATUSES={'in_progress': 'forwarded'},
    CHATTERBOX_LINES={
        'second': {'types': ['client']},
        'first': {'types': ['client']},
    },
)
@pytest.mark.parametrize(
    'task_id, action, params, data',
    [
        ('5b2cae5cb2682a976914c2a1', 'forward', {'line': 'second'}, {}),
        ('5b2cae5cb2682a976914c2a1', 'close', {}, {'comment': 'test'}),
        ('5b2cae5cb2682a976914c2a1', 'communicate', {}, {'comment': 'test'}),
        (
            '5b2cae5cb2682a976914c2a1',
            'defer',
            {'reopen_at': '2018-06-15T15:34:00+0000'},
            {'macro_id': 'some_macro_id'},
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'dismiss',
            {
                'chatterbox_button': 'chatterbox_nto',
                'additional_tag': 'nto_tag',
            },
            {'tags': ['double tag', 'double tag']},
        ),
        (
            '5b2cae5cb2682a976914c2a1',
            'take',
            {},
            {'lines': ['first'], 'force': True},
        ),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_update_last_action(
        cbox,
        task_id,
        action,
        params,
        data,
        mock_chat_add_update,
        mock_chat_get_history,
):
    mock_chat_get_history({'messages': [], 'total': 0})
    await cbox.post(
        '/v1/tasks/%s/%s' % (task_id, action), params=params, data=data,
    )
    assert cbox.status == http.HTTPStatus.OK

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.online_supporters '
            'WHERE supporter_login = $1',
            'test_user',
        )
    assert len(result) == 1
    assert result[0]['last_action_ts'] == NOW


@pytest.mark.now(NOW.isoformat())
async def test_take_update_last_action(
        cbox, mock_chat_add_update, mock_chat_get_history,
):
    mock_chat_get_history({'messages': [], 'total': 0})
    await cbox.post('/v1/tasks/take/', data={'lines': ['first']})
    assert cbox.status == http.HTTPStatus.OK

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.online_supporters '
            'WHERE supporter_login = $1',
            'test_user',
        )
    assert len(result) == 1
    assert result[0]['last_action_ts'] == NOW


@pytest.mark.config(
    CHATTERBOX_CHANGE_LINE_STATUSES={'in_progress': 'forwarded'},
)
@pytest.mark.parametrize(
    'login, action, updated',
    [
        ('superuser', 'forward', False),
        ('test_user', 'forward', True),
        ('superuser', 'comment', False),
        ('test_user', 'comment', True),
        ('superuser', 'autoreply', False),
        ('test_user', 'reopen', False),
        ('test_user', 'export', True),
        ('test_user', 'take', True),
        ('test_user', 'update_meta', False),
        ('test_user', 'take', True),
    ],
)
@pytest.mark.now(NOW.isoformat())
async def test_private_set_last_action(cbox, login, action, updated):

    await _private.set_last_action_ts(
        cbox.app.sqlt, cbox.app.pg_master_pool, login, action,
    )

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT * FROM chatterbox.online_supporters '
            'WHERE supporter_login = $1',
            'test_user',
        )
    assert len(result) == 1
    if updated:
        assert result[0]['last_action_ts'] == NOW
    else:
        assert result[0]['last_action_ts'] == LAST_UPDATED
