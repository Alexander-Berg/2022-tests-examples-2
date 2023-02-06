# pylint: disable=protected-access,unused-variable
import datetime

import pytest

from taxi.util import dates

from scripts.monrun.checks import too_many_expired

NOW = datetime.datetime(2019, 5, 30, 14)


@pytest.mark.parametrize(
    'script_docs',
    [
        [],
        [{}],
        [
            {
                'reason': 'expired',
                'status': 'failed',
                'updated': datetime.datetime(2019, 5, 20, 00),
            },
            {
                'reason': 'expired',
                'status': 'failed',
                'updated': datetime.datetime(2019, 5, 30, 00),
            },
        ],
    ],
)
@pytest.mark.config(
    SCRIPTS_MONITORING_CONFIGS={
        'too_many_expired': {'newer_then_delay': 1, 'threshold': 2},
    },
)
@pytest.mark.now(NOW.isoformat())
async def test_check_ok(scripts_tasks_app, setup_scripts, script_docs):
    await setup_scripts(script_docs)

    result = await too_many_expired._check(scripts_tasks_app, None)
    assert result == '0; OK'


@pytest.mark.usefixtures('setup_many_scripts')
@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    SCRIPTS_MONITORING_CONFIGS={
        'too_many_expired': {'newer_then_delay': 5, 'threshold': 1},
    },
)
async def test_check_warn(scripts_tasks_app):
    result = await too_many_expired._check(scripts_tasks_app, None)
    msg = (
        '1; WARN: 1 scripts are expired and '
        f'newer then {dates.timestring(NOW-datetime.timedelta(days=5))}'
    )
    assert result == msg
