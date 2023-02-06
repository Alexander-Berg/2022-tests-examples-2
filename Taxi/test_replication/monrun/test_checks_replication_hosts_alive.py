import pytest

from replication.generated.cron import run_monrun
from replication.monrun.checks import replication_hosts_alive


_MODULE = 'replication.monrun.checks.replication_hosts_alive'


@pytest.mark.parametrize('unit_type', ('web', 'cron'))
async def test_check_replication_hosts_alive(replication_app, unit_type):
    res = await run_monrun.run([_MODULE, '--unit', unit_type])
    assert res == f'0; Ok, host is active'


@pytest.mark.parametrize('unit_type', ('web', 'cron'))
async def test_check_hosts_alive_with_block_crontasks(
        monkeypatch, replication_app, unit_type,
):
    monkeypatch.setattr(
        replication_hosts_alive, '_is_crontasks_disable', lambda: True,
    )
    res = await run_monrun.run([_MODULE, '--unit', unit_type])
    assert res == f'0; Ok, host has "yandex-taxi-import-blocker" file'
