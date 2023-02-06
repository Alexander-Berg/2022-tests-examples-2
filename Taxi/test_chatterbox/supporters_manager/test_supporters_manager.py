import datetime

import pytest
import pytz

from test_chatterbox import plugins as conftest

SHIFT_START = datetime.datetime(
    2018, 8, 1, 12, 59, 23, 231000, tzinfo=datetime.timezone.utc,
)
SHIFT_FINISH = datetime.datetime(
    2018, 8, 1, 20, 59, 23, 231000, tzinfo=datetime.timezone.utc,
)


@pytest.mark.now('2019-01-01T00:00:00')
async def test_supporters_manager_save(cbox: conftest.CboxWrap):
    utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    record_number = await cbox.app.supporters_manager.save_supporters_profiles(
        supporters=[
            {
                'supporter_login': 'user_1',
                'quality': 11,
                'languages': ['ru', 'en'],
                'csat': 66.6,
                'is_piecework': False,
                'shift_finish': SHIFT_FINISH,
                'shift_start': SHIFT_START,
                'max_tickets_per_shift': 100,
                'in_additional_permitted': False,
                'off_shift_tickets_disabled': False,
                'max_chats_chatterbox': 5,
                'assigned_lines': ['line_1', 'line_2'],
                'can_choose_from_assigned_lines': True,
                'can_choose_except_assigned_lines': True,
            },
            {
                'supporter_login': 'old_user_1',
                'quality': 22,
                'languages': ['en'],
                'csat': 11.1,
                'is_piecework': True,
                'shift_finish': None,
                'shift_start': None,
                'max_tickets_per_shift': None,
                'in_additional_permitted': False,
                'off_shift_tickets_disabled': False,
                'max_chats_chatterbox': 5,
                'assigned_lines': ['line_1', 'line_2'],
                'can_choose_from_assigned_lines': True,
                'can_choose_except_assigned_lines': True,
            },
            {
                'supporter_login': 'user_2',
                'quality': 11,
                'languages': ['ru', 'en'],
                'csat': 66.6,
                'is_piecework': False,
                'shift_finish': SHIFT_FINISH,
                'shift_start': SHIFT_START,
                'max_tickets_per_shift': 100,
                'in_additional_permitted': False,
                'off_shift_tickets_disabled': False,
                'max_chats_chatterbox': 5,
                'assigned_lines': [],
                'can_choose_from_assigned_lines': False,
                'can_choose_except_assigned_lines': True,
            },
        ],
        updated=utc_now,
    )
    assert record_number == 3

    async with cbox.app.pg_master_pool.acquire() as conn:
        records = await conn.fetch(
            'SELECT * FROM chatterbox.supporter_profile '
            'ORDER BY supporter_login',
        )

    supporters = [dict(record) for record in records]
    assert supporters == [
        {
            'csat': 11.1,
            'languages': ['en'],
            'is_piecework': True,
            'quality': 22,
            'supporter_login': 'old_user_1',
            'updated': utc_now,
            'shift_finish': None,
            'shift_start': None,
            'max_tickets_per_shift': None,
            'in_additional_permitted': False,
            'off_shift_tickets_disabled': False,
            'max_chats': 5,
            'assigned_lines': ['line_1', 'line_2'],
            'can_choose_from_assigned_lines': True,
            'can_choose_except_assigned_lines': True,
        },
        {
            'csat': 0.0,
            'languages': [],
            'is_piecework': False,
            'quality': 0,
            'supporter_login': 'old_user_2',
            'updated': utc_now.replace(year=2018),
            'shift_finish': None,
            'shift_start': None,
            'max_tickets_per_shift': None,
            'in_additional_permitted': True,
            'off_shift_tickets_disabled': True,
            'max_chats': None,
            'assigned_lines': [],
            'can_choose_from_assigned_lines': False,
            'can_choose_except_assigned_lines': True,
        },
        {
            'csat': 66.6,
            'languages': ['ru', 'en'],
            'is_piecework': False,
            'quality': 11,
            'supporter_login': 'user_1',
            'updated': utc_now,
            'shift_finish': SHIFT_FINISH,
            'shift_start': SHIFT_START,
            'max_tickets_per_shift': 100,
            'in_additional_permitted': False,
            'off_shift_tickets_disabled': False,
            'max_chats': 5,
            'assigned_lines': ['line_1', 'line_2'],
            'can_choose_from_assigned_lines': True,
            'can_choose_except_assigned_lines': True,
        },
        {
            'csat': 66.6,
            'languages': ['ru', 'en'],
            'is_piecework': False,
            'quality': 11,
            'supporter_login': 'user_2',
            'updated': utc_now,
            'shift_finish': SHIFT_FINISH,
            'shift_start': SHIFT_START,
            'max_tickets_per_shift': 100,
            'in_additional_permitted': False,
            'off_shift_tickets_disabled': False,
            'max_chats': 5,
            'assigned_lines': [],
            'can_choose_from_assigned_lines': False,
            'can_choose_except_assigned_lines': True,
        },
    ]
