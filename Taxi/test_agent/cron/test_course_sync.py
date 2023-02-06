import datetime

import pytest

from agent.generated.cron import cron_context as context
from agent.generated.cron import run_cron


@pytest.mark.config(
    AGENT_MOE_COURSES=[
        {
            'deadline': '2023-01-01',
            'enable': True,
            'id': 1474,
            'required': True,
            'success_score': 80,
        },
    ],
    AGENT_MOE_CHUNK_READ=3,
)
async def test_import_completed_courses(
        cron_context: context.Context, mock_moe_students_results,
):
    await run_cron.main(['agent.crontasks.import_moe_results', '-t', '0'])

    query = 'SELECT * FROM agent.courses_results'
    async with cron_context.pg.slave_pool.acquire() as conn:
        rows = await conn.fetch(query)
        assert len(rows) == 2
        rows = [
            {
                'course_id': row['course_id'],
                'login': row['login'],
                'completed_at=': row['completed_at'],
                'source': row['source'],
                'result': row['result'],
            }
            for row in rows
        ]

        assert rows == [
            {
                'course_id': 1474,
                'login': 'agent_1',
                'completed_at=': datetime.datetime(2021, 1, 1, 0, 0),
                'source': 'moe',
                'result': 100.0,
            },
            {
                'course_id': 1474,
                'login': 'agent_4',
                'completed_at=': datetime.datetime(2021, 1, 1, 0, 0),
                'source': 'moe',
                'result': 80.0,
            },
        ]
