import datetime

import pytest

from agent.generated.cron import cron_context as context
from agent.generated.cron import run_cron


NOW = datetime.datetime(2021, 11, 5)

AVAILABLE_LINES_EXPECTED_DATA = [
    {'login': 'login_1', 'lines': ['line_1']},
    {'login': 'login_2', 'lines': ['line_2', 'line_3']},
    {'login': 'login_3', 'lines': ['line_2']},
]
LINES_INFO_EXPECTED_DATA = [
    {
        'line': 'line_1',
        'line_tanker_key': 'line_1_tanker_key',
        'mode': 'online',
        'open_chats': 0,
    },
    {
        'line': 'line_2',
        'line_tanker_key': 'line_2_tanker_key',
        'mode': 'offline',
        'open_chats': 12,
    },
    {
        'line': 'line_3',
        'line_tanker_key': 'line_3_tanker_key',
        'mode': 'offline',
        'open_chats': 13,
    },
]


@pytest.mark.config(
    AGENT_PROJECT_SETTINGS={
        'default': {'enable_chatterbox': False},
        'calltaxi': {
            'enable_chatterbox': True,
            'main_permission': 'user_calltaxi',
        },
    },
)
async def test_import_available_lines(
        cron_context: context.Context,
        mock_chatterbox_available_lines,
        mock_chatterbox_lines_info,
):
    await run_cron.main(['agent.crontasks.import_available_lines', '-t', '0'])

    query = 'SELECT * FROM agent.chatterbox_available_lines'
    async with cron_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        db_data = [dict(row) for row in rows]

    assert db_data == AVAILABLE_LINES_EXPECTED_DATA

    query = 'SELECT * FROM agent.chatterbox_lines_info'
    async with cron_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        db_data = [dict(row) for row in rows]

    assert db_data == LINES_INFO_EXPECTED_DATA
