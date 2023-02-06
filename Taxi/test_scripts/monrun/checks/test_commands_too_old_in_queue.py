# pylint: disable=protected-access,
import datetime

import pytest

from scripts.monrun.checks import commands_too_old_in_queue

NOW = datetime.datetime(2020, 2, 5, 16, 1)


@pytest.mark.now((NOW - datetime.timedelta(seconds=15)).isoformat())
async def test_check_ok(scripts_tasks_app):
    result = await commands_too_old_in_queue._check(scripts_tasks_app, None)
    assert result == '0; OK'


@pytest.mark.now(NOW.isoformat())
async def test_check_warn(scripts_tasks_app):
    result = await commands_too_old_in_queue._check(scripts_tasks_app, None)
    assert (
        result == '1; WARN: 2 not processed commands in queue for 15 seconds'
    )
