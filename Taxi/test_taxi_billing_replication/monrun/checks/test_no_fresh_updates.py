# pylint: disable=protected-access
import datetime
import re

import pytest

from taxi_billing_replication.monrun.checks import no_fresh_updates


WARN_THRESHOLD = 5
CRIT_THRESHOLD = 15


CHECKED_QUEUE_TABLES = ['parks.contracts_queue', 'parks.persons_queue']
BILLING_REPLICATION_CHECK_THRESHOLDS = {
    'no_fresh_updates': {
        'warn': 5,
        'crit': 15,
        'tables': CHECKED_QUEUE_TABLES,
    },
}


class ARGS:
    pass


@pytest.mark.config(
    BILLING_REPLICATION_CHECK_THRESHOLDS=BILLING_REPLICATION_CHECK_THRESHOLDS,
)
@pytest.mark.now(datetime.datetime(2017, 1, 1, 9, 0, 0).isoformat())
async def test_ok(billing_replictaion_cron_app):
    result = await no_fresh_updates._check(billing_replictaion_cron_app, ARGS)

    expected_message = (
        f'0; OK: all queues were updated in the last {WARN_THRESHOLD} minutes'
    )
    assert result == expected_message


@pytest.mark.config(
    BILLING_REPLICATION_CHECK_THRESHOLDS=BILLING_REPLICATION_CHECK_THRESHOLDS,
)
@pytest.mark.now(datetime.datetime(2017, 1, 1, 9, 7, 20).isoformat())
async def test_warn(billing_replictaion_cron_app):
    result = await no_fresh_updates._check(billing_replictaion_cron_app, ARGS)
    expected_regex = (
        # noqa: W605
        # pylint: disable=W1401
        f'1; WARN: no updates for queues \(([\w_\.,]+)\) '
        f'in the last {WARN_THRESHOLD} minutes'
    )

    match = re.match(expected_regex, result)
    assert match is not None

    warn_tables = match.group(1).split(',')
    assert set(warn_tables) == set(CHECKED_QUEUE_TABLES)


@pytest.mark.config(
    BILLING_REPLICATION_CHECK_THRESHOLDS=BILLING_REPLICATION_CHECK_THRESHOLDS,
)
@pytest.mark.now(datetime.datetime(2017, 1, 1, 9, 14, 10).isoformat())
async def test_crit(billing_replictaion_cron_app):
    result = await no_fresh_updates._check(billing_replictaion_cron_app, ARGS)
    msg = (
        f'2; CRIT: no updates for queues (parks.persons_queue) in the last '
        f'{CRIT_THRESHOLD} minutes'
    )
    assert result == msg
