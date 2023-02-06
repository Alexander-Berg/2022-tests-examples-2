import asyncio
import datetime
from typing import Callable

import pytest
import pytz

from taxi.maintenance import run

from chatterbox.crontasks import update_supporters_by_compendium
from test_chatterbox import plugins as conftest


SHIFT_START = '2018-08-01T12:59:23.231000+00:00'
SHIFT_FINISH = '2018-08-01T12:59:23.231000+00:00'


@pytest.mark.parametrize(
    'data_source',
    (
        pytest.param(
            'compendium',
            marks=pytest.mark.config(
                CHATTERBOX_UPDATE_SUPPORTERS_FROM_AGENT=False,
            ),
        ),
        pytest.param(
            'agent',
            marks=pytest.mark.config(
                CHATTERBOX_UPDATE_SUPPORTERS_FROM_AGENT=True,
            ),
        ),
    ),
)
@pytest.mark.config(CHATTERBOX_UPDATE_SUPPORTERS_CHUNK_SIZE=10)
@pytest.mark.now('2019-01-01T00:00:00')
async def test_compendium_cron(
        patch_compendium_get_info: Callable,
        patch_agent_get_info: Callable,
        cbox_context: run.StuffContext,
        cbox: conftest.CboxWrap,
        loop: asyncio.AbstractEventLoop,
        data_source: str,
):
    utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    if data_source == 'compendium':
        patch_compendium_get_info(
            response={
                'user_1': {
                    'quality': 11.1,
                    'languages': ['ru', 'en'],
                    'csat': 66.6,
                    'piece': False,
                    'shift_finish': SHIFT_START,
                    'shift_start': SHIFT_FINISH,
                    'max_tickets_per_shift': 1000,
                    'in_additional_permitted': True,
                    'off_shift_tickets_disabled': True,
                    'max_chats_chatterbox': 5,
                    'assigned_lines': ['line_1', 'line_2'],
                    'can_choose_from_assigned_lines': True,
                    'can_choose_except_assigned_lines': True,
                },
                'user_without_assigned_lines_info': {
                    'quality': 11.1,
                    'languages': ['ru', 'en'],
                    'csat': 66.6,
                    'piece': False,
                    'shift_finish': SHIFT_START,
                    'shift_start': SHIFT_FINISH,
                    'max_tickets_per_shift': 1000,
                    'in_additional_permitted': True,
                    'off_shift_tickets_disabled': True,
                    'max_chats_chatterbox': 5,
                },
            },
        )
    elif data_source == 'agent':
        patch_agent_get_info(
            response={
                'limit': 10,
                'page': 0,
                'total': 2,
                'settings': [
                    {
                        'supporter_login': 'user_1',
                        'quality': 11.1,
                        'languages': ['ru', 'en'],
                        'csat': 66.6,
                        'piece': False,
                        'shift_finish': SHIFT_START,
                        'shift_start': SHIFT_FINISH,
                        'max_tickets_per_shift': 1000,
                        'in_additional_permitted': True,
                        'dis_tickets_off_shift': True,
                        'max_chats_chatterbox': 5,
                        'assigned_lines': ['line_1', 'line_2'],
                        'can_choose_from_assigned_lines': True,
                        'can_choose_except_assigned_lines': True,
                        'block_tickets': False,
                        'reason_block_tickets': [],
                    },
                    {
                        'supporter_login': 'user_without_assigned_lines_info',
                        'quality': 11.1,
                        'languages': ['ru', 'en'],
                        'csat': 66.6,
                        'piece': False,
                        'shift_finish': SHIFT_START,
                        'shift_start': SHIFT_FINISH,
                        'max_tickets_per_shift': 1000,
                        'in_additional_permitted': True,
                        'dis_tickets_off_shift': True,
                        'max_chats_chatterbox': 5,
                        'block_tickets': False,
                        'reason_block_tickets': [],
                        'assigned_lines': [],
                        'can_choose_from_assigned_lines': False,
                        'can_choose_except_assigned_lines': True,
                    },
                ],
            },
        )

    await update_supporters_by_compendium.do_stuff(cbox_context, loop)

    async with cbox.app.pg_master_pool.acquire() as conn:
        records = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_profile '
            'ORDER BY supporter_login',
        )

    supporters = [dict(record) for record in records]
    assert supporters == [
        {
            'csat': 66.6,
            'languages': ['ru', 'en'],
            'shift_finish': datetime.datetime(
                2018, 8, 1, 12, 59, 23, 231000, tzinfo=datetime.timezone.utc,
            ),
            'shift_start': datetime.datetime(
                2018, 8, 1, 12, 59, 23, 231000, tzinfo=datetime.timezone.utc,
            ),
            'is_piecework': False,
            'quality': 11.1,
            'supporter_login': 'user_1',
            'updated': utc_now,
            'max_tickets_per_shift': 1000,
            'in_additional_permitted': True,
            'off_shift_tickets_disabled': True,
            'max_chats': 5,
            'assigned_lines': ['line_1', 'line_2'],
            'can_choose_from_assigned_lines': True,
            'can_choose_except_assigned_lines': True,
        },
        {
            'csat': 66.6,
            'languages': ['ru', 'en'],
            'shift_finish': datetime.datetime(
                2018, 8, 1, 12, 59, 23, 231000, tzinfo=datetime.timezone.utc,
            ),
            'shift_start': datetime.datetime(
                2018, 8, 1, 12, 59, 23, 231000, tzinfo=datetime.timezone.utc,
            ),
            'is_piecework': False,
            'quality': 11.1,
            'supporter_login': 'user_without_assigned_lines_info',
            'updated': utc_now,
            'max_tickets_per_shift': 1000,
            'in_additional_permitted': True,
            'off_shift_tickets_disabled': True,
            'max_chats': 5,
            'assigned_lines': [],
            'can_choose_from_assigned_lines': False,
            'can_choose_except_assigned_lines': True,
        },
    ]


