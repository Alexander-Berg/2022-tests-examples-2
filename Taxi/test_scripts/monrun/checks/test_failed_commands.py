# pylint: disable=protected-access
import datetime

import pytest

from scripts.monrun.checks import failed_commands

NOW = datetime.datetime(2020, 2, 5, 16, 12)


@pytest.mark.now((NOW + datetime.timedelta(minutes=10)).isoformat())
async def test_check_ok(scripts_tasks_app):
    result = await failed_commands._check(scripts_tasks_app, None)
    assert result == '0; OK'


@pytest.mark.now(NOW.isoformat())
async def test_check_warn(scripts_tasks_app):
    result = await failed_commands._check(scripts_tasks_app, None)
    assert result == '1; WARN: 2 commands failed in last 15 minutes'
