import pytest

from clownductor.generated.cron import run_cron


@pytest.mark.parametrize(
    ['cond_hosts', 'delete_count', 'add_count'],
    [
        ([], 0, 2),
        (['host1'], 1, 1),
        (['host1', 'host2'], 2, 0),
        (['host1', 'host2', 'host3'], 4, 0),
        (['host1', 'host3'], 3, 1),
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_SYNC_TO_CONDUCTOR=[
        {
            'clownductor_project': 'blah',
            'conductor': {
                'unstable': 'group_unstable',
                'testing': 'group_testing',
                'prestable': 'group_prestable',
                'stable': 'group_stable',
            },
        },
        {
            'clownductor_project': '__default__',
            'conductor': {
                'unstable': 'default_unstable',
                'testing': 'default_testing',
                'prestable': 'default_prestable',
                'stable': 'default_stable',
            },
        },
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_sync_to_conductor(patch, cond_hosts, delete_count, add_count):
    @patch(
        'clownductor.generated.service.'
        'conductor_api.plugin.ConductorClient.get_hosts',
    )
    async def _get_cond_hosts(*_args):
        return [{'name': host} for host in cond_hosts]

    @patch(
        'clownductor.generated.service.'
        'conductor_api.plugin.ConductorClient.add_host',
    )
    async def _add_host(*_args):
        return

    @patch(
        'clownductor.generated.service.'
        'conductor_api.plugin.ConductorClient.delete_host',
    )
    async def _delete_host(*_args):
        return

    @patch(
        'clownductor.generated.service.'
        'conductor_api.plugin.ConductorClient.add_group',
    )
    async def _add_group(*_args):
        return

    @patch(
        'clownductor.generated.service.'
        'conductor_api.plugin.ConductorClient.add_parent_groups',
    )
    async def _add_parent_groups(*_args):
        return

    @patch(
        'clownductor.generated.service.'
        'conductor_api.plugin.ConductorClient.get_group',
    )
    async def _get_group(*_args):
        return {'id': 1}

    await run_cron.main(['clownductor.crontasks.sync_to_conductor', '-t', '0'])

    assert len(_add_host.calls) == add_count
    assert len(_delete_host.calls) == delete_count