@pytest.mark.config(
    CHATTERBOX_LINES={
        'offline_line': {'mode': 'offline'},
        'online_line': {'mode': 'online'},
        'online_line_2': {'mode': 'online'},
    },
)
async def test_compendium_cron_validation(
        patch_compendium_get_info: Callable,
        cbox_context: run.StuffContext,
        cbox: conftest.CboxWrap,
        loop: asyncio.AbstractEventLoop,
):
    utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    patch_compendium_get_info(
        response={
            'user_invalid_piece': {
                'quality': 11.1,
                'languages': ['ru', 'en'],
                'csat': 66.6,
                'piece': 2,
                'shift_finish': SHIFT_START,
                'shift_start': SHIFT_FINISH,
            },
            'user_invalid_csat': {
                'quality': 11.1,
                'languages': ['ru', 'en'],
                'csat': '66.6.8',
                'piece': True,
                'shift_finish': SHIFT_START,
                'shift_start': SHIFT_FINISH,
            },
            'user_invalid_quality': {
                'quality': '11.1a',
                'languages': ['ru', 'en'],
                'csat': 66.6,
                'piece': True,
                'shift_finish': SHIFT_START,
                'shift_start': SHIFT_FINISH,
            },
            'user_invalid_lang': {
                'quality': 11.1,
                'languages': ['ru', 1],
                'csat': 66.6,
                'piece': True,
                'shift_finish': SHIFT_START,
                'shift_start': SHIFT_FINISH,
            },
            'user_bad_shift_period': {
                'quality': 11.1,
                'languages': ['ru', 'en'],
                'csat': 66.6,
                'piece': False,
                'shift_start': SHIFT_FINISH,
            },
            'user_need_shift_info': {
                'quality': 11.1,
                'languages': ['ru', 'en'],
                'csat': 66.6,
                'piece': False,
                'max_tickets_per_shift': 5,
            },
            'user_invalid_assigned_lines': {
                'quality': 11.1,
                'languages': ['ru'],
                'csat': 66.6,
                'piece': True,
                'shift_finish': SHIFT_START,
                'shift_start': SHIFT_FINISH,
                'assigned_lines': ['line_12', 32],
            },
            'user_invalid_can_choose_from_assigned_lines': {
                'quality': 11.1,
                'languages': ['ru'],
                'csat': 66.6,
                'piece': True,
                'shift_finish': SHIFT_START,
                'shift_start': SHIFT_FINISH,
                'can_choose_from_assigned_lines': 123,
            },
            'user_invalid_can_choose_except_assigned_lines': {
                'quality': 11.1,
                'languages': ['ru'],
                'csat': 66.6,
                'piece': True,
                'shift_finish': SHIFT_START,
                'shift_start': SHIFT_FINISH,
                'can_choose_except_assigned_lines': 123,
            },
            'user_with_different_assigned_lines_mode': {
                'quality': 11.1,
                'languages': ['ru', 'en'],
                'csat': 66.6,
                'piece': False,
                'shift_finish': SHIFT_START,
                'shift_start': SHIFT_FINISH,
                'in_additional_permitted': False,
                'off_shift_tickets_disabled': False,
                'assigned_lines': ['online_line', 'offline_line'],
                'can_choose_from_assigned_lines': True,
                'can_choose_except_assigned_lines': True,
            },
            'valid_user': {
                'quality': 11.1,
                'languages': ['ru', 'en'],
                'csat': 66.6,
                'piece': False,
                'shift_finish': SHIFT_START,
                'shift_start': SHIFT_FINISH,
                'in_additional_permitted': False,
                'off_shift_tickets_disabled': False,
                'assigned_lines': ['line_1', 'line_2'],
                'can_choose_from_assigned_lines': True,
                'can_choose_except_assigned_lines': True,
            },
        },
    )

    with pytest.raises(update_supporters_by_compendium.ValidationError):
        await update_supporters_by_compendium.do_stuff(cbox_context, loop)

    async with cbox.app.pg_master_pool.acquire() as conn:
        records = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_profile '
            'ORDER BY supporter_login',
        )

    supporters = [dict(record) for record in records]
    assert supporters == [
        {
            'csat': 66.6,
            'languages': ['ru', 'en'],
            'shift_finish': datetime.datetime(
                2018, 8, 1, 12, 59, 23, 231000, tzinfo=datetime.timezone.utc,
            ),
            'shift_start': datetime.datetime(
                2018, 8, 1, 12, 59, 23, 231000, tzinfo=datetime.timezone.utc,
            ),
            'is_piecework': False,
            'quality': 11.1,
            'supporter_login': 'valid_user',
            'updated': utc_now,
            'max_tickets_per_shift': None,
            'in_additional_permitted': False,
            'off_shift_tickets_disabled': False,
            'max_chats': None,
            'assigned_lines': ['line_1', 'line_2'],
            'can_choose_from_assigned_lines': True,
            'can_choose_except_assigned_lines': True,
        },
    ]


