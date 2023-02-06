# pylint: disable=protected-access
import re

import pytest

from taxi_billing_replication.monrun.checks import cycle_too_long


class ARGS:
    pass


async def test_ok(billing_replictaion_cron_app):
    result = await cycle_too_long._check(billing_replictaion_cron_app, ARGS)
    assert result == '0; OK: all last cycles are within bounds'


@pytest.mark.pgsql(
    'billing_replication', files=('pg_billing_replication.sql', 'warn.sql'),
)
async def test_warn(billing_replictaion_cron_app):
    result = await cycle_too_long._check(billing_replictaion_cron_app, ARGS)
    expected_regex = r'1; WARN: last cycle too long for tables: ([\w_\.,]+)'

    match = re.match(expected_regex, result)
    assert match is not None

    warn_tables = match.group(1).split(',')
    assert set(warn_tables) == {'parks.contracts_queue', 'parks.persons_queue'}


@pytest.mark.pgsql(
    'billing_replication', files=('pg_billing_replication.sql', 'crit.sql'),
)
async def test_crit(billing_replictaion_cron_app):
    result = await cycle_too_long._check(billing_replictaion_cron_app, ARGS)
    msg = '2; CRIT: last cycle too long for tables: parks.persons_queue'
    assert result == msg
