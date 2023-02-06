import datetime

import pytest
import pytz

from test_chatterbox import plugins as conftest


@pytest.mark.now('2019-02-01T12:12:12')
async def test_remove_profiles_before_datetime(cbox: conftest.CboxWrap):
    utc_now = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
    await cbox.app.supporters_manager.remove_profiles_before_datetime(
        updated=utc_now,
    )

    async with cbox.app.pg_master_pool.acquire() as conn:
        records = await conn.fetch(
            'SELECT supporter_login FROM chatterbox.supporter_profile',
        )

    supporters = set(record['supporter_login'] for record in records)
    assert supporters == {
        'user_with_utc_now_updated',
        'user_with_updated_in_future',
    }
