# pylint: disable=protected-access
import pytest

from taxi_billing_replication.monrun.checks import max_fail_count


class Args:
    def __init__(self, time_range):
        self.time_range = time_range


@pytest.mark.pgsql('billing_replication', files=['data.sql'])
async def test_ok(billing_replictaion_cron_app):
    args = Args(time_range=60)  # 1 minute
    result = await max_fail_count._check(billing_replictaion_cron_app, args)
    assert result == '0; No problems'


@pytest.mark.pgsql('billing_replication', files=['data.sql'])
async def test_warn(billing_replictaion_cron_app):
    args = Args(time_range=60 * 60 * 3)  # 3 hours
    result = await max_fail_count._check(billing_replictaion_cron_app, args)
    assert result == (
        '1; Problems detected: max failed count reached for billing kwargs '
        'billing_kwargs=<Record contract_id=1> fail_count=11, '
        'billing_kwargs=<Record contract_id=2> fail_count=10 '
        'of table parks.balances_queue; '
        'max failed count reached for billing kwargs '
        'billing_kwargs=<Record client_id=\'5\' '
        'contract_kind=\'SPENDABLE\'> fail_count=11 '
        'of table parks.contracts_queue'
    )
