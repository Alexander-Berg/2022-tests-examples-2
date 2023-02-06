# pylint: disable=redefined-outer-name,unused-variable

import datetime as dt

import pytest

from selfemployed.db import dbmain


@pytest.mark.pgsql(
    'selfemployed_main',
    queries=[
        """
        INSERT INTO profiles
            (id, inn, park_id, driver_id, status, step, created_at,
            modified_at)
        VALUES
            ('smz1', 'unbound_1', 'p1', 'd1', 'confirmed', 'finish',
            '2019-07-18 11:00:00', '2019-07-18 11:00:00'),
            ('smz2', 'unbound_2', 'p2', 'd2', 'confirmed', 'finish',
            '2019-07-18 10:00:00', '2019-07-18 10:00:00'),
            ('smz3', 'unbound_3', 'p3', 'd3', 'confirmed', 'finish',
            '2019-07-18 10:00:00', '2019-07-18 10:00:00')
        """,
    ],
)
async def test_get_recent_drivers(se_web_context):
    from_ts = dt.datetime(2019, 7, 18, 10, 30)
    from_ts.replace(tzinfo=dt.timezone.utc)
    drivers = await dbmain.get_recent_drivers(se_web_context.pg, from_ts, 3, 0)
    assert len(drivers) == 1
    driver = drivers[0]
    assert driver['park_id'] == 'p1'
    assert driver['driver_id'] == 'd1'
    assert driver['step'] == 'finish'
    from_ts -= dt.timedelta(hours=1)
    drivers = await dbmain.get_recent_drivers(se_web_context.pg, from_ts, 5, 0)
    assert len(drivers) == 3
    drivers = await dbmain.get_recent_drivers(se_web_context.pg, from_ts, 3, 1)
    assert len(drivers) == 2
    drivers = await dbmain.get_recent_drivers(se_web_context.pg, from_ts, 1, 1)
    assert len(drivers) == 1
    drivers = await dbmain.get_recent_drivers(se_web_context.pg, from_ts, 3, 3)
    assert drivers == []
