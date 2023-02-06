import asyncio
import datetime

import pytest

from taxi.maintenance import run
from taxi.util import dates

from rida.crontasks import send_sms_statistics


@pytest.mark.now('2021-08-17T13:30:00.0')
async def test_php_status_metrics(
        cron_context, mockserver, get_stats_by_label_values,
):
    stuff_context = run.StuffContext(
        lock=None,
        task_id='some-id',
        start_time=dates.utcnow(),
        data=cron_context,
    )

    loop = asyncio.get_event_loop()
    await send_sms_statistics.do_stuff(stuff_context, loop)

    stats = get_stats_by_label_values(
        cron_context, {'sensor': 'sms.statistics'},
    )
    assert stats == [
        {
            'value': 1,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'sms.statistics',
                'status': 'FAILED_TO_FETCH_STATUS',
            },
        },
        {
            'value': 2,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'sms.statistics',
                'status': 'DELIVERED_TO_HANDSET',
            },
        },
        {
            'value': 3,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'sensor': 'sms.statistics',
                'status': 'REJECTED_FLOODING_FILTER',
            },
        },
    ]

    query = (
        'SELECT last_id, last_updated_at '
        'FROM cursors '
        'WHERE name = \'user_login_attempt_statistics\''
    )
    async with cron_context.pg.ro_pool.acquire() as conn:
        record = await conn.fetchrow(query)
        assert record['last_id'] == 0
        assert record['last_updated_at'] == datetime.datetime(
            2021, 8, 17, 13, 25, 14,
        )