@pytest.mark.parametrize(
    'expected_result',
    (
        pytest.param(
            {
                'supporter_login': 'user_in_additional',
                'in_additional': False,
                'status': 'offline',
            },
            marks=pytest.mark.config(
                CHATTERBOX_COMPENDIUM_SWITCH_SUPPORTERS_OFFLINE=True,
            ),
        ),
        pytest.param(
            {
                'supporter_login': 'user_in_additional',
                'in_additional': True,
                'status': 'online',
            },
            marks=pytest.mark.config(
                CHATTERBOX_COMPENDIUM_SWITCH_SUPPORTERS_OFFLINE=False,
            ),
        ),
    ),
)
async def test_in_additional_to_offline(
        patch_compendium_get_info: Callable,
        cbox_context: run.StuffContext,
        cbox: conftest.CboxWrap,
        loop: asyncio.AbstractEventLoop,
        expected_result: dict,
):
    patch_compendium_get_info(
        response={'user_in_additional': {'in_additional_permitted': False}},
    )

    await update_supporters_by_compendium.do_stuff(cbox_context, loop)

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch(
            'SELECT supporter_login, in_additional, status '
            'FROM chatterbox.online_supporters '
            'WHERE supporter_login = \'user_in_additional\'',
        )

    assert dict(result[0]) == expected_result


async def test_remove_old_records(
        patch_compendium_get_info: Callable,
        cbox_context: run.StuffContext,
        cbox: conftest.CboxWrap,
        loop: asyncio.AbstractEventLoop,
):
    patch_compendium_get_info(response={})

    await update_supporters_by_compendium.do_stuff(cbox_context, loop)

    async with cbox.app.pg_master_pool.acquire() as conn:
        result = await conn.fetch('SELECT * FROM chatterbox.supporter_profile')

    assert not result
