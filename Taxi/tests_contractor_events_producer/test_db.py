import datetime as dt

import pytest

from tests_contractor_events_producer import db_tools
from tests_contractor_events_producer import online_events


@pytest.mark.now('2021-11-14T23:59:59+00:00')
async def test_online_status_change_produce_events(
        taxi_contractor_events_producer, pgsql, testpoint,
):
    assert not db_tools.get_online_events_in_outbox(pgsql)

    cursor = pgsql['contractor_events_producer'].cursor()

    event = online_events.OnlineDbEvent(
        'dbid1',
        'uuid1',
        online_events.OFFLINE_STATUS,
        dt.datetime.fromisoformat('2021-11-14T22:59:59+00:00'),
    )

    cursor.execute(db_tools.insert_online_events([event]))

    online_events_in_outbox = db_tools.get_online_events_in_outbox(pgsql)
    assert online_events_in_outbox == [event]

    cursor.execute(db_tools.insert_online_events([event]))

    online_events_in_outbox = db_tools.get_online_events_in_outbox(pgsql)
    assert online_events_in_outbox == [event, event]
