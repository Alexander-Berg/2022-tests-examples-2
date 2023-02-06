import socket

import pytest

from taxi.logs import auto_log_extra

from supportai import models as db_models

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai', files=['heartbeat.sql']),
]


@pytest.mark.skip
async def test_heartbeat(web_context):
    log_extra = auto_log_extra.get_log_extra()
    async with web_context.pg.master_pool.acquire(log_extra=log_extra) as conn:
        heartbeats = await db_models.Heartbeat.select_all(web_context, conn)

    assert len(heartbeats) == 1
    assert heartbeats[0].host == socket.gethostname()
