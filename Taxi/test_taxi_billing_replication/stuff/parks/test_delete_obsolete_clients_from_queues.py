import pytest

from taxi_billing_replication import config
from taxi_billing_replication import cron_run


@pytest.mark.now('2021-03-16T09:00:00.000000+00:00')
@pytest.mark.pgsql(
    'billing_replication',
    files=['test_delete_obsolete_clients_from_queues.sql'],
)
@pytest.mark.filldb(parks='test_delete_obsolete_clients_from_queues')
@pytest.mark.parametrize('delete_obsolete_clients_from_queues', [True, False])
async def test_delete_obsolete_clients_from_queues(
        patch,
        fixed_secdist,
        billing_replictaion_cron_app,
        monkeypatch,
        delete_obsolete_clients_from_queues,
):
    @patch('taxi.clients.solomon.SolomonClient.push_data')
    async def _push_data(data, handler=None, log_extra=None):
        pass

    monkeypatch.setattr(
        config.Config,
        'BILLING_REPLICATION_DELETE_OBSOLETE_CLIENTS_FROM_QUEUES',
        delete_obsolete_clients_from_queues,
    )
    module = 'taxi_billing_replication.stuff.parks.sync_client_ids'
    await cron_run.run_replication_task([module, '-t', '0'])
    pool = billing_replictaion_cron_app.pg_connection_pool
    async with pool.acquire() as conn:
        contracts_queue_rows = await conn.fetch(
            'SELECT (billing_kwargs).client_id '
            'FROM parks.contracts_queue '
            'ORDER BY (billing_kwargs).client_id;',
        )

        persons_queue_rows = await conn.fetch(
            'SELECT (billing_kwargs).client_id '
            'FROM parks.persons_queue '
            'ORDER BY (billing_kwargs).client_id;',
        )

        park_clients_rows = await conn.fetch(
            'SELECT id, park_id FROM parks.clients ',
        )

        # 789000 - current active bci
        assert (
            len(park_clients_rows) == 1
            and park_clients_rows[0]['park_id'] == '1'
            and park_clients_rows[0]['id'] == '789000'
        )
        if delete_obsolete_clients_from_queues:
            assert (
                len(contracts_queue_rows) == 2
                and contracts_queue_rows[0]['client_id'] == '789000'
                and contracts_queue_rows[1]['client_id'] == '789000'
            )
            assert (
                len(persons_queue_rows) == 1
                and persons_queue_rows[0]['client_id'] == '789000'
            )
        else:
            assert (
                len(contracts_queue_rows) == 4
                and contracts_queue_rows[0]['client_id'] == '123456'
                and contracts_queue_rows[1]['client_id'] == '123456'
                and contracts_queue_rows[2]['client_id'] == '789000'
                and contracts_queue_rows[3]['client_id'] == '789000'
            )
            assert (
                len(persons_queue_rows) == 2
                and persons_queue_rows[0]['client_id'] == '123456'
                and persons_queue_rows[1]['client_id'] == '789000'
            )
