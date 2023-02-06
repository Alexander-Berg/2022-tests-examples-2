import datetime

import pytest

from chatterbox.crontasks import import_yandex_calendar_table


NOW = datetime.datetime(2015, 1, 6)


async def get_yandex_calendar(cbox):
    query = 'SELECT * FROM chatterbox.yandex_calendar'
    async with cbox.app.pg_slave_pool.acquire() as conn:
        return await conn.fetch(query)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    EATS_RESTAPP_SUPPORT_CHAT_CALENDAR_CACHE_SETTINGS={
        'days_count_from': 7,
        'days_count_to': 7,
    },
)
async def test_import_yandex_calendar(
        cbox, cbox_context, loop, mock_yandex_calendar,
):
    await import_yandex_calendar_table.do_stuff(cbox_context, loop)
    calendar = await get_yandex_calendar(cbox)
    assert len(calendar) == 3
