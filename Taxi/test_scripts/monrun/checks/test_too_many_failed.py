# pylint: disable=protected-access,unused-variable
import datetime

import pytest

from taxi.util import dates

from scripts.monrun.checks import too_many_failed

NOW = datetime.datetime(2019, 5, 30, 14)


@pytest.mark.parametrize(
    'script_docs',
    [
        [],
        [{}],
        [
            {
                'status': 'failed',
                'updated': datetime.datetime(2019, 5, 30, 13, 59),
            },
            {
                'status': 'failed',
                'updated': datetime.datetime(2019, 5, 30, 13, 50),
            },
        ],
    ],
)
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    SCRIPTS_MONITORING_CONFIGS={
        'too_many_failed': {'newer_then_delay': 5, 'threshold': 2},
    },
)
async def test_check_ok(scripts_tasks_app, setup_scripts, script_docs):
    await setup_scripts(script_docs)

    result = await too_many_failed._check(scripts_tasks_app, None)
    assert result == '0; OK'


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    SCRIPTS_MONITORING_CONFIGS={
        'too_many_failed': {'newer_then_delay': 5, 'threshold': 1},
    },
)
async def test_check_warn(scripts_tasks_app):
    result = await too_many_failed._check(scripts_tasks_app, None)
    msg = (
        '1; WARN: 1 scripts are failed and '
        f'newer then {dates.timestring(NOW-datetime.timedelta(minutes=5))}'
    )
    assert result == msg
