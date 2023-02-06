import datetime

import pytest

from taxi import event_monitor


@pytest.mark.now('2018-10-19T12:08:12')
@pytest.mark.mongodb_collections('event_stats', 'event_monitor')
async def test_event_monitor(db):
    stats = {'some_stat': 1, 'another_stat': 2}
    await event_monitor.driver_ivr_session_stats(db, **stats)
    await event_monitor.driver_ivr_session_stats(db, some_stat=3)

    result = await db.event_stats.find({}, {'_id': False}).to_list(None)
    assert result == [
        {
            'name': 'driver_ivr_session_stats',
            'some_stat': 4,
            'another_stat': 2,
            'created': datetime.datetime(2018, 10, 19, 12, 8),
        },
    ]
