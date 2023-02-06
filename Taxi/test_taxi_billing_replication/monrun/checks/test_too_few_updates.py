# pylint: disable=protected-access
import datetime
import re

import pytest

from taxi_billing_replication.monrun.checks import too_few_updates


CHECK_THRESHOLDS_CONFIG_KEY = 'BILLING_REPLICATION_CHECK_THRESHOLDS'
CHECKED_TABLES = ('parks.persons', 'parks.contract_versions')


class ARGS:
    pass


@pytest.mark.config(
    BILLING_REPLICATION_CHECK_THRESHOLDS={
        'too_few_updates': [
            {'table': 'parks.persons', 'warn': 0, 'crit': 0},
            {'table': 'parks.contract_versions', 'warn': 0, 'crit': 0},
        ],
    },
)
@pytest.mark.now(datetime.datetime(2017, 1, 1, 11, 0, 0).isoformat())
async def test_ok(billing_replictaion_cron_app):
    result = await too_few_updates._check(billing_replictaion_cron_app, ARGS)

    expected_regex = (
        # noqa: W605
        # pylint: disable=W1401
        f'0; OK: enough updates in tables ([\w_\.,]+) '
        f'in the last {too_few_updates.CHECK_PERIOD}'
    )

    match = re.match(expected_regex, result)
    assert match is not None

    checked_tables = match.group(1).split(',')
    assert set(checked_tables) == set(CHECKED_TABLES)


@pytest.mark.config(
    BILLING_REPLICATION_CHECK_THRESHOLDS={
        'too_few_updates': [
            {'table': 'parks.persons', 'warn': 10, 'crit': 5},
            {'table': 'parks.contract_versions', 'warn': 5, 'crit': 1},
        ],
    },
)
@pytest.mark.now(datetime.datetime(2017, 1, 1, 11, 0, 0).isoformat())
async def test_warn(billing_replictaion_cron_app):
    result = await too_few_updates._check(billing_replictaion_cron_app, ARGS)

    expected_regex = (
        f'1; WARN: too few updates for one of the tables: '
        # noqa: W605
        # pylint: disable=W1401
        f'([\w_\.,]+) in the last {too_few_updates.CHECK_PERIOD}'
    )
    match = re.match(expected_regex, result)
    assert match is not None

    warn_tables = match.group(1).split(',')
    assert set(warn_tables) == set(CHECKED_TABLES)


@pytest.mark.config(
    BILLING_REPLICATION_CHECK_THRESHOLDS={
        'too_few_updates': [
            {'table': 'parks.persons', 'warn': 10, 'crit': 5},
            {'table': 'parks.contract_versions', 'warn': 5, 'crit': 3},
        ],
    },
)
@pytest.mark.now(datetime.datetime(2017, 1, 1, 11, 0, 0).isoformat())
async def test_crit(billing_replictaion_cron_app):
    result = await too_few_updates._check(billing_replictaion_cron_app, ARGS)

    expected_message = (
        f'2; CRIT: critically few updates for one of the tables: '
        f'parks.contract_versions in the last {too_few_updates.CHECK_PERIOD}'
    )
    assert result == expected_message
